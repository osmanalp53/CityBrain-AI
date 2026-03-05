from backend.app.routers.health import router as health_router
from backend.app.routers.config import router as config_router

routers = [
    health_router,
    config_router,
]