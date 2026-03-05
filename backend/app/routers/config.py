from fastapi import APIRouter

from backend.app.core.config import settings

router = APIRouter(tags=["config"])


@router.get("/config")
def get_config() -> dict:
    return {
        "default_city": settings.default_city,
        "default_radius_m": settings.default_radius_m,
        "default_h3_res": settings.default_h3_res,
    }