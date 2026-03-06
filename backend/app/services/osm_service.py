from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import osmnx as ox

from backend.app.core.config import settings

DATA_DIR = Path("data")
PARKS_SNAPSHOT = DATA_DIR / "parks.geojson"
METRO_SNAPSHOT = DATA_DIR / "metro.geojson"
HOSPITAL_SNAPSHOT = DATA_DIR / "hospital.geojson"


def fetch_parks() -> gpd.GeoDataFrame:
    """
    Returns parks as a GeoDataFrame.

    Strategy (product-grade):
    1) If data/parks.geojson exists -> read locally (fast, reliable).
    2) Else try to download from OSM (may be slow/unreliable).
       If download succeeds -> save snapshot for future runs.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if PARKS_SNAPSHOT.exists():
        gdf = gpd.read_file(PARKS_SNAPSHOT)
        if gdf.empty:
            raise ValueError("Park GeoJSON is empty.")
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)
        return gdf

    ox.settings.timeout = 180
    ox.settings.use_cache = True
    ox.settings.overpass_rate_limit = True

    tags = {"leisure": "park"}

    min_lon, min_lat, max_lon, max_lat = settings.ankara_bbox
    gdf = ox.features_from_bbox((max_lat, min_lat, max_lon, min_lon), tags=tags)
    gdf = gdf.reset_index()

    gdf.to_file(PARKS_SNAPSHOT, driver="GeoJSON")

    if gdf.empty:
        raise ValueError("Fetched park GeoDataFrame is empty.")
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    return gdf


def fetch_metro() -> gpd.GeoDataFrame:
    if not METRO_SNAPSHOT.exists():
        raise FileNotFoundError(
            "data/metro.geojson not found. Place metro station data under data/."
        )

    gdf = gpd.read_file(METRO_SNAPSHOT)

    if gdf.empty:
        raise ValueError("Metro GeoJSON is empty.")

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    return gdf


def fetch_hospitals() -> gpd.GeoDataFrame:
    if not HOSPITAL_SNAPSHOT.exists():
        raise FileNotFoundError(
            "data/hospital.geojson not found. Place hospital data under data/."
        )

    gdf = gpd.read_file(HOSPITAL_SNAPSHOT)

    if gdf.empty:
        raise ValueError("Hospital GeoJSON is empty.")

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    return gdf