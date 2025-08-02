from agentspring.orchestration import create_orchestrator
from agentspring.tools import tool_registry

from examples import custom_tools

tool_registry.register(custom_tools.llm_summarize_issues)
tool_registry.register(custom_tools.write_summary)
tool_registry.register(custom_tools.read_csv)
tool_registry.register(custom_tools.print_csv_head)

orchestrator = create_orchestrator()

user_instruction = "Return the top 5 rows of the following file: examples/complaints.csv."

orchestrator.execute_prompt(user_instruction)