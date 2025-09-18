import os
import sys
import pathlib
import asyncio

# Ensure project root is on sys.path when running this file directly
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentspring.db.session import engine, Base
from sqlalchemy import text

# Ensure all models are registered before creating tables
from agentspring.db import models as _m  # noqa: F401
from agentspring.db import models_versioned as _mv  # noqa: F401


async def main():
    async with engine.begin() as conn:
        # Requires pgvector installed on the Postgres server
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    print("DB initialized")


if __name__ == "__main__":
    asyncio.run(main())
