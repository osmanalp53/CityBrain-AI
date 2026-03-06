from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import osmnx as ox

from backend.app.core.config import settings

DATA_DIR = Path("data")
PARKS_SNAPSHOT = DATA_DIR / "parks.geojson"


def fetch_parks() -> gpd.GeoDataFrame:
    """
    Returns parks as a GeoDataFrame.

    Strategy (product-grade):
    1) If data/parks.geojson exists -> read locally (fast, reliable).
    2) Else try to download from OSM (may be slow/unreliable).
       If download succeeds -> save snapshot for future runs.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Offline-first
    if PARKS_SNAPSHOT.exists():
        gdf = gpd.read_file(PARKS_SNAPSHOT)
        return gdf

    # 2) Online fetch (best effort)
    ox.settings.timeout = 180
    ox.settings.use_cache = True
    ox.settings.overpass_rate_limit = True

    tags = {"leisure": "park"}

    # Use bbox for now but with smaller area if needed
    min_lon, min_lat, max_lon, max_lat = settings.ankara_bbox

    # OSMnx bbox signature differs by version; this works in recent versions:
    gdf = ox.features_from_bbox((max_lat, min_lat, max_lon, min_lon), tags=tags)

    # Keep only geometries
    gdf = gdf.reset_index()

    # Save snapshot
    gdf.to_file(PARKS_SNAPSHOT, driver="GeoJSON")
    

    return gdf
METRO_SNAPSHOT = Path("data") / "metro.geojson"


def fetch_metro() -> gpd.GeoDataFrame:
    if not METRO_SNAPSHOT.exists():
        raise FileNotFoundError(
            "data/metro.geojson not found. Place metro station data under data/."
        )
    return gpd.read_file(METRO_SNAPSHOT)