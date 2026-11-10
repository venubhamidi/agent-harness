"""Example application settings and roles. Replace with your application's."""
from __future__ import annotations

from pathlib import Path

from harness.config import HarnessSettings

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


class Settings(HarnessSettings):
    # Development tokens. Ignored with single sign-on; refused outright when APP_ENVIRONMENT=prod.
    api_tokens: dict[str, tuple[str, str]] = {
        "dev-editor-token": ("editor@example.com", "editor"),
        "dev-viewer-token": ("viewer@example.com", "viewer"),
        "dev-guest-token": ("guest@example.com", "guest"),
    }


settings = Settings()

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "viewer": {"items:read"},
    "editor": {"items:read", "agents:run", "tickets:create"},
    "guest": set(),
    "admin": {"*"},
}
