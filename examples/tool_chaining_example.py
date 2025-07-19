#!/usr/bin/env python3
"""
AgentSpring Self-Running Demo with Custom Prompt Template

This demo showcases the AgentSpring orchestration system with a custom prompt template
optimized for mathematical operations, text processing, and multi-step workflows.

SETUP:
1. Install Ollama: https://ollama.ai/
2. Run: ollama pull llama3.2
3. Start Ollama: ollama serve
4. Run this script: python -m examples.tool_chaining_example

The custom prompt template includes:
- Better mathematical operation examples
- Multi-step workflow patterns
- Domain-specific tool selection rules
- Improved variable passing between steps
"""

import os
import sys
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentspring.orchestration import execute_prompt, set_prompt_template

# Custom prompt template optimized for demo tasks
CUSTOM_PROMPT_TEMPLATE = """
You are an expert AI orchestrator specialized in mathematical computations, text processing, and multi-step workflows. 
Given the following user instruction, extract a list of steps, where each step has a tool_name and a parameters dictionary. 
Respond ONLY with a valid JSON object with keys: steps (list of steps), priority, and intent.

IMPORTANT: Only use tool names from this exact list: {tools_list}

User instruction: {prompt}

CRITICAL RULES AND EXAMPLES:

MATHEMATICAL OPERATIONS:
- For all mathematical operations (summing ranges, calculations, etc.), use calculate tool
- For summing ranges (e.g., "1 through 10", "1 to 10", "sum of 1-10"), use calculate with "1+2+3+4+5+6+7+8+9+10"
- For simple calculations (e.g., "2 + 3", "5 * 4"), use calculate tool  
- For random number generation, use generate_random tool
- For prime number checking, use is_prime tool

TEXT PROCESSING:
- For case conversion, use text_to_uppercase or text_to_lowercase
- For character counting, use count_characters
- For text reversal, use reverse_text
- For word counting, use count_words

MULTI-STEP WORKFLOWS:
- Always use {{result}} variables to pass data between steps
- For text chains: text_to_uppercase → count_characters
- For random operations: generate_random → calculate
- For mathematical chains: calculate → write_file

EXAMPLES:

1. "Calculate sum of 1 through 10":
   {{"steps": [{{"tool_name": "calculate", "parameters": {{"expression": "1+2+3+4+5+6+7+8+9+10"}}}}], "priority": "low", "intent": "sum_calculation"}}

2. "Convert Hello World to uppercase and count characters":
   {{"steps": [
     {{"tool_name": "text_to_uppercase", "parameters": {{"text": "Hello World"}}}},
     {{"tool_name": "count_characters", "parameters": {{"text": "{{uppercase_text}}"}}}}
   ], "priority": "medium", "intent": "text_processing"}}

3. "Generate random number between 1 and 100 and double it":
   {{"steps": [
     {{"tool_name": "generate_random", "parameters": {{"min_value": 1, "max_value": 100}}}},
     {{"tool_name": "calculate", "parameters": {{"expression": "{{random_number}} * 2"}}}}
   ], "priority": "medium", "intent": "random_calculation"}}

4. "Check if 42 is prime":
   {{"steps": [{{"tool_name": "is_prime", "parameters": {{"number": 42}}}}], "priority": "low", "intent": "prime_check"}}

Now respond for the user instruction above.
"""

def setup_demo():
    """Setup the demo environment"""
    print("🔧 Setting up demo environment...")
    
    # Create demo directory if it doesn't exist
    os.makedirs("demo_data", exist_ok=True)
    
    # Set the custom prompt template
    set_prompt_template(CUSTOM_PROMPT_TEMPLATE)
    print("✅ Custom prompt template set")
    print()

def log_step(step_result, step_index):
    """Log the result of a single step"""
    print(f"    Step {step_index + 1}:")
    print(f"      Tool: {step_result.tool_name if hasattr(step_result, 'tool_name') else 'unknown'}")
    print(f"      Success: {step_result.success}")
    print(f"      Time: {step_result.execution_time:.2f}s")
    
    if step_result.success and step_result.result:
        if isinstance(step_result.result, dict):
            for key, value in step_result.result.items():
                print(f"      {key}: {value}")
        else:
            print(f"      Result: {step_result.result}")
    elif not step_result.success:
        print(f"      Error: {step_result.error}")

def run_prompt(prompt):
    print(f"\nUser: {prompt}")
    
    # Demo-specific prompting: Add context about the expected workflow
    enhanced_prompt = prompt
    if "calculate" in prompt.lower() and "sum" in prompt.lower():
        enhanced_prompt = f"{prompt}\n\nNote: This requires calculating the sum of numbers using the calculate tool with a mathematical expression like '1+2+3+4+5+6+7+8+9+10'."
    elif "convert" in prompt.lower() and "uppercase" in prompt.lower() and "count" in prompt.lower():
        enhanced_prompt = f"{prompt}\n\nNote: This requires text processing to convert case and then counting characters. Use text_to_uppercase first, then count_characters with the result."
    elif "generate" in prompt.lower() and "random" in prompt.lower() and "double" in prompt.lower():
        enhanced_prompt = f"{prompt}\n\nNote: This requires generating a random number first, then doubling it. Use generate_random first, then calculate with the result."
    elif "check" in prompt.lower() and "prime" in prompt.lower():
        enhanced_prompt = f"{prompt}\n\nNote: This requires checking if a number is prime using the is_prime tool with the 'number' parameter."
    
    result = execute_prompt(enhanced_prompt)
    print(f"  Overall Success: {result.success}")
    print(f"  Execution Time: {result.execution_time:.2f}s")
    print(f"  Steps:")
    if not result.results:
        print("    (No steps executed)")
    for i, step_result in enumerate(result.results):
        log_step(step_result, i)
    print("  --- End of Prompt ---\n")

def write_fallback_files():
    """Write fallback files for demo purposes"""
    print("📝 Writing fallback files...")
    
    # Create some sample files for the demo
    files = {
        "demo_data/file1.txt": "This is the first sample file.\nIt has two lines.",
        "demo_data/file2.txt": "Second file here!\nWith more words in total.",
        "demo_data/notes.txt": "Notes: AgentSpring demo.\nTesting word count.",
        "demo_data/report.txt": "6"
    }
    
    for file_path, content in files.items():
        with open(file_path, 'w') as f:
            f.write(content)
    
    print("✅ Fallback files created")

def main():
    """Main demo function"""
    print("Welcome to the AgentSpring Self-Running Demo!")
    print("This demo uses a custom prompt template optimized for mathematical and text operations.")
    print()
    print("NOTE: Ollama must be running with the llama3.2 model for LLM-based prompt parsing.")
    print("See the top of this script for setup instructions.")
    print()
    
    # Setup demo environment
    setup_demo()
    write_fallback_files()
    
    # Example prompts that showcase different capabilities
    prompts = [
        "Calculate the sum of numbers 1 through 10 and store the result",
        "Convert the text 'Hello World' to uppercase and count its characters", 
        "Generate a random number between 1 and 100 and double it",
        "Check if the number 42 is prime and save the result"
    ]
    
    print("🚀 Starting demo with custom prompt template...")
    print("=" * 60)
    
    # Execute each prompt
    for prompt in prompts:
        run_prompt(prompt)
    
    print("Demo complete. All prompts processed as if entered by a user.")
    
    # Show final results
    print("\n📊 Final Results:")
    print("-" * 30)
    
    result_files = [
        "demo_data/sum_result.txt",
        "demo_data/text_result.txt", 
        "demo_data/random_result.txt",
        "demo_data/prime_result.txt"
    ]
    
    for file_path in result_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().strip()
                print(f"{file_path}: {content}")
        else:
            print(f"{file_path} was not created.")

if __name__ == "__main__":
    main() 