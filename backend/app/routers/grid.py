from fastapi import APIRouter, Query

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
    summarize_park_metrics,
    get_worst_cells,
    recommend_new_parks,
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

    hospitals = fetch_hospitals()
    fc = add_nearest_hospital_distance(fc, hospitals)
    fc = add_hospital_score(fc)

    fc = add_urban_score(fc)

    if not full:
        summary = summarize_park_metrics(fc)
        worst_cells = get_worst_cells(fc, top_k=top_k)
        park_recommendations = recommend_new_parks(fc, top_k=top_k)

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