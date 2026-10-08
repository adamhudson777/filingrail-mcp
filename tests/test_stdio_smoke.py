"""Start the server the way a real MCP client does and list its tools.

Speaks raw newline-delimited JSON-RPC over stdio so the test does not depend on
which `mcp` major version (1.x or 2.x) is installed -- that is the whole point:
0.1.2 crashed on import under mcp 2.x (support report 2026-09-26).

Run:  python -m pytest tests/ -q
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time

EXPECTED_TOOLS = {
    "search_companies",
    "get_recent_filings",
    "get_financials",
    "get_financials_history",
    "get_insider_trades",
    "get_8k_events",
    "get_13f_holdings",
    "health",
}


def _send(proc: subprocess.Popen, msg: dict) -> None:
    proc.stdin.write((json.dumps(msg) + "\n").encode())
    proc.stdin.flush()


def _recv(proc: subprocess.Popen, want_id: int, timeout: float = 30.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            raise AssertionError("server closed stdout before replying")
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue  # not a JSON-RPC frame (shouldn't happen on stdout, but be lenient)
        if msg.get("id") == want_id:
            return msg
    raise AssertionError(f"timed out waiting for response id={want_id}")


def _drain_stderr(proc: subprocess.Popen, sink: list) -> None:
    for line in proc.stderr:
        sink.append(line.decode(errors="replace"))


def test_server_starts_and_lists_all_tools():
    env = dict(os.environ)
    env.setdefault("RAPIDAPI_KEY", "test-key-not-used-by-tools-list")
    proc = subprocess.Popen(
        [sys.executable, "-m", "filingrail_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    stderr_lines: list = []
    threading.Thread(target=_drain_stderr, args=(proc, stderr_lines), daemon=True).start()
    try:
        _send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "filingrail-mcp-smoke-test", "version": "0"},
            },
        })
        init = _recv(proc, 1)
        assert "result" in init, f"initialize failed: {init}\nstderr: {''.join(stderr_lines)}"
        assert init["result"]["serverInfo"]["name"] == "filingrail"

        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        _send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        listed = _recv(proc, 2)
        assert "result" in listed, f"tools/list failed: {listed}\nstderr: {''.join(stderr_lines)}"
        names = {t["name"] for t in listed["result"]["tools"]}
        assert names == EXPECTED_TOOLS, f"tool set drifted: {sorted(names)}"

        # every tool must publish an input schema a client can render
        for t in listed["result"]["tools"]:
            assert t.get("inputSchema", {}).get("type") == "object", t["name"]
    finally:
        proc.kill()
        proc.wait(timeout=10)

    # the process must not have crashed on import -- the 0.1.2 failure mode
    assert "ModuleNotFoundError" not in "".join(stderr_lines)


def test_import_path_resolves_on_this_mcp_version():
    import filingrail_mcp.server as s

    assert s.mcp is not None
    assert type(s.mcp).__name__ in {"MCPServer", "FastMCP"}
