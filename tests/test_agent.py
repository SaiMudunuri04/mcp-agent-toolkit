import pytest

from mcp_toolkit.agent import run_ask
from mcp_toolkit.mcp_client import MCPToolClient
from tests.conftest import run


def test_agent_uses_doc_search(agent):
    r = run(run_ask(agent, "What is the refund policy?"))
    assert "doc_search" in r["tools_used"]
    assert "refund" in r["answer"].lower()
    assert r["valid"]


def test_agent_record_lookup(agent):
    r = run(run_ask(agent, "What is the status of record R-2003?"))
    assert "record_lookup" in r["tools_used"]
    assert "R-2003" in r["answer"]


def test_agent_multi_hop(agent):
    r = run(run_ask(agent, "What does the refund policy say, and what is the status of record R-2003?"))
    assert "doc_search" in r["tools_used"]
    assert "record_lookup" in r["tools_used"]
    assert r["steps"] == 2


def test_agent_answers_directly_when_no_tool_fits(agent):
    r = run(run_ask(agent, "What is the capital of France?"))
    assert r["tools_used"] == []
    assert "don't have enough information" in r["answer"].lower()


def test_scoped_permissions_block_disallowed_tool(tool_client):
    scoped = MCPToolClient(server=tool_client._server, allowed_tools=("doc_search",))
    with pytest.raises(PermissionError):
        run(scoped.call_tool("record_lookup", {"record_id": "R-2001"}))


def test_mcp_tool_discovery(tool_client):
    tools = run(tool_client.list_tools())
    names = {t["name"] for t in tools}
    assert names == {"doc_search", "record_lookup", "text_stats"}


def test_validation_fallback_on_empty_answer(agent, llm, tool_client):
    # LLM that returns an empty final answer -> validator substitutes safe fallback
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatGeneration, ChatResult

    from mcp_toolkit.agent import build_agent
    from mcp_toolkit.llm import MockChatLLM

    class EmptyLLM(MockChatLLM):
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content='{"answer": "  "}'))]
            )

    app = build_agent(EmptyLLM(), tool_client)
    r = run(run_ask(app, "What is the refund policy?"))
    assert r["answer"] != ""
    assert "rephrasing" in r["answer"].lower()
