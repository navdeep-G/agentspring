import pytest
from agentspring import orchestration

def test_agent_orchestrator_lifecycle():
    orchestrator = orchestration.AgentOrchestrator()
    run_id = orchestrator.start_run('agent1', {'foo': 'bar'})
    assert run_id in orchestrator.active_runs
    orchestrator.pause_run(run_id)
    assert orchestrator.active_runs[run_id]['status'] == 'paused'
    # There is no resume_run, so just check status remains paused
    orchestrator.log_action(run_id, 'test_action', {'a': 1})
    actions = orchestrator.active_runs[run_id]['actions']
    assert any(a['action'] == 'test_action' for a in actions)
    inspected = orchestrator.inspect_run(run_id)
    assert inspected['agent_id'] == 'agent1'
    debugged = orchestrator.debug_run(run_id)
    assert debugged['run_id'] == run_id
    orchestrator.end_run(run_id)
    assert orchestrator.active_runs[run_id]['status'] == 'ended'

def test_tool_orchestrator_prompt_template():
    tool_orch = orchestration.ToolOrchestrator()
    default_tpl = tool_orch.get_prompt_template()
    tool_orch.set_prompt_template('Hello {foo}')
    assert tool_orch.get_prompt_template() == 'Hello {foo}'
    tool_orch.set_prompt_template(default_tpl)

def test_prompt_parser_extract_chain():
    parser = orchestration.PromptParser()
    # Use a prompt that matches the expected schema for steps
    prompt = '{"steps": [{"tool_name": "foo", "parameters": {"bar": 1}}]}'
    chain = parser.parse_prompt(prompt, context={'foo': 'bar'})
    assert hasattr(chain, 'steps')
    assert isinstance(chain.steps, list)
    if chain.steps:
        step = chain.steps[0]
        assert hasattr(step, 'tool_name') or 'tool_name' in step.__dict__

# Test that parse_prompt does not crash on invalid input
import pytest

def test_prompt_parser_invalid_input():
    parser = orchestration.PromptParser()
    try:
        chain = parser.parse_prompt('nonsense', context=None)
        # Should not raise, but may return empty or default chain
        assert hasattr(chain, 'steps')
    except Exception as e:
        pytest.fail(f"parse_prompt should not crash, got: {e}")

def test_execute_prompt_calls_orchestrator(monkeypatch):
    called = {}
    # Match the signature of the real method: (self, prompt, context=None)
    def fake_execute_prompt(self, prompt, context=None):
        called['prompt'] = prompt
        called['context'] = context
        return 'result'
    monkeypatch.setattr(
        orchestration, 'orchestrator', type('O', (), {'execute_prompt': fake_execute_prompt})())
    result = orchestration.execute_prompt('prompt', {'foo': 'bar'})
    assert result == 'result'

def test_prompt_parser_handles_invalid_tool(monkeypatch):
    parser = orchestration.PromptParser()
    # Simulate an invalid tool in the prompt
    prompt = '{"steps": [{"tool_name": "not_registered", "parameters": {"bar": 1}}]}'
    chain = parser.parse_prompt(prompt, context={})
    assert hasattr(chain, "steps")
    assert isinstance(chain.steps, list)

# Edge case: parse_prompt with invalid JSON
# Already tested in test_prompt_parser_invalid_input

def test_prompt_parser_handles_nonlist_steps():
    parser = orchestration.PromptParser()
    # Pass steps as a string instead of a list
    prompt = '{"steps": "notalist"}'
    chain = parser.parse_prompt(prompt, context={})
    assert hasattr(chain, "steps")
    assert isinstance(chain.steps, list)

# Exception in extract_structured_data is handled in _extract_intent, which is called by parse_prompt
# Already tested via test_prompt_parser_invalid_input
