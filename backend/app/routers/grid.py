from fastapi import APIRouter, Query
from backend.app.services.osm_service import fetch_parks
from backend.app.services.grid_service import add_nearest_park_distance
from backend.app.core.config import settings
from backend.app.services.grid_service import add_park_score
from backend.app.services.grid_service import summarize_park_metrics
from backend.app.services.grid_service import get_worst_cells
from backend.app.services.grid_service import recommend_new_parks
from backend.app.services.osm_service import fetch_metro
from backend.app.services.grid_service import add_nearest_metro_distance
from backend.app.services.grid_service import add_metro_score
from backend.app.services.grid_service import add_urban_score
from backend.app.services.grid_service import (
    bbox_to_h3_cells,
    h3_cells_to_feature_collection,
)

router = APIRouter(tags=["grid"])


@router.get("/grid")
def get_grid(
    full: bool = Query(False, description="If true, return full GeoJSON FeatureCollection"),
    limit: int = Query(0, ge=0, le=20000, description="If >0, limit number of cells returned"),
    top_k: int = Query(3, ge=1, le=20, description="Number of park recommendations"),
) -> dict:
    cells = bbox_to_h3_cells(settings.ankara_bbox, settings.default_h3_res)

    if limit > 0:
        cells = cells[:limit]

    fc = h3_cells_to_feature_collection(cells)

    parks = fetch_parks()

    fc = add_nearest_park_distance(fc, parks)
    fc = add_park_score(fc)
    metro = fetch_metro()
    fc = add_nearest_metro_distance(fc, metro)
    fc = add_metro_score(fc)
    fc = add_urban_score(fc)

    if not full:
        summary = summarize_park_metrics(fc)
        worst_cells = get_worst_cells(fc)
        park_recommendations = recommend_new_parks(fc,top_k=top_k)
        return {
            "city": settings.default_city,
            "bbox": settings.ankara_bbox,
            "h3_res": settings.default_h3_res,
            "cell_count": len(cells),
            **summary,
            "worst_cells": worst_cells,
            "park_recommendations": park_recommendations,
        }

    return fc