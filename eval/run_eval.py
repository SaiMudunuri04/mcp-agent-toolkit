"""Golden-set eval: runs the agent in mock mode over eval/golden_set.json.

Reports pass/total. Exits non-zero on any failure (CI gate).
All data is synthetic and bundled; the mock LLM is deterministic.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

os.environ["MOCK_MODE"] = "true"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from mcp_toolkit.agent import build_agent, run_ask  # noqa: E402
from mcp_toolkit.llm import MockChatLLM  # noqa: E402
from mcp_toolkit.mcp_client import MCPToolClient  # noqa: E402
from mcp_toolkit.server import create_server  # noqa: E402


async def main_async() -> int:
    cases = json.loads(Path("eval/golden_set.json").read_text(encoding="utf-8"))
    client = MCPToolClient(server=create_server("data"))
    app = build_agent(MockChatLLM(), client)
    passed = 0
    for i, case in enumerate(cases, 1):
        result = await run_ask(app, case["message"])
        answer = result["answer"].lower()
        ok_tools = all(t in result["tools_used"] for t in case["expect_tools"])
        if not case["expect_tools"]:
            ok_tools = result["tools_used"] == []
        ok_terms = all(t.lower() in answer for t in case["must_contain"])
        ok = ok_tools and ok_terms and result["valid"]
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] case {i}: tools={result['tools_used']}")
        if not ok:
            print(f"   message={case['message']!r}")
            print(f"   answer={result['answer'][:200]!r}")
    print(f"eval: {passed}/{len(cases)} passed")
    return 0 if passed == len(cases) else 1


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
