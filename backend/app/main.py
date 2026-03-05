from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.routers import routers

app = FastAPI(title=settings.app_name, version="0.2.2")

for r in routers:
    app.include_router(r, prefix=settings.api_v1_prefix)