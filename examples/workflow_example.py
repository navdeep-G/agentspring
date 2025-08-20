"""
Agentic Workflow with Native Tool Chaining
------------------------------------------
This example demonstrates how to use AgentSpring's built-in workflow system
for dynamic tool chaining based on input analysis.
"""
import asyncio
import aiohttp
import json
import logging
import re
from typing import Dict, Any, List, Optional, Union, AsyncGenerator

from agentspring.agent import Agent
from agentspring.workflow import Workflow, NodeStatus
from agentspring.tools import tool, ToolRegistry, tool_registry
from agentspring.goals import Goal, GoalStatus
from agentspring.llm import LLMProvider, register_provider

# 1. Define a custom LLM provider for Ollama
class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.2:latest", base_url: str = "http://localhost:11434"):
        # Initialize with default config
        super().__init__(config={
            "timeout": 30,
            "max_retries": 3,
            "rate_limit": {
                "requests_per_minute": 60,
                "max_concurrent": 10,
                "retry_after": 60
            },
            "validate_input": False  # Disable input validation to avoid config issues
        })
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Generate a response using Ollama's API."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get('response', '')
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"
            
    async def stream_async(self, prompt: str, **kwargs) -> str:
        """Stream a response using Ollama's API."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                yield chunk['response']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"Error streaming response: {str(e)}")
            yield f"Error streaming response: {str(e)}"

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()

# Register the provider
register_provider("ollama")(OllamaProvider)

# Initialize the LLM
llm = OllamaProvider()  # or any other model you have installed

# 2. Define tools with proper decorators
@tool("analyze_sentiment", "Analyze the sentiment of a text")
async def analyze_sentiment(text: str) -> dict:
    """Simple sentiment analysis."""
    text = text.lower()
    positive_words = ["good", "great", "excellent", "happy", "awesome", "love"]
    negative_words = ["bad", "terrible", "awful", "sad", "horrible", "hate"]
    
    score = 0
    words = text.split()
    for word in words:
        if word in positive_words:
            score += 1
        elif word in negative_words:
            score -= 1
    
    sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {
        "sentiment": sentiment,
        "score": score / max(len(words), 1),  # Normalize score
        "analysis": f"The text has a {sentiment} sentiment with a score of {score}"
    }

@tool("summarize_text", "Generate a summary of the text")
async def summarize_text(text: str, max_sentences: int = 2) -> dict:
    """Generate a summary of the text."""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    summary = '. '.join(sentences[:max_sentences]) + '.'
    return {
        "summary": summary,
        "sentence_count": len(sentences[:max_sentences])
    }

@tool("extract_keywords", "Extract keywords from the text")
async def extract_keywords(text: str, top_n: int = 5) -> dict:
    """Extract top keywords from the text."""
    # Simple keyword extraction by word frequency
    from collections import Counter
    import string
    
    # Remove punctuation and convert to lowercase
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove stopwords (very basic list for example)
    stopwords = set(["the", "and", "is", "in", "it", "to", "of", "for"])
    words = [word for word in text.split() if word not in stopwords and len(word) > 2]
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Get top N keywords
    keywords = [word for word, _ in word_counts.most_common(top_n)]
    
    return {
        "keywords": keywords,
        "total_keywords": len(word_counts)
    }

class AnalysisAgent(Agent):
    """Agent that analyzes text and determines which tools to use."""
    
    def __init__(self, name: str = "AnalysisAgent"):
        super().__init__(name=name, description="Analyzes text and determines which tools to use")
        self.available_tools = ["analyze_sentiment", "summarize_text", "extract_keywords"]
        self.llm = llm  # Use the registered LLM
    
    async def process(self, goal: Union[Goal, dict]) -> Dict[str, Any]:
        """Process the goal and let the LLM handle tool orchestration."""
        # Handle both Goal object and dictionary
        if isinstance(goal, dict):
            text = goal.get('description', '')
        else:
            text = getattr(goal, 'description', '')
            
        if not text:
            return {"status": "error", "message": "No input text provided"}
        
        # Create a prompt that includes tool descriptions and lets the LLM decide what to do
        prompt = f"""You are an AI assistant that can analyze text using various tools. 
Here are the available tools:

1. analyze_sentiment: For understanding emotions and opinions in text
   - Input: {{"text": "text to analyze"}}
   
2. summarize_text: For condensing longer texts into shorter summaries
   - Input: {{"text": "text to summarize", "max_sentences": 2}}
   
3. extract_keywords: For identifying key topics in text
   - Input: {{"text": "text to analyze", "top_n": 5}}

Here's the text to analyze:
{text}

Your task is to analyze this text and decide which tools to use and in what order.
You can use one tool, multiple tools, or none at all, depending on what makes sense.

Return your response as a JSON object with the following structure:
{{
    "steps": [
        {{
            "tool": "tool_name",
            "parameters": {{...}},
            "reasoning": "Why this tool is being used"
        }}
    ]
}}
"""
        
        try:
            print(f"[DEBUG] Sending prompt to LLM...")
            print(f"[DEBUG] Prompt: {prompt}")
            
            # Get the LLM's plan
            response = await self.llm.generate_async(prompt)
            print(f"[DEBUG] Received response from LLM: {response}")
            
            # Extract and parse the JSON response
            try:
                # Look for JSON in markdown code blocks first
                json_match = re.search(r'```(?:json\n)?([\s\S]*?)\n```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    # If no code block, look for a raw JSON object
                    json_match = re.search(r'\{[\s\S]*\}', response)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        raise ValueError("No valid JSON found in response")
                
                plan = json.loads(json_str)
                
                if not isinstance(plan, dict) or 'steps' not in plan:
                    raise ValueError("Invalid response format: missing 'steps' field")
                
                results = []
                for step in plan.get('steps', []):
                    if not all(k in step for k in ['tool', 'parameters', 'reasoning']):
                        print(f"[WARNING] Skipping invalid step: {step}")
                        continue
                        
                    tool_name = step['tool']
                    if tool_name not in tool_registry.list_tools():
                        print(f"[WARNING] Unknown tool: {tool_name}")
                        continue
                        
                    print(f"[INFO] Using {tool_name}: {step['reasoning']}")
                    
                    try:
                        # Get the tool function from the registry
                        tool_func = tool_registry.get_tool(tool_name)
                        if not tool_func:
                            raise ValueError(f"Tool '{tool_name}' not found in registry")
                        
                        # Ensure parameters include the text if not provided
                        params = step.get('parameters', {})
                        if 'text' not in params:
                            params['text'] = text
                            
                        print(f"[DEBUG] Calling {tool_name} with params: {params}")
                        
                        # Execute the tool
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(**params)
                        else:
                            result = tool_func(**params)
                            
                        print(f"[DEBUG] {tool_name} returned: {result}")
                        
                        # Ensure the result is a dictionary
                        if not isinstance(result, dict):
                            result = {"result": result}
                        
                        tool_result = {
                            'tool': tool_name,
                            'result': result,
                            'success': True,
                            'reasoning': step['reasoning']
                        }
                        print(f"[DEBUG] Adding result: {tool_result}")
                        results.append(tool_result)
                        
                    except Exception as e:
                        error_msg = str(e)
                        print(f"[ERROR] Error executing {tool_name}: {error_msg}")
                        results.append({
                            'tool': tool_name,
                            'error': error_msg,
                            'success': False,
                            'reasoning': step['reasoning']
                        })
                
                print(f"[DEBUG] Final results: {results}")
                if not results:
                    return {
                        'status': 'completed',
                        'message': 'No tools were executed',
                        'results': []
                    }
                
                return {
                    'status': 'completed',
                    'steps': plan['steps'],
                    'results': results
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                error_msg = f"[ERROR] Failed to parse LLM response: {str(e)}\nResponse: {response}"
                print(error_msg)
                return {
                    'status': 'error',
                    'message': f"Error parsing LLM response: {str(e)}",
                    'results': []
                }
                
        except Exception as e:
            error_msg = f"[ERROR] Error in LLM processing: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f"Error in processing: {str(e)}",
                'results': []
            }

async def create_workflow(input_text: str) -> Workflow:
    """Create a dynamic workflow based on input text."""
    # Initialize workflow with tools
    workflow = Workflow(
        workflow_id="dynamic_analysis",
        name="Dynamic Text Analysis Workflow",
        tools=tool_registry  # Use the global tool registry
    )
    
    # Register the analysis agent
    analysis_agent = AnalysisAgent()
    workflow.agents["analysis_agent"] = analysis_agent
    
    # Add a single agent node that will handle all tool orchestration via LLM
    workflow.add_agent_node(
        node_id="analysis_node",
        agent_id="analysis_agent",
        goal=Goal(description=input_text)  # Pass the input text directly as the goal
    )
    
    return workflow

async def main():
    """Run the dynamic analysis workflow."""
    print("Welcome to the Text Analysis Workflow!")
    print("I can analyze text for sentiment, generate summaries, and extract keywords.")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("What would you like me to analyze? ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        if not user_input:
            print("Please provide some text to analyze.")
            continue
            
        print("\nStarting analysis...")
        
        try:
            # Create and execute the workflow
            workflow = await create_workflow(user_input)
            result = await workflow.execute()
            
            # Display results
            print("\nAnalysis complete!")
            print("-" * 50)
            
            # Get the results from the agent's response
            agent_node = workflow.nodes.get("analysis_node")
            if agent_node and agent_node.status == NodeStatus.COMPLETED:
                results = agent_node.result.get('results', [])
                
                for tool_result in results:
                    if not tool_result.get('success', False):
                        print(f"\nError in {tool_result.get('tool', 'unknown')}:")
                        print(f"Error: {tool_result.get('error', 'Unknown error')}")
                        continue
                        
                    tool_name = tool_result.get('tool', 'unknown')
                    result_data = tool_result.get('result', {})
                    
                    print(f"\n{tool_name.replace('_', ' ').title()} Results:")
                    print("-" * 30)
                    
                    if tool_name == "analyze_sentiment":
                        print(f"Sentiment: {result_data.get('sentiment', 'N/A')}")
                        print(f"Score: {result_data.get('score', 'N/A')}")
                        print(f"Analysis: {result_data.get('analysis', 'N/A')}")
                        
                    elif tool_name == "summarize_text":
                        print(f"Summary: {result_data.get('summary', 'N/A')}")
                        print(f"Sentences: {result_data.get('sentence_count', 0)}")
                        
                    elif tool_name == "extract_keywords":
                        keywords = result_data.get('keywords', [])
                        print(f"Keywords: {', '.join(keywords) if keywords else 'None'}")
                        print(f"Total unique keywords: {result_data.get('total_keywords', 0)}")
                    
                    print(f"\nReasoning: {tool_result.get('reasoning', 'No reasoning provided')}")
            else:
                print("\nNo results available or analysis failed.")
                if agent_node and agent_node.result:
                    print(f"Error: {agent_node.result.get('message', 'Unknown error')}")
            
            print("\n" + "=" * 50 + "\n")
            
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            print("\n" + "=" * 50 + "\n")

# Add cleanup for the LLM
import atexit

def cleanup():
    """Clean up resources."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(llm.close())

atexit.register(cleanup)

if __name__ == "__main__":
    # Make sure all tools are registered
    print("Available tools:", tool_registry.list_tools())
    asyncio.run(main())
