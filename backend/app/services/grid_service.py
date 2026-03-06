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

def h3_cells_to_feature_collection(cells):

    features = []

    for h in cells:

        boundary = h3.cell_to_boundary(h)
        poly = Polygon([(lng, lat) for lat, lng in boundary])

        features.append(
            {
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {
                    "h3": h,
                    "score": None,
                    "d_park": None,
                    "d_metro": None,
                    "d_hospital": None,
                    "park_score": None,
                    "metro_score": None,
                    "hospital_score": None,
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }
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
def add_nearest_metro_distance(
    feature_collection: Dict[str, Any],
    metro_gdf: Any,
) -> Dict[str, Any]:
    """
    For each hex feature, compute distance from hex centroid to nearest metro geometry.
    Distance is in meters.
    """
    project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform

    metro_geoms = [transform(project, geom) for geom in metro_gdf.geometry if geom is not None]

    for feature in feature_collection["features"]:
        geom = shape(feature["geometry"])
        geom_m = transform(project, geom)
        centroid_m = geom_m.centroid

        min_distance = min(centroid_m.distance(metro_geom) for metro_geom in metro_geoms)

        feature["properties"]["d_metro"] = round(float(min_distance), 2)

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
def add_metro_score(feature_collection, radius_m=1200):

    for feature in feature_collection["features"]:

        d = feature["properties"].get("d_metro")

        if d is None:
            feature["properties"]["metro_score"] = None
            continue

        score = 1 - (d / radius_m)

        score = max(0.0, min(1.0, score))

        feature["properties"]["metro_score"] = round(score, 3)

    return feature_collection

def summarize_park_metrics(feature_collection):
    distances = []
    park_scores = []
    urban_scores = []

    for feature in feature_collection["features"]:
        props = feature["properties"]

        d_park = props.get("d_park")
        park_score = props.get("park_score")
        urban_score = props.get("score")

        if d_park is not None:
            distances.append(d_park)

        if park_score is not None:
            park_scores.append(park_score)

        if urban_score is not None:
            urban_scores.append(urban_score)

    avg_d_park = round(sum(distances) / len(distances), 2) if distances else None
    avg_park_score = round(sum(park_scores) / len(park_scores), 3) if park_scores else None
    avg_urban_score = round(sum(urban_scores) / len(urban_scores), 3) if urban_scores else None

    bad_access_cell_count = sum(
        1
        for feature in feature_collection["features"]
        if (feature["properties"].get("park_score") or 0) == 0
    )

    return {
        "avg_d_park": avg_d_park,
        "avg_park_score": avg_park_score,
        "avg_urban_score": avg_urban_score,
        "bad_access_cell_count": bad_access_cell_count,
    }
def get_worst_cells(feature_collection, top_k=10):

    features = feature_collection["features"]

    sorted_features = sorted(
        features,
        key=lambda f: f["properties"].get("score", 0)
    )

    worst = sorted_features[:top_k]

    return [
        {
            "h3": f["properties"]["h3"],
            "score": f["properties"]["score"],
            "park_score": f["properties"]["park_score"],
            "metro_score": f["properties"]["metro_score"],
            "d_park": f["properties"]["d_park"],
            "d_metro": f["properties"]["d_metro"],
        }
        for f in worst
    ]
def recommend_new_parks(feature_collection, top_k=3):
    features = feature_collection["features"]

    candidates = [
        f for f in features
        if (f["properties"].get("park_score") or 0) == 0
    ]

    ranked = sorted(
        candidates,
        key=lambda f: f["properties"].get("score", 1)
        
    )

    top = ranked[:top_k]

    recommendations = []

    for f in top:

        h3_id = f["properties"]["h3"]

        lat, lon = h3.cell_to_latlng(h3_id)

        recommendations.append(
            {
                "h3": h3_id,
                "lat": lat,
                "lon": lon,
                "d_park": f["properties"]["d_park"],
                "park_score": f["properties"]["park_score"],
                "reason": f"Nearest park is {round(f['properties']['d_park'], 1)} meters away. This area is a strong candidate for a new park."
            }
        )
    return recommendations    
def add_urban_score(feature_collection):

    for feature in feature_collection["features"]:
        props = feature["properties"]

        park_score = props.get("park_score")
        metro_score = props.get("metro_score")

        if park_score is None:
            park_score = 0.0

        if metro_score is None:
            metro_score = 0.0

        urban_score = (0.6 * park_score) + (0.4 * metro_score)

        props["score"] = round(urban_score, 3)

    return feature_collection