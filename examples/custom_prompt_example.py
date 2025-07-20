#!/usr/bin/env python3
"""
Example: Customizing the AgentSpring Orchestrator Prompt Template

This demonstrates how users can customize the prompt template for:
1. Domain-specific optimization
2. Better mathematical operations
3. Improved multi-step workflows
4. Custom examples and instructions
"""

from agentspring.orchestration import (
    execute_prompt, 
    set_prompt_template, 
    get_prompt_template,
    create_orchestrator
)

def example_1_basic_usage():
    """Show basic usage with default prompt"""
    print("=== Example 1: Basic Usage (Default Prompt) ===")
    result = execute_prompt("Calculate the sum of numbers 1 through 10")
    print(f"Success: {result.success}")
    print(f"Steps: {len(result.results)}")
    print()

def example_2_math_optimized_prompt():
    """Show usage with math-optimized prompt"""
    print("=== Example 2: Math-Optimized Prompt ===")
    
    math_prompt_template = """
You are a mathematical computation orchestrator. Given the following user instruction, 
extract a list of steps, where each step has a tool_name and a parameters dictionary. 
Respond ONLY with a valid JSON object with keys: steps (list of steps), priority, and intent.

IMPORTANT: Only use tool names from this exact list: {tools_list}

User instruction: {prompt}

CRITICAL RULES FOR MATHEMATICAL OPERATIONS:
- For summing ranges (e.g., "1 through 10", "1 to 10"), use sum_range tool
- For simple calculations (e.g., "2 + 3", "5 * 4"), use calculate tool
- For random number generation, use generate_random tool
- For prime number checking, use is_prime tool

Examples:
1. "Sum numbers 1 to 10" → {{"tool_name": "sum_range", "parameters": {{"start": 1, "end": 10}}}}
2. "Calculate 5 + 3" → {{"tool_name": "calculate", "parameters": {{"expression": "5 + 3"}}}}
3. "Check if 17 is prime" → {{"tool_name": "is_prime", "parameters": {{"number": 17}}}}

Now respond for the user instruction above.
"""
    
    # Set the custom prompt template
    set_prompt_template(math_prompt_template)
    
    result = execute_prompt("Calculate the sum of numbers 1 through 10")
    print(f"Success: {result.success}")
    print(f"Steps: {len(result.results)}")
    if result.results:
        for i, step in enumerate(result.results):
            print(f"  Step {i+1}: {step.result}")
    print()

def example_3_multi_step_optimized_prompt():
    """Show usage with multi-step optimized prompt"""
    print("=== Example 3: Multi-Step Optimized Prompt ===")
    
    multi_step_prompt_template = """
You are a multi-step workflow orchestrator. Given the following user instruction, 
extract a list of steps, where each step has a tool_name and a parameters dictionary. 
Respond ONLY with a valid JSON object with keys: steps (list of steps), priority, and intent.

IMPORTANT: Only use tool names from this exact list: {tools_list}

User instruction: {prompt}

CRITICAL RULES FOR MULTI-STEP WORKFLOWS:
- Always use {{result}} variables to pass data between steps
- For text processing chains, use text_to_uppercase → count_characters
- For random number operations, use generate_random → calculate
- For mathematical chains, use sum_range → write_file

Examples:
1. "Convert text to uppercase and count characters":
   [
     {{"tool_name": "text_to_uppercase", "parameters": {{"text": "hello world"}}}},
     {{"tool_name": "count_characters", "parameters": {{"text": "{{uppercase_text}}"}}}}
   ]

2. "Generate random number and double it":
   [
     {{"tool_name": "generate_random", "parameters": {{"min_value": 1, "max_value": 100}}}},
     {{"tool_name": "calculate", "parameters": {{"expression": "{{random_number}} * 2"}}}}
   ]

Now respond for the user instruction above.
"""
    
    # Create a new orchestrator with custom prompt
    custom_orchestrator = create_orchestrator(multi_step_prompt_template)
    
    result = custom_orchestrator.execute_prompt("Convert Hello World to uppercase and count its characters")
    print(f"Success: {result.success}")
    print(f"Steps: {len(result.results)}")
    if result.results:
        for i, step in enumerate(result.results):
            print(f"  Step {i+1}: {step.result}")
    print()

def example_4_domain_specific_prompt():
    """Show usage with domain-specific prompt"""
    print("=== Example 4: Domain-Specific Prompt (File Operations) ===")
    
    file_ops_prompt_template = """
You are a file operations orchestrator. Given the following user instruction, 
extract a list of steps, where each step has a tool_name and a parameters dictionary. 
Respond ONLY with a valid JSON object with keys: steps (list of steps), priority, and intent.

IMPORTANT: Only use tool names from this exact list: {tools_list}

User instruction: {prompt}

CRITICAL RULES FOR FILE OPERATIONS:
- For reading files, use read_file with file_path parameter
- For writing files, use write_file with file_path and content parameters
- For listing files, use list_files with directory parameter
- Always use {{content}} to pass file content between steps

Examples:
1. "Read file and write to another file":
   [
     {{"tool_name": "read_file", "parameters": {{"file_path": "input.txt"}}}},
     {{"tool_name": "write_file", "parameters": {{"file_path": "output.txt", "content": "{{content}}"}}}}
   ]

2. "List files in directory":
   [
     {{"tool_name": "list_files", "parameters": {{"directory": "."}}}}
   ]

Now respond for the user instruction above.
"""
    
    # Create orchestrator with file operations prompt
    file_orchestrator = create_orchestrator(file_ops_prompt_template)
    
    result = file_orchestrator.execute_prompt("List files in the current directory")
    print(f"Success: {result.success}")
    print(f"Steps: {len(result.results)}")
    if result.results:
        for i, step in enumerate(result.results):
            print(f"  Step {i+1}: {step.result}")
    print()

def show_current_prompt():
    """Show the current prompt template"""
    print("=== Current Prompt Template ===")
    print(get_prompt_template())
    print()

if __name__ == "__main__":
    print("🤖 AgentSpring Custom Prompt Examples")
    print("=" * 50)
    
    # Show current prompt
    show_current_prompt()
    
    # Run examples
    example_1_basic_usage()
    example_2_math_optimized_prompt()
    example_3_multi_step_optimized_prompt()
    example_4_domain_specific_prompt()
    
    print("✅ Examples completed!")
    print("\n💡 Key Benefits of Custom Prompts:")
    print("  - Domain-specific optimization")
    print("  - Better tool selection")
    print("  - Improved multi-step workflows")
    print("  - Custom examples and rules")
    print("  - Iterative prompt engineering") 