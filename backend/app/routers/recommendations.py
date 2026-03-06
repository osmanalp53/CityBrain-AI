from fastapi import APIRouter, Query

from backend.app.schemas.analyze import RecommendationsResponse
from backend.app.core.config import settings

from backend.app.services.osm_service import fetch_parks, fetch_metro, fetch_hospitals
from backend.app.services.grid_service import (
    bbox_to_h3_cells,
    h3_cells_to_feature_collection,
    add_nearest_park_distance,
    add_park_score,
    add_nearest_metro_distance,
    add_metro_score,
    add_nearest_hospital_distance,
    add_hospital_score,
    add_urban_score,
    recommend_new_parks,
)

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    top_k: int = Query(5, ge=1, le=50),
):
    cells = bbox_to_h3_cells(settings.ankara_bbox, settings.default_h3_res)

    fc = h3_cells_to_feature_collection(cells)

    parks = fetch_parks()
    fc = add_nearest_park_distance(fc, parks)
    fc = add_park_score(fc, radius_m=settings.default_radius_m)

    metro = fetch_metro()
    fc = add_nearest_metro_distance(fc, metro)
    fc = add_metro_score(fc, radius_m=settings.default_radius_m * 1.5)

    hospitals = fetch_hospitals()
    fc = add_nearest_hospital_distance(fc, hospitals)
    fc = add_hospital_score(fc, radius_m=settings.default_radius_m * 2)

    fc = add_urban_score(fc)

    recs = recommend_new_parks(fc, top_k=top_k)

    return {
        "recommendation_type": "park",
        "city": settings.default_city,
        "radius_m": settings.default_radius_m,
        "h3_res": settings.default_h3_res,
        "top_k": top_k,
        "items": recs,
    }