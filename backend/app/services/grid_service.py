from __future__ import annotations
from typing import Any, Dict, List, Tuple
import h3
from shapely.geometry import Polygon, mapping
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

def bbox_to_h3_cells(
    bbox: Tuple[float, float, float, float],
    h3_res: int,
) -> List[str]:
    """
    bbox: (min_lon, min_lat, max_lon, max_lat)
    Returns a list of H3 cell ids covering the bbox.
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    # H3 expects (lat, lon) for LatLngPoly
    outer = [
        (min_lat, min_lon),
        (min_lat, max_lon),
        (max_lat, max_lon),
        (max_lat, min_lon),
        (min_lat, min_lon),
    ]

    poly = h3.LatLngPoly(outer)

    cells = h3.polygon_to_cells(poly, h3_res)
    return list(cells)

def h3_cells_to_feature_collection(cells: List[str]) -> Dict[str, Any]:
    """
    Converts H3 cell ids to a GeoJSON FeatureCollection.
    """
    features: List[Dict[str, Any]] = []

    for cell in cells:
        # h3 boundary returns list of (lat, lon) by default; we need (lon, lat)
        boundary = h3.cell_to_boundary(cell)  # returns [(lat, lon), ...]
        coords_lonlat = [[lon, lat] for (lat, lon) in boundary]
        coords_lonlat.append(coords_lonlat[0])
        poly = Polygon(coords_lonlat)

        features.append(
            {
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {
                    "h3": cell,
                    "score": None,
                    "d_park": None,
                    "d_metro": None,
                    "d_hospital": None
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}

def add_nearest_park_distance(
    feature_collection: Dict[str, Any],
    parks_gdf: Any,
) -> Dict[str, Any]:
    """
    For each hex feature, compute distance from hex centroid to nearest park geometry.
    Distance is in meters.
    """
    # Metric projection for Turkey/Ankara
    project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform

    # Park geometrilerini metrik sisteme çevir
    park_geoms = [transform(project, geom) for geom in parks_gdf.geometry if geom is not None]

    for feature in feature_collection["features"]:
        geom = shape(feature["geometry"])
        geom_m = transform(project, geom)
        centroid_m = geom_m.centroid

        min_distance = min(centroid_m.distance(park_geom) for park_geom in park_geoms)

        feature["properties"]["d_park"] = round(float(min_distance), 2)

    return feature_collection
def add_park_score(feature_collection, radius_m=800):

    for feature in feature_collection["features"]:

        d = feature["properties"].get("d_park")

        if d is None:
            continue

        score = 1 - (d / radius_m)
        score = max(0, min(1, score))
        score = round(score, 3)
        
        feature["properties"]["park_score"] = score
        feature["properties"]["score"] = score 
    return feature_collection

def summarize_park_metrics(feature_collection):
    distances = []
    scores = []

    for feature in feature_collection["features"]:
        props = feature["properties"]

        d_park = props.get("d_park")
        park_score = props.get("park_score")

        if d_park is not None:
            distances.append(d_park)

        if park_score is not None:
            scores.append(park_score)

    avg_d_park = round(sum(distances) / len(distances), 2) if distances else None
    avg_park_score = round(sum(scores) / len(scores), 3) if scores else None

    bad_access_cell_count = sum(
        1 for feature in feature_collection["features"]
        if (feature["properties"].get("park_score") or 0) == 0
    )

    return {
        "avg_d_park": avg_d_park,
        "avg_park_score": avg_park_score,
        "bad_access_cell_count": bad_access_cell_count,
    }