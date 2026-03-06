from fastapi import APIRouter

from backend.app.schemas.analyze import AnalyzeRequest
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

router = APIRouter(tags=["analyze"])


@router.post("/analyze")
def analyze_city(req: AnalyzeRequest):

    cells = bbox_to_h3_cells(settings.ankara_bbox, req.h3_res)

    fc = h3_cells_to_feature_collection(cells)

    parks = fetch_parks()
    fc = add_nearest_park_distance(fc, parks)
    fc = add_park_score(fc,radius_m=req.radius_m)

    metro = fetch_metro()
    fc = add_nearest_metro_distance(fc, metro)
    fc = add_metro_score(fc,radius_m=req.radius_m * 1.5)

    hospitals = fetch_hospitals()
    fc = add_nearest_hospital_distance(fc, hospitals)
    fc = add_hospital_score(fc,radius_m=req.radius_m * 2)

    fc = add_urban_score(fc)

    summary = summarize_park_metrics(fc)
    worst_cells = get_worst_cells(fc)
    recommendations = recommend_new_parks(fc)

    return {
        "city": req.city,
        "radius_m": req.radius_m,
        "h3_res": req.h3_res,
        "cell_count": len(cells),
        **summary,
        "worst_cells": worst_cells,
        "park_recommendations": recommendations,
    }