#!/usr/bin/env python3
"""Deterministic teaching-only Agent loop: mock decisions and mock report tools.

No network, LLM API, file access or credentials. Run: python3 scripts/agent_loop.py
"""
from __future__ import annotations

REPORTS = {"Q1": 100, "Q2": 120, "Q3": 132}
ALLOWED = {"read_report"}


def choose_next(messages: list[dict]) -> dict:
    """Mock model policy, not a real model or a recommendation for production."""
    seen = {msg["quarter"] for msg in messages if msg["role"] == "tool" and msg.get("ok")}
    for quarter in REPORTS:
        if quarter not in seen:
            return {"role": "assistant", "tool_calls": [
                {"id": f"call-{quarter}", "name": "read_report", "arguments": {"quarter": quarter}}
            ]}
    values = {msg["quarter"]: msg["revenue"] for msg in messages if msg["role"] == "tool"}
    return {"role": "assistant", "content": (
        f"Q1={values['Q1']}, Q2={values['Q2']}, Q3={values['Q3']} million_CNY; "
        f"Q2 QoQ={(values['Q2']/values['Q1']-1):.0%}, "
        f"Q3 QoQ={(values['Q3']/values['Q2']-1):.0%}; "
        "sources: Q1/Q2/Q3-report/table-A (fictional)."
    )}


def execute(call: dict) -> dict:
    if call["name"] not in ALLOWED:
        return {"role": "tool", "ok": False, "error": "permission_denied"}
    quarter = call["arguments"].get("quarter")
    if quarter not in REPORTS:
        return {"role": "tool", "ok": False, "error": "not_found", "quarter": quarter}
    return {"role": "tool", "ok": True, "call_id": call["id"],
            "quarter": quarter, "revenue": REPORTS[quarter],
            "unit": "million_CNY", "source": f"{quarter}-report/table-A"}


def run(max_steps: int = 4) -> list[dict]:
    messages = [
        {"role": "system", "content": "Only authorized reports; cite sources."},
        {"role": "user", "content": "Compare revenue of Q1-Q3."},
    ]
    for _ in range(max_steps):
        answer = choose_next(messages)
        messages.append(answer)
        if not answer.get("tool_calls"):
            return messages
        for call in answer["tool_calls"]:
            result = execute(call)
            messages.append(result)
            if not result.get("ok"):
                return messages  # Do not invent an answer after a tool error.
    raise RuntimeError("step_budget_exceeded")


if __name__ == "__main__":
    history = run()
    assert len(history) == 9  # system, user, three calls/results, final assistant
    assert "Q2 QoQ=20%" in history[-1]["content"]
    assert "Q3 QoQ=10%" in history[-1]["content"]
    for item in history:
        print(item)
