# Example application — rules for Claude Code

This is the template's placeholder application: a small registry of work items. It exists to
show each harness pattern once. Replace it with your application and rewrite this file.

## What is here
```
app/config.py                 settings, development tokens, the role table
app/migrations/001_items.sql  the one table
app/rules.py                  business rules, defined once (used by the API and the agent)
app/api.py                    list / summary / detail, run the agent, open a ticket
app/mcp_servers/items_mcp/    read-only tool server for agents
app/agents/review_agent.py    the example agent (structured output, untrusted data)
app/evals/                    evaluation cases and fixture records for the agent
app/plugins/                  where this application's own plugins go (empty)
app/seed.py                   sample rows
```

## Domain rules (each has a test in tests/test_app.py)
1. An item with no owner is flagged `no_owner`; priority `unknown` is flagged `priority_unknown`.
   `unknown` is never treated as `low`.
2. The API and the agent use the same rule functions in `app/rules.py`.
3. Summary counts come from `/api/v1/items/summary`.
4. Only a person with `tickets:create` can open a ticket; the agent cannot.

## When you turn this into a real application
1. `python scripts/rename_app.py <name>`
2. Replace the migration, rules, API, tools, agent, evals and front end with your own.
3. Rewrite this file and start `DECISIONS.md` with your open questions.
