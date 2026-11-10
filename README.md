# agent-harness

A template for building web applications with AI agents. Every new application starts as a copy of
this repository and inherits login, permissions, audit, rate limiting, agent guardrails, retries,
evaluations, plugin integrations and container deployment from `harness/`.

It contains a small example application (`app/`, a registry of work items) that uses each of
those once. You replace the example; you do not edit `harness/`.

For a real application built on it, see [cyber-command-center](https://github.com/venubhamidi/cyber-command-center).

## Start a new application
1. Create a repository from this template (on GitHub: **Use this template**).
2. `python scripts/rename_app.py <name>` to rename `app/` to your application's name.
3. Replace the example's table, rules, API, tools, agent, evaluation cases and screen with your own.
4. Rewrite `<name>/CLAUDE.md` and `<name>/DECISIONS.md`.
5. Keep `python scripts/check_structure.py` and the tests passing. CI enforces both.

## Run it locally
Needs Python 3.12+, Node 22 and PostgreSQL 16.
```bash
sudo -u postgres scripts/dev_db.sh        # creates databases app and app_test
pip install -r requirements-dev.txt
python -m harness.migrate app && python -m app.seed
uvicorn app.main:app --reload             # API on http://localhost:8000/docs
cd frontend && npm install && npm run dev # screen on http://localhost:5173
```
Development tokens: `dev-editor-token`, `dev-viewer-token`, `dev-guest-token` (see `app/config.py`).

## Run it in containers
```bash
cp deploy/.env.example deploy/.env
docker compose -f deploy/docker-compose.yml up --build    # then open http://localhost:8080
docker compose -f deploy/docker-compose.yml exec api python -m app.seed
```

## Check it
```bash
python scripts/check_structure.py   # required files, unmodified harness, documented settings, evals exist
ruff check .
python -m pytest -q
python -m harness.evals app
```

## Going to production
The two images are what you deploy. Production differs from the compose file in configuration only:
- `APP_ENVIRONMENT=prod` and `APP_AUTH_PROVIDER=oidc` with your identity provider's settings
- `APP_DATABASE_URL` pointing at your managed PostgreSQL
- secrets from your secret store (`APP_SECRETS_PROVIDER=file` reads mounted secret files)
- `APP_LLM_PROVIDER` and `APP_LLM_MODEL` set to an approved model
- `APP_TICKETING_PROVIDER=servicenow` (or your own plugin) if the application opens tickets

## Upgrading the harness
`scripts/update_harness.sh https://github.com/venubhamidi/agent-harness.git <tag>` replaces `harness/` with a released version
and runs the checks. Read `harness/CHANGELOG.md` first.

## What has and has not been proven
Everything in `harness/` is covered by tests that run offline. Not yet exercised against the real
thing: a model provider, a ServiceNow instance, an identity provider, and the container images
(they are built and started for the first time by the CI workflow). See `harness/README.md`.
