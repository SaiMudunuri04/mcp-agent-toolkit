"""Spawns uvicorn, hits POST /ask N times, reports p50/p95 latency. Mock mode."""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
PORT = 8124
N = 15
QUESTION = "What is the refund policy?"


def wait_for_health() -> None:
    url = f"http://127.0.0.1:{PORT}/health"
    with httpx.Client(timeout=2, trust_env=False) as client:
        for _ in range(60):
            try:
                r = client.get(url)
                if r.status_code == 200:
                    return
            except Exception:
                time.sleep(0.5)
    raise RuntimeError("server did not become healthy")


def main() -> None:
    env = dict(os.environ, MOCK_MODE="true", DATA_DIR=str(ROOT / "data"))
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "mcp_toolkit.api:app",
         "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=str(ROOT), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_health()
        lat = []
        with httpx.Client(timeout=30, trust_env=False) as client:
            for _ in range(N):
                t0 = time.perf_counter()
                r = client.post(f"http://127.0.0.1:{PORT}/ask",
                                json={"question": QUESTION})
                r.raise_for_status()
                lat.append((time.perf_counter() - t0) * 1000)
        lat.sort()
        p50 = statistics.median(lat)
        p95 = lat[int(0.95 * (len(lat) - 1))]
        print(json.dumps({"n": N, "p50_ms": round(p50, 2), "p95_ms": round(p95, 2),
                          "min_ms": round(lat[0], 2), "max_ms": round(lat[-1], 2)}))
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
