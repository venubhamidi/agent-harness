# Example application — rules for Claude Code

The template's placeholder application: a small registry of work items, showing each harness
pattern once. Replace it with your application and rewrite this file.
Terms, glossary: `app/CONTEXT.md`. Open questions: `app/DECISIONS.md`.

## Domain rules (each names its test in `tests/test_app.py`)
1. **Flag an item with no owner as `no_owner`, and priority `unknown` as `priority_unknown`.**
   Treat `unknown` as unknown, never as `low`. (`test_flags_are_the_same_in_api_and_agent`)
2. **Apply the same rule functions, `app/rules.py`, from the API and the agent.**
   (`test_flags_are_the_same_in_api_and_agent`)
3. **Take summary counts from `/api/v1/items/summary`**, computed over the whole table.
   (`test_summary_counts_all_items_not_one_page`)
4. **Only a person with `tickets:create` opens a ticket; the agent cannot.**
   (`test_ticket_is_opened_by_a_person_through_the_ticketing_plugin`)

## Traps
- The tests assert the counts in `app/seed.py`; change the seed and the expected numbers move.
- The evaluation suite runs on `app/evals/fixtures.json`, not on the database; keep the fixtures
  in step with the schema.

## When you turn this into a real application
1. `python scripts/rename_app.py <name>`
2. `/grill` the open questions in `DECISIONS.md`, then `/slice` the first feature.
3. Replace the migration, rules, API, tools, agent, evals, glossary and front end with your own.
4. Rewrite this file, `<name>/CONTEXT.md` and `<name>/DECISIONS.md`.
