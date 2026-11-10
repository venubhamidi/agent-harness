# Applications take the harness by template copy; harness/ is read-only and checksum-verified
**Status:** accepted
**Date:** 2026-11-10

## Context
Every application needs the same foundation: login, permissions, audit, rate limiting, database
access, migrations, the agent contract, guardrails, evaluations, plugins and deployment. The
foundation must be the same in every application, and an application must not drift from it by
patching it locally. There was one real application when this was decided.

## Decision
A new application is created by copying this template repository. The foundation lives in
`harness/` with a `VERSION` and a `MANIFEST.sha256`; `scripts/harness_lock.py --check` fails CI
if any file in it differs from the manifest. Applications never edit `harness/`. Changes are made
in the template and arrive in an application through `scripts/update_harness.sh`, which replaces
the folder with a released version and reruns the checks.

## Alternatives considered
- **A versioned Python package** installed from an index. Cleaner upgrades, but it needs a
  package index, release tooling and a second repository to maintain before there are enough
  applications to justify them. Revisit when two or three real applications exist
  (recorded in the Command Center's `DECISIONS.md` as D-017).
- **A git submodule.** Keeps one source of truth but is awkward to review and easy to leave
  on a stale commit.
- **Copy without a lock.** Simplest, but nothing stops an application from editing the
  foundation and silently diverging.

## Consequences
- An application's `harness/` can be diffed byte for byte against the template's.
- Anything an application needs that the harness lacks is built in the application (a plugin,
  a helper, a subclass) or proposed for the template.
- `scripts/check_structure.py` and `scripts/harness_lock.py` are template-owned and copied to
  applications by the update script.
