from fastapi import APIRouter, Query
from backend.app.services.osm_service import fetch_parks
from backend.app.services.grid_service import add_nearest_park_distance
from backend.app.core.config import settings
from backend.app.services.grid_service import add_park_score
from backend.app.services.grid_service import summarize_park_metrics

from backend.app.services.grid_service import (
    bbox_to_h3_cells,
    h3_cells_to_feature_collection,
)

router = APIRouter(tags=["grid"])


@router.get("/grid")
def get_grid(
    full: bool = Query(False, description="If true, return full GeoJSON FeatureCollection"),
    limit: int = Query(0, ge=0, le=20000, description="If >0, limit number of cells returned"),
) -> dict:
    cells = bbox_to_h3_cells(settings.ankara_bbox, settings.default_h3_res)

    if limit > 0:
        cells = cells[:limit]

    fc = h3_cells_to_feature_collection(cells)

    parks = fetch_parks()

    fc = add_nearest_park_distance(fc, parks)
    fc = add_park_score(fc)

    if not full:
        summary = summarize_park_metrics(fc)
        return {
            "city": settings.default_city,
            "bbox": settings.ankara_bbox,
            "h3_res": settings.default_h3_res,
            "cell_count": len(cells),
            **summary,
        }

    return fc