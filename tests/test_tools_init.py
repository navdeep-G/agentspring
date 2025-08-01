import pytest
from agentspring.tools import ToolRegistry, tool, tool_registry, ToolSchema, ToolExecutionResult

def test_tool_registry_register_and_execute():
    reg = ToolRegistry()
    @reg.register('foo', 'desc')
    def foo(x):
        return x + 1
    result = reg.execute_tool('foo', x=1)
    assert result.success and result.result == 2

def test_tool_decorator_registers():
    @tool('bar', 'desc')
    def bar(y):
        return y * 2
    assert tool_registry.get_tool('bar') is not None

def test_tool_schema_and_execution_result():
    schema = ToolSchema(name='n', description='d', parameters={}, returns={})
    res = ToolExecutionResult(success=True, result=123, execution_time=0.1)
    assert schema.name == 'n'
    assert res.success
