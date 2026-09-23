from fastapi.testclient import TestClient

from mcp_toolkit.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert set(body["allowed_tools"]) == {"doc_search", "record_lookup", "text_stats"}


def test_tools_endpoint_discovers_mcp_tools():
    r = client.get("/tools")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()["tools"]}
    assert names == {"doc_search", "record_lookup", "text_stats"}


def test_ask_contract():
    r = client.post("/ask", json={"question": "What is the refund policy?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"]
    assert "doc_search" in body["tools_used"]
    assert body["steps"] >= 1
    assert body["latency_ms"] >= 0


def test_ask_rejects_empty():
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_ask_rejects_oversize():
    assert client.post("/ask", json={"question": "x" * 2001}).status_code == 422
