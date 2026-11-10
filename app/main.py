from app.api import router
from app.config import ROLE_PERMISSIONS, settings
from harness.app import create_app

app = create_app(title="Example application", version="0.1.0", settings=settings,
                 role_permissions=ROLE_PERMISSIONS, routers=[router])
