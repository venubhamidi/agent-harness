# Computation is done in code and SQL; models only interpret
**Status:** accepted
**Date:** 2026-11-10

## Context
Dashboards show counts, flags and scores; agents explain them. If a model computed any of these,
two screens could disagree, a count could depend on the page that was loaded, and a wrong number
would be plausible rather than detectably wrong.

## Decision
Business rules are functions and SQL predicates defined once in the application package
(`rules.py` in the example) and used by the API, the MCP tools and the agents. Summary counts
are computed in SQL over the whole table. An agent computes its facts with those rule functions
and passes them to the model as data; the model returns words in a validated schema. A model
never applies a rule, never queries the database, and its output never changes stored data.

## Alternatives considered
- **Let the model reason over raw records and report flags.** Reads naturally but is not
  repeatable, cannot be unit-tested, and drifts from the dashboard.
- **Compute in the browser from the loaded page.** Wrong beyond one page; the Command Center's
  first dashboard did this and was corrected (its `DECISIONS.md` D-023).
- **Rules in both the API and the agent, written separately.** Two copies disagree eventually.

## Consequences
- A test can assert that the API's flags and the agent's flags for the same record are equal.
- Evaluation suites on a mock model check the deterministic half of an agent fully.
- Adding a rule means one function and one SQL predicate, then the model's wording follows.
