import pytest
from agentspring.llm import LLMHelper, PromptTemplates, OutputParsers, classify, detect_priority, summarize, extract_structured_data
from unittest.mock import patch
from langchain_community.llms import Ollama

def test_llmhelper_classify(monkeypatch):
    helper = LLMHelper()
    monkeypatch.setattr(helper, "_call_with_fallback", lambda *a, **k: "TestCategory")
    assert helper.classify("text", ["A", "B"]) == "TestCategory"

def test_llmhelper_detect_priority(monkeypatch):
    helper = LLMHelper()
    monkeypatch.setattr(helper, "_call_with_fallback", lambda *a, **k: "High")
    assert helper.detect_priority("text") == "High"

def test_llmhelper_summarize(monkeypatch):
    helper = LLMHelper()
    monkeypatch.setattr(helper, "_call_with_fallback", lambda *a, **k: "Short summary")
    assert helper.summarize("long text", 10) == "Short summary"

def test_llmhelper_extract_structured_data(monkeypatch):
    with patch.object(Ollama, "invoke", lambda self, prompt: '{"foo": "bar"}'):
        helper = LLMHelper()
        result = helper.extract_structured_data("text", {"foo": "desc"})
        assert result["foo"] == "bar"

def test_prompt_templates():
    assert "Classify this text" in PromptTemplates.classification(["A", "B"])
    assert "Summarize this text" in PromptTemplates.summarization(50)
    assert "Extract information" in PromptTemplates.extraction({"foo": "desc"})
    assert "sentiment" in PromptTemplates.sentiment()
    assert "question" in PromptTemplates.question_answer()
    assert "true|false" in PromptTemplates.boolean("Prompt")

def test_output_parsers():
    assert OutputParsers.json('{"a":1}') == {"a": 1}
    assert OutputParsers.list('[1,2]') == [1, 2]
    assert OutputParsers.string('  hi  ') == 'hi'

def test_module_helpers(monkeypatch):
    monkeypatch.setattr(LLMHelper, "classify", lambda self, t, c, max_retries=3: "A")
    monkeypatch.setattr(LLMHelper, "detect_priority", lambda self, t, priorities=None, max_retries=3: "High")
    monkeypatch.setattr(LLMHelper, "summarize", lambda self, t, max_length=100, max_retries=3: "Sum")
    monkeypatch.setattr(LLMHelper, "extract_structured_data", lambda self, t, s, max_retries=3: {"foo": "bar"})
    assert classify("t", ["A"]) == "A"
    assert detect_priority("t") == "High"
    assert summarize("t") == "Sum"
    assert extract_structured_data("t", {"foo": "desc"})["foo"] == "bar" 