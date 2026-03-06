from __future__ import annotations

from typing import Any, Dict, List, Tuple
import copy

import geopandas as gpd
import h3
import pyproj
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import transform


def bbox_to_h3_cells(
    bbox: Tuple[float, float, float, float],
    h3_res: int,
) -> List[str]:
    """
    bbox: (min_lon, min_lat, max_lon, max_lat)
    Returns a list of H3 cell ids covering the bbox.
    """
    min_lon, min_lat, max_lon, max_lat = bbox

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
    project = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:3857", always_xy=True
    ).transform

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
    project = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:3857", always_xy=True
    ).transform

    metro_geoms = [transform(project, geom) for geom in metro_gdf.geometry if geom is not None]

    for feature in feature_collection["features"]:
        geom = shape(feature["geometry"])
        geom_m = transform(project, geom)
        centroid_m = geom_m.centroid

        min_distance = min(centroid_m.distance(metro_geom) for metro_geom in metro_geoms)
        feature["properties"]["d_metro"] = round(float(min_distance), 2)

    return feature_collection


def add_nearest_hospital_distance(
    feature_collection: dict,
    hospitals_gdf: gpd.GeoDataFrame,
) -> dict:
    fc = copy.deepcopy(feature_collection)

    if hospitals_gdf.empty:
        for feature in fc["features"]:
            feature["properties"]["d_hospital"] = None
        return fc

    hospitals_metric = hospitals_gdf.to_crs(epsg=3857)
    hospital_union = hospitals_metric.unary_union

    for feature in fc["features"]:
        geom = shape(feature["geometry"])
        centroid = geom.centroid

        centroid_gdf = gpd.GeoDataFrame(
            geometry=[centroid],
            crs="EPSG:4326",
        ).to_crs(epsg=3857)

        centroid_metric = centroid_gdf.geometry.iloc[0]
        distance_m = centroid_metric.distance(hospital_union)

        feature["properties"]["d_hospital"] = round(float(distance_m), 2)

    return fc


def add_park_score(feature_collection, radius_m=800):
    for feature in feature_collection["features"]:
        d = feature["properties"].get("d_park")

        if d is None:
            continue

        score = 1 - (d / radius_m)
        score = max(0, min(1, score))
        score = round(score, 3)

        feature["properties"]["park_score"] = score

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


def add_hospital_score(feature_collection: dict, radius_m: int = 1500) -> dict:
    fc = copy.deepcopy(feature_collection)

    for feature in fc["features"]:
        props = feature["properties"]
        d_hospital = props.get("d_hospital")

        if d_hospital is None:
            props["hospital_score"] = None
            continue

        score = max(0.0, 1.0 - (float(d_hospital) / float(radius_m)))
        props["hospital_score"] = round(score, 4)

    return fc


def add_urban_score(feature_collection):
    for feature in feature_collection["features"]:
        props = feature["properties"]

        park_score = props.get("park_score")
        metro_score = props.get("metro_score")
        hospital_score = props.get("hospital_score")

        if park_score is None:
            park_score = 0.0
        if metro_score is None:
            metro_score = 0.0
        if hospital_score is None:
            hospital_score = 0.0

        urban_score = (
            (0.40 * park_score)
            + (0.35 * metro_score)
            + (0.25 * hospital_score)
        )

        props["score"] = round(urban_score, 4)

    return feature_collection


def summarize_park_metrics(feature_collection):
    d_park_values = []
    d_metro_values = []
    d_hospital_values = []

    park_scores = []
    metro_scores = []
    hospital_scores = []
    urban_scores = []

    for feature in feature_collection["features"]:
        props = feature["properties"]

        d_park = props.get("d_park")
        d_metro = props.get("d_metro")
        d_hospital = props.get("d_hospital")

        park_score = props.get("park_score")
        metro_score = props.get("metro_score")
        hospital_score = props.get("hospital_score")
        urban_score = props.get("score")

        if d_park is not None:
            d_park_values.append(d_park)
        if d_metro is not None:
            d_metro_values.append(d_metro)
        if d_hospital is not None:
            d_hospital_values.append(d_hospital)

        if park_score is not None:
            park_scores.append(park_score)
        if metro_score is not None:
            metro_scores.append(metro_score)
        if hospital_score is not None:
            hospital_scores.append(hospital_score)
        if urban_score is not None:
            urban_scores.append(urban_score)

    avg_d_park = round(sum(d_park_values) / len(d_park_values), 2) if d_park_values else None
    avg_d_metro = round(sum(d_metro_values) / len(d_metro_values), 2) if d_metro_values else None
    avg_d_hospital = round(sum(d_hospital_values) / len(d_hospital_values), 2) if d_hospital_values else None

    avg_park_score = round(sum(park_scores) / len(park_scores), 3) if park_scores else None
    avg_metro_score = round(sum(metro_scores) / len(metro_scores), 3) if metro_scores else None
    avg_hospital_score = round(sum(hospital_scores) / len(hospital_scores), 3) if hospital_scores else None
    avg_urban_score = round(sum(urban_scores) / len(urban_scores), 3) if urban_scores else None

    bad_access_cell_count = sum(
        1
        for feature in feature_collection["features"]
        if (feature["properties"].get("score") or 0) == 0
    )

    return {
        "avg_d_park": avg_d_park,
        "avg_d_metro": avg_d_metro,
        "avg_d_hospital": avg_d_hospital,
        "avg_park_score": avg_park_score,
        "avg_metro_score": avg_metro_score,
        "avg_hospital_score": avg_hospital_score,
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
            "hospital_score": f["properties"].get("hospital_score"),
            "d_park": f["properties"]["d_park"],
            "d_metro": f["properties"]["d_metro"],
            "d_hospital": f["properties"].get("d_hospital"),
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
        props = f["properties"]
        h3_id = props["h3"]
        lat, lon = h3.cell_to_latlng(h3_id)

        reason = (
            f"Low urban score area. "
            f"Nearest park {props.get('d_park')} m, "
            f"metro {props.get('d_metro')} m, "
            f"hospital {props.get('d_hospital')} m."
        )

        recommendations.append(
            {
                "h3": h3_id,
                "lat": lat,
                "lon": lon,
                "score": props.get("score"),
                "d_park": props.get("d_park"),
                "d_metro": props.get("d_metro"),
                "d_hospital": props.get("d_hospital"),
                "park_score": props.get("park_score"),
                "metro_score": props.get("metro_score"),
                "hospital_score": props.get("hospital_score"),
                "reason": reason,
            }
        )

    return recommendations