"""
LLM Integration Helpers for AgentSpring
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional, Union
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LLMHelper:
    """Helper class for common LLM operations"""
    
    def __init__(self, model: str = "llama3.2", base_url: Optional[str] = None):
        """Initialize LLM with configurable model and base URL"""
        self.base_url = base_url or "http://localhost:11434"
        self.llm = Ollama(model=model, base_url=self.base_url)
        self.json_parser = JsonOutputParser()
    
    def classify(self, text: str, categories: List[str], max_retries: int = 3) -> str:
        """Classify text into one of the given categories"""
        prompt = PromptTemplate(
            template="Classify this text into one of {categories}. Respond ONLY with a JSON object: {{\"category\": \"<category>\"}}.\n\nText: {text}",
            input_variables=["text", "categories"]
        )
        
        return self._call_with_fallback(
            prompt.format(text=text, categories=categories),
            categories,
            "Other",
            max_retries
        )
    
    def detect_priority(self, text: str, priorities: Optional[List[str]] = None, max_retries: int = 3) -> str:
        """Detect priority level in text"""
        if priorities is None:
            priorities = ["Low", "Medium", "High", "Critical"]
        
        prompt = PromptTemplate(
            template="Assign a priority to this text: {text}\nRespond ONLY with a JSON object: {{\"priority\": \"<priority>\"}}.",
            input_variables=["text"]
        )
        
        return self._call_with_fallback(
            prompt.format(text=text),
            priorities,
            "Medium",
            max_retries
        )
    
    def summarize(self, text: str, max_length: int = 100, max_retries: int = 3) -> str:
        """Summarize text"""
        prompt = PromptTemplate(
            template="Summarize this text in {max_length} characters or less. Respond ONLY with a JSON object: {{\"summary\": \"<summary>\"}}.\n\nText: {text}",
            input_variables=["text", "max_length"]
        )
        
        result = self._call_with_fallback(
            prompt.format(text=text, max_length=max_length),
            None,
            text[:max_length] + "..." if len(text) > max_length else text,
            max_retries
        )
        
        return result if result else text[:max_length] + "..." if len(text) > max_length else text
    
    def extract_structured_data(self, text: str, schema: Dict[str, str], max_retries: int = 3) -> Dict[str, Any]:
        """Extract structured data from text based on schema"""
        schema_desc = ", ".join([f'"{k}": "{v}"' for k, v in schema.items()])
        prompt = PromptTemplate(
            template="Extract information from this text. Respond ONLY with a JSON object: {{{schema_desc}}}.\n\nText: {text}",
            input_variables=["text", "schema_desc"]
        )
        
        try:
            response = self.llm.invoke(prompt.format(text=text, schema_desc=schema_desc)).strip()
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to extract structured data: {e}")
            return {k: "unknown" for k in schema.keys()}
    
    def _call_with_fallback(self, prompt: str, valid_options: Optional[List[str]], default: str, max_retries: int) -> str:
        """Call LLM with retry logic and fallback to regex extraction"""
        response = ""
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(prompt).strip()
                result = json.loads(response)
                
                # Extract the value (could be any key in the JSON)
                value = list(result.values())[0] if result else default
                
                # Validate against valid options if provided
                if valid_options and value not in valid_options:
                    # Try to find closest match
                    for option in valid_options:
                        if option.lower() in value.lower() or value.lower() in option.lower():
                            return option
                    return default
                
                return value
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.warning(f"LLM call failed after {max_retries} attempts: {e}")
                    # Fallback to regex extraction
                    if valid_options and response:
                        for option in valid_options:
                            if re.search(option, response, re.IGNORECASE):
                                return option
                    return default
                logger.warning(f"LLM call failed, attempt {attempt + 1}/{max_retries}: {e}")
        
        return default

class PromptTemplates:
    """Collection of common prompt templates"""
    
    @staticmethod
    def classification(categories: List[str]) -> str:
        """Template for classification tasks"""
        return f"""Classify this text into one of {categories}. 
Respond ONLY with a JSON object: {{"category": "<category>"}}.

Text: {{text}}"""
    
    @staticmethod
    def summarization(max_length: int = 100) -> str:
        """Template for summarization tasks"""
        return f"""Summarize this text in {max_length} characters or less.
Respond ONLY with a JSON object: {{"summary": "<summary>"}}.

Text: {{text}}"""
    
    @staticmethod
    def extraction(schema: Dict[str, str]) -> str:
        """Template for data extraction tasks"""
        schema_desc = ", ".join([f'"{k}": "{v}"' for k, v in schema.items()])
        return f"""Extract information from this text.
Respond ONLY with a JSON object: {{{schema_desc}}}.

Text: {{text}}""" 

    @staticmethod
    def sentiment() -> str:
        return """Analyze the sentiment of this text. Respond ONLY with a JSON object: {\"sentiment\": \"positive|neutral|negative\"}.\n\nText: {text}"""
    @staticmethod
    def question_answer() -> str:
        return """Answer the following question based on the provided context. Respond ONLY with a JSON object: {\"answer\": \"<answer>\"}.\n\nContext: {context}\nQuestion: {question}"""
    @staticmethod
    def boolean(prompt: str) -> str:
        return f"""{prompt}\nRespond ONLY with a JSON object: {{\"answer\": true|false}}."""

class OutputParsers:
    """Common output parsers for LLM responses"""
    @staticmethod
    def json(response: str) -> dict:
        try:
            return json.loads(response)
        except Exception:
            return {}
    @staticmethod
    def list(response: str) -> list:
        try:
            return json.loads(response) if response.strip().startswith("[") else [response.strip()]
        except Exception:
            return [response.strip()]
    @staticmethod
    def string(response: str) -> str:
        return response.strip()

default_llm = LLMHelper()

def classify(text: str, categories: List[str], max_retries: int = 3) -> str:
    """Classify text into one of the given categories using the default LLM."""
    return default_llm.classify(text, categories, max_retries=max_retries)

def detect_priority(text: str, priorities: Optional[List[str]] = None, max_retries: int = 3) -> str:
    """Detect priority level in text using the default LLM."""
    return default_llm.detect_priority(text, priorities=priorities, max_retries=max_retries)

def summarize(text: str, max_length: int = 100, max_retries: int = 3) -> str:
    """Summarize text using the default LLM."""
    return default_llm.summarize(text, max_length=max_length, max_retries=max_retries)

def extract_structured_data(text: str, schema: Dict[str, str], max_retries: int = 3) -> Dict[str, Any]:
    """Extract structured data from text using the default LLM."""
    return default_llm.extract_structured_data(text, schema, max_retries=max_retries) 