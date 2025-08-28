"""
Agentic Workflow (Planner + Loop + Memory)
------------------------------------------
This example demonstrates a truly *agentic* flow using the new components:

- Tools are declared via @tool and auto-registered in ToolRegistry
- A Planner turns natural-language instructions into a Workflow (DAG of TOOL nodes)
- AgentLoop runs: perceive (prompt) -> plan (Planner) -> act (Workflow.execute)
- InMemoryMemory stores a tiny bit of context between runs

You can run it with:
    python examples/agentic_workflow_example.py
"""

import asyncio
import json
import logging
from typing import Dict, Optional

import aiohttp

from agentspring.llm import LLMProvider, register_provider
from agentspring.planner import Planner
from agentspring.loop import AgentLoop
from agentspring.memory import InMemoryMemory
from agentspring.tools import tool, tool_registry


# ---------------------------------------------------------------------------
# 0) Minimal Ollama LLM provider (works with your agentspring.llm base)
# ---------------------------------------------------------------------------

class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str = "llama3.2:latest",
        base_url: str = "http://localhost:11434",
    ):
        super().__init__(
            config={
                "timeout": 30,
                "max_retries": 3,
                "rate_limit": {"requests_per_minute": 60, "max_concurrent": 10, "retry_after": 60},
                "validate_input": False,  # keep loose for quickstarts
            }
        )
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_async(self, prompt: str, **kwargs) -> str:
        sess = await self._get_session()
        try:
            async with sess.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("response", "")
        except Exception as e:
            self.logger.error(f"Ollama generate_async error: {e}")
            return f"ERROR: {e}"

    async def stream_async(self, prompt: str, **kwargs):
        sess = await self._get_session()
        try:
            async with sess.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True},
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.content:
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Ollama stream_async error: {e}")
            yield f"ERROR: {e}"

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


# Make the provider available via the registry (optional but nice)
register_provider("ollama")(OllamaProvider)
llm = OllamaProvider()


# ---------------------------------------------------------------------------
# 1) Tools (these are what the Planner can choose from)
# ---------------------------------------------------------------------------

@tool("analyze_sentiment", "Analyze the sentiment of text")
async def analyze_sentiment(text: str) -> Dict[str, object]:
    pos = {"good", "great", "excellent", "happy", "awesome", "love"}
    neg = {"bad", "terrible", "awful", "sad", "horrible", "hate"}
    score = 0
    for w in text.lower().split():
        score += 1 if w in pos else -1 if w in neg else 0
    sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"sentiment": sentiment, "score": score}


@tool("summarize_text", "Summarize text to N sentences")
async def summarize_text(text: str, max_sentences: int = 2) -> dict:
    # Cast max_sentences safely
    try:
        max_sentences = int(max_sentences)
    except Exception:
        max_sentences = 2

    sentences = [s.strip() for s in text.split(".") if s.strip()]
    summary = ". ".join(sentences[:max_sentences]) + ("." if sentences else "")
    return {"summary": summary, "sentence_count": min(len(sentences), max_sentences)}


@tool("extract_keywords", "Extract keywords by simple frequency")
async def extract_keywords(text: str, top_n: int = 5) -> dict:
    try:
        top_n = int(top_n)
    except Exception:
        top_n = 5

    import re, collections, string
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stop = {"the", "and", "are", "is", "with", "for", "that", "from", "this", "have", "has", "was", "were", "but"}
    words = [w.strip(string.punctuation) for w in words if w not in stop]
    counter = collections.Counter(words)
    return {"keywords": [w for w, _ in counter.most_common(top_n)], "unique": len(counter)}


# ---------------------------------------------------------------------------
# 2) Use Planner + AgentLoop + Memory together
# ---------------------------------------------------------------------------

async def interactive():
    """
    - Memory stores a tiny "notes" field across turns
    - Planner (with the Ollama provider) turns your instruction into a tool DAG
    - AgentLoop runs the planned Workflow and returns results + workflow dict
    """
    memory = InMemoryMemory()
    planner = Planner(llm=llm)     # explicitly pass LLM; otherwise Planner tries default provider
    loop = AgentLoop(planner)      # minimal perceive -> plan -> act loop

    print("Available tools:", ", ".join(tool_registry.list_tools()))
    print("Type 'exit' to quit.\n")

    while True:
        user = input("What should I do? ").strip()

        if not user:             # <- if user gave nothing, don't run
            print("Please type an instruction.")
            continue

        prior = memory.recall("notes", "")
        prompt = user if not prior else f"{user}\n\nContext from last run: {prior}"

        print("\n[planning + running…]")
        result = await loop.run_async(prompt)

        # Unpack the return: {'workflow': <wf_dict>, 'result': <exec_result>, 'status': 'completed'}
        wf = result.get("workflow", {})
        exec_result = result.get("result", {})  # {'status', 'context', 'results'}

        # Pretty-print the workflow nodes + tool outputs
        nodes = wf.get("nodes", {})
        if not nodes:
            print("No nodes were planned. (Do you have any tools registered?)\n")
            continue

        print("\n=== Planned Nodes ===")
        for node_id, node in nodes.items():
            cfg = node.get("config", {})
            tool = cfg.get("tool_name", "<unknown>")
            status = node.get("status", "<unknown>")
            print(f"- {node_id}: tool={tool} status={status}")

        print("\n=== Results ===")
        for node_id, node in nodes.items():
            cfg = node.get("config", {})
            tool = cfg.get("tool_name", "<unknown>")
            res = node.get("result") or {}
            ok = res.get("success")
            payload = res.get("result")
            if ok:
                print(f"[{tool}] → {json.dumps(payload, ensure_ascii=False)}")
            else:
                err = res.get("error", "unknown error")
                print(f"[{tool}] ERROR → {err}")

        # Save a tiny note to memory for the next turn
        # (Here we just remember which tools ran successfully)
        successful_tools = [
            (node.get("config", {}) or {}).get("tool_name", "")
            for node in nodes.values()
            if (node.get("result") or {}).get("success")
        ]
        memory.remember("notes", f"Previously ran: {', '.join(t for t in successful_tools if t)}")

        print("\n" + "=" * 50 + "\n")


# ---------------------------------------------------------------------------
# 3) Entrypoint & cleanup
# ---------------------------------------------------------------------------

import atexit

def _cleanup():
    try:
        asyncio.run(llm.close())
    except RuntimeError:
        # If an event loop is already running (rare in this script), skip
        pass

atexit.register(_cleanup)

if __name__ == "__main__":
    asyncio.run(interactive())
