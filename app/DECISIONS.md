# Decision log

Questions the requirements leave open. Nothing listed as Open is guessed in code.

| ID | Status | Question | Current choice in code | Owner |
|----|--------|----------|------------------------|-------|
| D-001 | Open | Which identity provider, and which of its groups map to which application roles? | Development tokens; `APP_AUTH_PROVIDER=oidc` is ready to configure. | |
| D-002 | Open | Which model is approved, and may this application's data be sent to a hosted model? | Mock provider. No model id is configured. | |
| D-003 | Open | Which ticket system and which table or project? | In-memory ticketing. | |
