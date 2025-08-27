"""Agent loop (minimal): perceive -> plan -> act -> (optional reflect)"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, TYPE_CHECKING

# Only import heavy/optional modules for type checking.
# At runtime these imports are skipped, preventing import-time failures.
if TYPE_CHECKING:
    from . import Agent
    from ..planner import Planner
    from ..workflow import Workflow


class AgentLoop:
    def __init__(
        self,
        planner: "Planner",
        agent: Optional["Agent"] = None,
        max_iterations: int = 1,
        enable_reflection: bool = False,
    ) -> None:
        self.planner = planner
        self.agent = agent
        self.max_iterations = max_iterations
        self.enable_reflection = enable_reflection

    async def run_async(self, user_prompt: str) -> Dict[str, Any]:
        # Lazy import here too, in case workflow has optional deps
        from ..workflow import Workflow  # type: ignore

        wf: "Workflow" = await self.planner.plan_workflow(user_prompt)
        result = await wf.execute()
        return {"status": "completed", "workflow": wf.to_dict(), "result": result}

    def run(self, user_prompt: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # In an async context already
            return loop.create_task(self.run_async(user_prompt))  # type: ignore

        return asyncio.run(self.run_async(user_prompt))


__all__ = ["AgentLoop"]
