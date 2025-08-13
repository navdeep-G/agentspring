"""
Orchestration System for AgentSpring
Handles dynamic user prompts and translates them into tool execution chains
"""
import logging
import re
import json
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from pydantic import BaseModel, Field

from .tools import tool_registry, ToolExecutionResult
from .llm.registry import LLMRegistry, get_provider

logger = logging.getLogger(__name__)

class ToolStep(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    description: str = Field("", description="Human-readable description of this step")
    depends_on: Optional[str] = Field(None, description="Step this depends on (for future parallel execution)")
    condition: Optional[str] = Field(None, description="Condition for executing this step")

class ToolChain(BaseModel):
    steps: List[ToolStep] = Field(..., description="List of tool steps to execute")
    context: Dict[str, Any] = Field(default_factory=dict, description="Shared context between steps")
    description: str = Field("", description="Human-readable description of the chain")

class ChainExecutionResult(BaseModel):
    success: bool = Field(..., description="Whether the entire chain succeeded")
    results: List[ToolExecutionResult] = Field(..., description="Results from each step")
    context: Dict[str, Any] = Field(default_factory=dict, description="Final context after execution")
    execution_time: float = Field(..., description="Total execution time")
    timestamp: datetime = Field(default_factory=datetime.now)

class PromptParser:
    def __init__(self, llm_provider=None, prompt_template: Optional[str] = None):
        try:
            self.llm = llm_provider or get_provider()
        except ValueError as e:
            if "No default LLM provider" in str(e):
                raise RuntimeError(
                    "No LLM provider specified and no default provider is set. "
                    "Please either pass an LLM provider instance or register a default provider."
                ) from e
            raise
            
        self.available_tools = tool_registry.get_all_schemas()
        # Allow custom prompt template or use default
        self.prompt_template = prompt_template or self._get_default_prompt_template()

    def _get_default_prompt_template(self) -> str:
        """Get the default prompt template"""
        return (
            "You are an agentic API orchestrator. Given the following user instruction, "
            "extract a list of steps, where each step has a tool_name and a parameters dictionary. "
            "Respond ONLY with a valid JSON object with keys: steps (list of steps), priority, and intent.\n"
            "IMPORTANT: Only use tool names from this exact list: {tools_list}\n"
            "User instruction: {prompt}\n"
            "Example 1 - Single step operation:\n"
            "  Instruction: List files in a directory\n"
            "  Response: {{\n"
            "    \"steps\": [{{\"tool_name\": \"list_files\", \"parameters\": {{\"directory\": \"path/to/dir\"}}}}],\n"
            "    \"priority\": \"low\",\n"
            "    \"intent\": \"list_files\"\n"
            "  }}\n"
            "Example 2 - Two step operation:\n"
            "  Instruction: Read a file and write its contents to another file\n"
            "  Response: {{\n"
            "    \"steps\": [\n"
            "      {{\"tool_name\": \"read_file\", \"parameters\": {{\"file_path\": \"input.txt\"}}}},\n"
            "      {{\"tool_name\": \"write_file\", \"parameters\": {{\"file_path\": \"output.txt\", \"content\": \"{{content}}\"}}}}\n"
            "    ],\n"
            "    \"priority\": \"medium\",\n"
            "    \"intent\": \"file_copy\"\n"
            "  }}\n"
            "Example 3 - Multi-step processing:\n"
            "  Instruction: Process data and save the result\n"
            "  Response: {{\n"
            "    \"steps\": [\n"
            "      {{\"tool_name\": \"read_file\", \"parameters\": {{\"file_path\": \"data.txt\"}}}},\n"
            "      {{\"tool_name\": \"calculate\", \"parameters\": {{\"expression\": \"{{content}}\"}}}},\n"
            "      {{\"tool_name\": \"write_file\", \"parameters\": {{\"file_path\": \"result.txt\", \"content\": \"{{result}}\"}}}}\n"
            "    ],\n"
            "    \"priority\": \"medium\",\n"
            "    \"intent\": \"data_processing\"\n"
            "  }}\n"
            "Now respond for the user instruction above."
        )

    def set_prompt_template(self, template: str):
        """Set a custom prompt template"""
        self.prompt_template = template

    def get_prompt_template(self) -> str:
        """Get the current prompt template"""
        return self.prompt_template

    def parse_prompt(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> ToolChain:
        extracted_info = self._extract_intent(user_prompt)
        steps = self._generate_steps(extracted_info, context or {})
        # --- Mapping/Validation Layer ---
        valid_steps = []
        for step in steps:
            if step.tool_name not in self.available_tools:
                print(f"[DEBUG] LLM suggested tool '{step.tool_name}' which is not in the registry. Skipping.")
                continue
            valid_params = {}
            tool_schema = self.available_tools[step.tool_name].parameters
            if not isinstance(tool_schema, dict):
                print(f"[DEBUG] Tool schema for '{step.tool_name}' is not a dict. Skipping step.")
                continue
            if not isinstance(step.parameters, dict):
                print(f"[DEBUG] Step parameters for '{step.tool_name}' are not a dict. Skipping step.")
                continue
            for param, value in step.parameters.items():
                if param in tool_schema:
                    valid_params[param] = value
                else:
                    print(f"[DEBUG] LLM suggested parameter '{param}' for tool '{step.tool_name}' which is not valid. Skipping this parameter.")
            for param in tool_schema:
                if param not in valid_params and param != 'required':
                    if isinstance(context, dict) and param in context:
                        valid_params[param] = context[param]
            step.parameters = valid_params
            valid_steps.append(step)

        if not valid_steps:
            print("[DEBUG] No valid tool steps after mapping/validation. Returning empty chain.")
        return ToolChain(
            steps=valid_steps,
            context=context or {},
            description=f"Generated from prompt: {user_prompt[:100]}..."
        )

    def _extract_intent(self, prompt: str) -> Dict[str, Any]:
        # New schema: list of steps, each with tool_name and parameters
        schema = {
            "steps": [
                {
                    "tool_name": "Name of the tool to call",
                    "parameters": "Dictionary of parameters for this tool"
                }
            ],
            "priority": "Priority level (low/medium/high/urgent)",
            "intent": "The main action the user wants to perform (optional)"
        }
        
        # Get list of available tools for the prompt
        available_tools = list(self.available_tools.keys())
        tools_list = ", ".join(available_tools)
        
        prompt_template = self.prompt_template.format(prompt=prompt, tools_list=tools_list)
        print("[DEBUG] Sending to LLM:\n", prompt_template)
        try:
            extracted = self.llm_helper.extract_structured_data(prompt_template, schema)
            print("[DEBUG] LLM raw output:", extracted)
            return extracted
        except Exception as e:
            print(f"[DEBUG] Failed to extract intent with LLM: {e}")
            return {"steps": [], "priority": "medium", "intent": "unknown"}

    def _generate_steps(self, extracted_info: Dict[str, Any], context: Dict[str, Any]) -> List[ToolStep]:
        steps = []
        step_objs = extracted_info.get("steps", [])
        # Robustness: Only process if step_objs is a list
        if not isinstance(step_objs, list):
            return steps
        for step_info in step_objs:
            tool_name = step_info.get("tool_name")
            parameters = step_info.get("parameters", {})
            steps.append(ToolStep(
                tool_name=tool_name,
                parameters=parameters,
                description=f"Execute {tool_name}",
                depends_on=None,
                condition=None
            ))
        return steps

class ToolOrchestrator:
    def __init__(
        self,
        llm_provider=None,
        tool_registry: Any = None,
        prompt_parser: Optional[PromptParser] = None,
        prompt_template: Optional[str] = None,
        max_steps: int = 10,
        verbose: bool = False
    ):
        self.tool_registry = tool_registry or tool_registry
        self.prompt_parser = prompt_parser or PromptParser(
            llm_provider=llm_provider,
            prompt_template=prompt_template
        )
        self.max_steps = max_steps
        self.verbose = verbose
        self.active_runs = {}
        self.execution_log = []

    def set_prompt_template(self, template: str):
        """Set a custom prompt template for the orchestrator"""
        self.prompt_parser.set_prompt_template(template)

    def get_prompt_template(self) -> str:
        """Get the current prompt template"""
        return self.prompt_parser.get_prompt_template()

    def execute_prompt(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> ChainExecutionResult:
        start_time = datetime.now()
        try:
            chain = self.prompt_parser.parse_prompt(user_prompt, context)
            result = self.execute_chain(chain)
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to execute prompt: {e}")
            return ChainExecutionResult(
                success=False,
                results=[],
                context=context or {},
                execution_time=execution_time
            )
    def execute_chain(self, chain: ToolChain) -> ChainExecutionResult:
        start_time = datetime.now()
        results = []
        current_context = chain.context.copy()
        try:
            for i, step in enumerate(chain.steps):
                # Substitute variables in parameters using context
                resolved_params = self._resolve_parameters(step.parameters, current_context)
                # (Strict) Do NOT auto-fill missing parameters from context unless via {{var}} substitution
                # Execute the tool
                step_result = self.tool_registry.execute_tool(step.tool_name, **resolved_params)
                results.append(step_result)
                # Update context with the result
                if step_result.success and step_result.result:
                    if isinstance(step_result.result, dict):
                        # Add all result keys to context for downstream variable substitution
                        for k, v in step_result.result.items():
                            current_context[k] = v
                    if isinstance(step_result.result, dict) and 'content' in step_result.result:
                        current_context['content'] = step_result.result['content']
                        current_context[f"{step.tool_name}_content"] = step_result.result['content']
                        print(f"[DEBUG] Added 'content' from {step.tool_name} to context.")
                    current_context[f"step_{i}_result"] = step_result.result
                    current_context[f"{step.tool_name}_result"] = step_result.result
                if not step_result.success:
                    logger.warning(f"Step {i} failed: {step_result.error}")
                current_context[f"step_{i}_metadata"] = {
                    "tool_name": step.tool_name,
                    "success": step_result.success,
                    "execution_time": step_result.execution_time
                }
            execution_time = (datetime.now() - start_time).total_seconds()
            return ChainExecutionResult(
                success=all(r.success for r in results),
                results=results,
                context=current_context,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Chain execution failed: {e}")
            return ChainExecutionResult(
                success=False,
                results=results,
                context=current_context,
                execution_time=execution_time
            )
    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        import re
        for key, value in parameters.items():
            if isinstance(value, str):
                # Replace {var} or {{var}} with context value
                def repl(match):
                    var = match.group(1) or match.group(2)
                    return str(context.get(var, match.group(0)))
                # Support both {var} and {{var}} patterns
                resolved_value = re.sub(r'\{(\w+)\}|\{\{(\w+)\}\}', repl, value)
                resolved[key] = resolved_value
            else:
                resolved[key] = value
        return resolved
    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, match.group(0)))
        return re.sub(r'\{\{(\w+)\}\}', replace_var, text)
    def get_available_tools(self) -> Dict[str, Any]:
        schemas = self.tool_registry.get_all_schemas()
        return {
            "tools": list(schemas.keys()),
            "schemas": {name: schema.model_dump() for name, schema in schemas.items()}
        }

class AgentOrchestrator:
    """Interface for orchestrating agent runs and workflows."""
    def __init__(self):
        self.active_runs = {}

    def start_run(self, agent_id, context):
        run_id = f"run_{agent_id}_{len(self.active_runs)+1}"
        self.active_runs[run_id] = {'agent_id': agent_id, 'context': context, 'actions': [], 'status': 'running'}
        self.log_action(run_id, 'start', context)
        return run_id

    def log_action(self, run_id, action, details=None):
        if run_id in self.active_runs:
            self.active_runs[run_id]['actions'].append({'action': action, 'details': details})
        # Also log to audit trail
        from agentspring.api import audit_log
        audit_log('agent_action', user=run_id, details={'action': action, 'details': details})

    def pause_run(self, run_id):
        if run_id in self.active_runs:
            self.active_runs[run_id]['status'] = 'paused'
            self.log_action(run_id, 'pause')

    def inspect_run(self, run_id):
        return self.active_runs.get(run_id, None)

    def debug_run(self, run_id):
        # Stub for debugging agent runs
        run = self.active_runs.get(run_id, None)
        if run:
            return {'run_id': run_id, 'actions': run['actions'], 'context': run['context']}
        return None

    def end_run(self, run_id):
        if run_id in self.active_runs:
            self.log_action(run_id, 'end')
            self.active_runs[run_id]['status'] = 'ended'

def create_orchestrator(llm_provider=None, prompt_template: Optional[str] = None):
    """Create a new orchestrator instance with optional LLM provider and custom prompt template"""
    return ToolOrchestrator(llm_provider=llm_provider, prompt_template=prompt_template)

def execute_prompt(prompt: str, context: Optional[Dict[str, Any]] = None, llm_provider=None):
    """Execute a prompt with the specified LLM provider"""
    return create_orchestrator(llm_provider).execute_prompt(prompt, context)

def execute_chain(chain: ToolChain, llm_provider=None):
    """Execute a tool chain with the specified LLM provider"""
    return create_orchestrator(llm_provider).execute_chain(chain)

def set_prompt_template(template: str, llm_provider=None):
    """Set a custom prompt template for the orchestrator"""
    return create_orchestrator(llm_provider).set_prompt_template(template)

def get_prompt_template(llm_provider=None):
    """Get the current prompt template"""
    return create_orchestrator(llm_provider).get_prompt_template()

__all__ = [
    "ToolStep",
    "ToolChain", 
    "ChainExecutionResult",
    "PromptParser",
    "ToolOrchestrator",
    "orchestrator",
    "execute_prompt",
    "execute_chain",
    "set_prompt_template",
    "get_prompt_template",
    "create_orchestrator"
] 