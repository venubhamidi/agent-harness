# Agents get read-only tools; anything that changes data or an outside system is a human-called endpoint
**Status:** accepted
**Date:** 2026-11-10

## Context
Agents call a model, and a model can be steered by text it reads: tool results, documents, user
input. The injection scan in `harness/agents/guardrails.py` is a heuristic. Decisions that affect
a customer, a record of fact or an outside system need an accountable person.

## Decision
An agent's `AgentSpec.allowed_tools` lists only read-only MCP tools; a call to any other name is
refused and audited. Every agent response carries `confidence="advisory"`. Anything that writes
(for example opening a ticket) is an API endpoint a person calls, guarded by a permission in the
application's role table (`tickets:create` in the example). An agent has no such permission and
no code path to those endpoints.

## Alternatives considered
- **Agents with write tools behind an approval step.** Puts the irreversible action inside the
  agent loop, where a steered model and a bug look the same; the approval becomes a formality.
- **Trust the injection scan.** It catches patterns, not intent; it cannot be the control.
- **Human-in-the-loop checkpoints inside the agent.** Adds a state machine the applications so far
  do not need; the endpoint already is the checkpoint.

## Consequences
- The real protection against prompt injection is structural: a steered agent can read, not act.
- Writes are tested as endpoint behaviour (401, 403, 200), not as agent behaviour.
- A workflow that must act on an agent's recommendation is deterministic code or a person,
  never the agent.
