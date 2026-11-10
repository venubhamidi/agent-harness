# Outside systems are reached through plugins chosen by a setting
**Status:** accepted
**Date:** 2026-11-10

## Context
Applications connect to identity providers, ticket systems, scanners, secret stores and model
providers. Which product fills each role is decided per deployment, often late, and often not
by the people writing the code. Tests must run offline.

## Decision
`harness/plugins/__init__.py` holds a registry of factories keyed by (kind, name). A setting per
kind (`APP_AUTH_PROVIDER`, `APP_LLM_PROVIDER`, `APP_SECRETS_PROVIDER`, `APP_TICKETING_PROVIDER`)
selects the name. Built-in plugins ship with the harness; an application adds its own in its
`plugins/` folder and lists the module in `APP_PLUGIN_MODULES`. An application may define new
kinds. Host names, credentials and model ids are settings or secrets, never code.

## Alternatives considered
- **Direct SDK calls from application code.** Fastest to write; swapping a system becomes a code
  change in every call site, and tests need the real thing or per-call mocks.
- **A dependency-injection framework.** More machinery than four kinds warrant.
- **One plugin per kind, hard-wired at import time.** Loses the per-deployment choice.

## Consequences
- Swapping an integration is a configuration change plus, at most, one new module.
- Every plugin has an offline stand-in (`static`, `mock`, `env`, `memory`) so tests and CI run
  without outside systems.
- A missing or misnamed plugin fails at start with the list of available names.
