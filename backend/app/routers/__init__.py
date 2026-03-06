from backend.app.routers.health import router as health_router
from backend.app.routers.config import router as config_router
from backend.app.routers.grid import router as grid_router
from backend.app.routers.analyze import router as analyze_router
routers = [
    health_router,
    config_router,
    grid_router,
    analyze_router,
]