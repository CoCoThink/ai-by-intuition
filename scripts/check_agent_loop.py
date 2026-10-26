#!/usr/bin/env python3
"""Execute the printed Agent pseudocode and compare its stopping branches.

Regression: the book previously continued after a denied Q2 tool result while
the runnable example stopped after two model calls. All tools here are mocks.
"""
from pathlib import Path
import re
import textwrap

import agent_loop as agent

ROOT = Path(__file__).resolve().parents[1]


def printed_loop(max_steps=4, *, model=agent.choose_next,
                 authorizer=agent.is_authorized, executor=agent.execute_with_limits):
    source = (ROOT / "book/chapters/23d-agent-tools.tex").read_text()
    blocks = re.findall(r"\\begin\{Verbatim\}(?:\[[^\]]*\])?\s*\n(.*?)\\end\{Verbatim\}",
                        source, re.S)
    bodies = [block for block in blocks
              if block.startswith("messages = [system_message, user_message]")]
    assert len(bodies) == 1, "Expected one printed Agent loop"
    namespace = {
        "system_message": {"role": "system", "content": "Only authorized reports; cite sources."},
        "user_message": {"role": "user", "content": "Compare revenue of Q1-Q3."},
        "MAX_STEPS": max_steps, "model": model, "allowed_tools": agent.ALLOWED,
        "is_authorized": authorizer, "execute_with_limits": executor,
        "tool_message": agent.tool_message, "app_finish": agent.app_finish,
    }
    exec(compile("def printed():\n" + textwrap.indent(bodies[0], "    "),
                 "book Agent pseudocode", "exec"), namespace)
    return namespace["printed"]()


def run_checks():
    denied = lambda call: (agent.is_authorized(call)
                           and call["arguments"]["quarter"] != "Q2")

    def failed_tool(call):
        if call["arguments"]["quarter"] == "Q2":
            return {"ok": False, "error": "timeout"}
        return agent.execute(call)

    def direct_answer(messages, allowed_tools):
        return {"role": "assistant", "content": "Q2 QoQ=20%, Q3 QoQ=10%"}

    def wrong_answer(messages, allowed_tools):
        answer = agent.choose_next(messages, allowed_tools)
        if not answer.get("tool_calls"):
            answer["content"] = answer["content"].replace("20%", "200%")
        return answer

    cases = [
        ({}, "complete", "answer", [], [80, 140, 200, 260]),
        ({"authorizer": denied}, "incomplete", "tool_error", ["Q2", "Q3"], [80, 140]),
        ({"executor": failed_tool}, "incomplete", "tool_error", ["Q2", "Q3"], [80, 140]),
        ({"model": direct_answer}, "incomplete", "answer", ["Q1", "Q2", "Q3"], [80]),
        ({"model": wrong_answer}, "incomplete", "answer", [], [80, 140, 200, 260]),
        ({"max_steps": 2}, "incomplete", "step_budget_exceeded", ["Q3"], [80, 140]),
        ({"max_steps": 3}, "incomplete", "step_budget_exceeded", [], [80, 140, 200]),
        ({"max_steps": 0}, "incomplete", "step_budget_exceeded", ["Q1", "Q2", "Q3"], []),
    ]
    for kwargs, status, reason, missing, costs in cases:
        printed, runnable = printed_loop(**kwargs), agent.run(**kwargs)
        assert printed == runnable, (kwargs, printed, runnable)
        assert (printed["status"], printed["reason"], printed["missing_quarters"]) == (
            status, reason, missing), (kwargs, printed)
        assert agent.input_tokens_per_call(printed["messages"]) == costs
        if reason == "tool_error":
            assert printed["messages"][-1]["role"] == "tool"
            assert not any(msg.get("quarter") == "Q3" for msg in printed["messages"])
    print("Agent loop QA: printed/runnable normal, denied, failed, direct-answer, invalid-answer and budget branches agree")


if __name__ == "__main__":
    run_checks()
