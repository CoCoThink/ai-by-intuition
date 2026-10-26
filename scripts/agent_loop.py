#!/usr/bin/env python3
"""Deterministic teaching-only Agent loop: mock decisions and mock report tools.

No network, LLM API, file access or credentials. Run: python3 scripts/agent_loop.py
"""
from __future__ import annotations

REPORTS = {"Q1": 100, "Q2": 120, "Q3": 132}
ALLOWED = {"read_report"}
# Teaching-only message sizes (not tied to any tokenizer): system+user, request, result.
PROMPT_TOKENS, CALL_TOKENS, RESULT_TOKENS = 80, 20, 40


def input_tokens_per_call(history: list[dict]) -> list[int]:
    """Each model call re-reads every earlier message (stateless request)."""
    sizes, total = [], PROMPT_TOKENS
    for message in history[2:]:
        if message["role"] == "assistant":
            sizes.append(total)
            total += CALL_TOKENS * len(message.get("tool_calls", []))
        else:
            total += RESULT_TOKENS
    return sizes


def resent_history_tokens(rounds: int, per_round: int, window: int | None = None) -> int:
    """Total input when round t resends the last `window` rounds (all if None)."""
    return sum(per_round * (t if window is None else min(t, window))
               for t in range(1, rounds + 1))


def format_answer(values: dict) -> str:
    return (
        f"Q1={values['Q1']}, Q2={values['Q2']}, Q3={values['Q3']} million_CNY; "
        f"Q2 QoQ={(values['Q2']/values['Q1']-1):.0%}, "
        f"Q3 QoQ={(values['Q3']/values['Q2']-1):.0%}; "
        "sources: Q1/Q2/Q3-report/table-A (fictional)."
    )


def choose_next(messages: list[dict], allowed_tools=ALLOWED) -> dict:
    """Mock model policy, not a real model or a recommendation for production."""
    seen = {msg["quarter"] for msg in messages if msg["role"] == "tool" and msg.get("ok")}
    for quarter in REPORTS:
        if quarter not in seen:
            return {"role": "assistant", "tool_calls": [
                {"id": f"call-{quarter}", "name": "read_report", "arguments": {"quarter": quarter}}
            ]}
    values = {msg["quarter"]: msg["revenue"] for msg in messages if msg["role"] == "tool"}
    return {"role": "assistant", "content": format_answer(values)}


def is_authorized(call: dict) -> bool:
    return (call.get("name") in ALLOWED
            and call.get("arguments", {}).get("quarter") in REPORTS)


def execute(call: dict) -> dict:
    if call["name"] not in ALLOWED:
        return {"role": "tool", "ok": False, "error": "permission_denied"}
    quarter = call["arguments"].get("quarter")
    if quarter not in REPORTS:
        return {"role": "tool", "ok": False, "error": "not_found", "quarter": quarter}
    return {"role": "tool", "ok": True, "call_id": call["id"],
            "quarter": quarter, "revenue": REPORTS[quarter],
            "unit": "million_CNY", "source": f"{quarter}-report/table-A"}


def tool_message(call_id: str, result: dict) -> dict:
    return {**result, "role": "tool", "call_id": call_id}


def execute_with_limits(call: dict) -> dict:
    """Mock tool boundary; real adapters also enforce time and resource limits."""
    try:
        return execute(call)
    except (OSError, TimeoutError) as exc:
        return {"ok": False, "error": type(exc).__name__}


def app_finish(reason: str, messages: list[dict]) -> dict:
    """Application review against this fixed fixture; no additional model call.

    Exact text comparison is adequate for the deterministic mock, not a general
    natural-language verifier. Evidence must have the expected units and sources.
    """
    evidence = {msg["quarter"]: msg["revenue"] for msg in messages
                if msg["role"] == "tool" and msg.get("ok")
                and msg.get("quarter") in REPORTS
                and msg.get("unit") == "million_CNY"
                and msg.get("source") == f"{msg['quarter']}-report/table-A"
                and msg.get("revenue") == REPORTS[msg["quarter"]]}
    missing = [quarter for quarter in REPORTS if quarter not in evidence]
    complete = (reason == "answer" and not missing
                and messages[-1].get("content") == format_answer(evidence))
    return {"status": "complete" if complete else "incomplete", "reason": reason,
            "missing_quarters": missing, "messages": messages}


def run(max_steps: int = 4, *, model=choose_next,
        authorizer=is_authorized, executor=execute_with_limits) -> dict:
    messages = [
        {"role": "system", "content": "Only authorized reports; cite sources."},
        {"role": "user", "content": "Compare revenue of Q1-Q3."},
    ]
    for _ in range(max_steps):
        answer = model(messages, ALLOWED)
        messages.append(answer)
        if not answer.get("tool_calls"):
            return app_finish("answer", messages)
        for call in answer["tool_calls"]:
            if not authorizer(call):
                result = {"ok": False, "error": "permission_denied"}
            else:
                result = executor(call)
            messages.append(tool_message(call["id"], result))
            if not result["ok"]:
                return app_finish("tool_error", messages)
    return app_finish("step_budget_exceeded", messages)


if __name__ == "__main__":
    outcome = run()
    assert outcome["status"] == "complete"
    history = outcome["messages"]
    assert len(history) == 9  # system, user, three calls/results, final assistant
    assert "Q2 QoQ=20%" in history[-1]["content"]
    assert "Q3 QoQ=10%" in history[-1]["content"]
    calls = input_tokens_per_call(history)
    assert calls == [80, 140, 200, 260] and sum(calls) == 680
    batched = PROMPT_TOKENS + (PROMPT_TOKENS + 3 * CALL_TOKENS + 3 * RESULT_TOKENS)
    assert batched == 340
    denied = run(authorizer=lambda call: is_authorized(call)
                 and call["arguments"]["quarter"] != "Q2")
    assert denied["reason"] == "tool_error"
    assert denied["missing_quarters"] == ["Q2", "Q3"]
    assert input_tokens_per_call(denied["messages"]) == [80, 140]
    # Self-check: four quarters read one by one, then a final answer (5 calls).
    assert sum(PROMPT_TOKENS + (CALL_TOKENS + RESULT_TOKENS) * j for j in range(5)) == 1000
    assert resent_history_tokens(10, 200) == 200 * 55 == 11000
    assert resent_history_tokens(10, 200, window=3) == 5400
    print("input tokens per model call:", calls, "total:", sum(calls), "batched:", batched)
    print("10 rounds x 200 new tokens, full resend:", resent_history_tokens(10, 200),
          "last-3-rounds window:", resent_history_tokens(10, 200, window=3))
    for item in history:
        print(item)
