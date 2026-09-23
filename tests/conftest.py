import asyncio
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["MOCK_MODE"] = "true"
os.environ["DATA_DIR"] = str(ROOT / "data")


def run(coro):
    return asyncio.run(coro)


@pytest.fixture()
def llm():
    from mcp_toolkit.llm import MockChatLLM

    return MockChatLLM()


@pytest.fixture()
def tool_client():
    from mcp_toolkit.mcp_client import MCPToolClient
    from mcp_toolkit.server import create_server

    return MCPToolClient(server=create_server(os.environ["DATA_DIR"]))


@pytest.fixture()
def agent(llm, tool_client):
    from mcp_toolkit.agent import build_agent

    return build_agent(llm, tool_client)
