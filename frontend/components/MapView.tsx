"use client";

import { useEffect, useRef, useState } from "react";
import Map, {
    Source,
    Layer,
    type LayerProps,
    type MapRef,
} from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

const hexLayer: LayerProps = {
    id: "hex-fill",
    type: "fill",
    paint: {
        "fill-color": [
            "interpolate",
            ["linear"],
            ["coalesce", ["get", "score"], 0],
            0, "#b91c1c",
            0.25, "#f97316",
            0.5, "#facc15",
            0.75, "#84cc16",
            1, "#15803d",
        ] as any,
        "fill-opacity": 0.6,
    },
};

const hexOutlineLayer: LayerProps = {
    id: "hex-outline",
    type: "line",
    paint: {
        "line-color": "#334155",
        "line-width": 1,
    },
};

const selectedHexOutlineLayer: LayerProps = {
    id: "selected-hex-outline",
    type: "line",
    paint: {
        "line-color": "#111827",
        "line-width": 3,
    },
};

function getGeoJSONBounds(
    geojson: any
): [[number, number], [number, number]] | null {
    if (!geojson?.features?.length) return null;

    let minLng = Infinity;
    let minLat = Infinity;
    let maxLng = -Infinity;
    let maxLat = -Infinity;

    for (const feature of geojson.features) {
        const coords = feature?.geometry?.coordinates;
        if (!coords) continue;

        const ring = coords[0];
        if (!Array.isArray(ring)) continue;

        for (const point of ring) {
            const [lng, lat] = point;
            if (lng < minLng) minLng = lng;
            if (lat < minLat) minLat = lat;
            if (lng > maxLng) maxLng = lng;
            if (lat > maxLat) maxLat = lat;
        }
    }

    if (
        minLng === Infinity ||
        minLat === Infinity ||
        maxLng === -Infinity ||
        maxLat === -Infinity
    ) {
        return null;
    }

    return [
        [minLng, minLat],
        [maxLng, maxLat],
    ];
}

export default function MapView() {
    const [geojson, setGeojson] = useState<any>(null);
    const [error, setError] = useState<string>("");
    const [hoverInfo, setHoverInfo] = useState<any>(null);
    const [selectedHex, setSelectedHex] = useState<any>(null);
    const mapRef = useRef<MapRef | null>(null);

    useEffect(() => {
        fetch("/api/grid")
            .then((res) => {
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }
                return res.json();
            })
            .then((data) => {
                console.log("GRID OK:", data);
                console.log("FEATURE COUNT:", data?.features?.length);
                setGeojson(data);

                const bounds = getGeoJSONBounds(data);
                if (bounds && mapRef.current) {
                    mapRef.current.fitBounds(bounds, {
                        padding: 60,
                        duration: 1000,
                    });
                }
            })
            .catch((err) => {
                console.error("Grid fetch error:", err);
                setError(String(err));
            });
    }, []);

    return (
        <div className="w-full h-[600px] rounded-lg overflow-hidden border bg-white relative">
            <Map
                ref={mapRef}
                initialViewState={{
                    longitude: 32.78,
                    latitude: 39.9,
                    zoom: 13,
                }}
                style={{ width: "100%", height: "100%" }}
                mapStyle="https://demotiles.maplibre.org/style.json"
                interactiveLayerIds={["hex-fill"]}
                onMouseMove={(e) => {
                    const feature = e.features?.[0];
                    if (feature) {
                        setHoverInfo({
                            x: e.point.x,
                            y: e.point.y,
                            properties: feature.properties,
                        });
                    } else {
                        setHoverInfo(null);
                    }
                }}
                onMouseLeave={() => setHoverInfo(null)}
                onClick={(e) => {
                    const feature = e.features?.[0];
                    if (feature) {
                        setSelectedHex(feature);
                    } else {
                        setSelectedHex(null);
                    }
                }}
            >
                {geojson && (
                    <Source id="hex-data" type="geojson" data={geojson}>
                        <Layer {...hexLayer} />
                        <Layer {...hexOutlineLayer} />
                    </Source>
                )}

                {selectedHex && (
                    <Source
                        id="selected-hex-data"
                        type="geojson"
                        data={{
                            type: "FeatureCollection",
                            features: [selectedHex],
                        }}
                    >
                        <Layer {...selectedHexOutlineLayer} />
                    </Source>
                )}
            </Map>

            <div className="absolute top-3 left-3 bg-white/90 px-3 py-2 rounded shadow text-sm z-10">
                {error
                    ? `Hata: ${error}`
                    : geojson
                        ? `Hex sayısı: ${geojson?.features?.length ?? 0}`
                        : "Yükleniyor..."}
            </div>

            {hoverInfo && (
                <div
                    className="absolute bg-white/95 shadow-lg px-3 py-2 rounded text-xs border"
                    style={{
                        left: hoverInfo.x + 10,
                        top: hoverInfo.y + 10,
                        pointerEvents: "none",
                        zIndex: 10,
                    }}
                >
                    <div>
                        <b>Urban Score:</b>{" "}
                        {hoverInfo.properties?.score != null
                            ? Number(hoverInfo.properties.score).toFixed(2)
                            : "-"}
                    </div>
                    <div>
                        <b>Park Distance:</b>{" "}
                        {hoverInfo.properties?.d_park != null
                            ? `${Number(hoverInfo.properties.d_park).toFixed(0)} m`
                            : "-"}
                    </div>
                    <div>
                        <b>Metro Distance:</b>{" "}
                        {hoverInfo.properties?.d_metro != null
                            ? `${Number(hoverInfo.properties.d_metro).toFixed(0)} m`
                            : "-"}
                    </div>
                    <div>
                        <b>Park Score:</b>{" "}
                        {hoverInfo.properties?.park_score != null
                            ? Number(hoverInfo.properties.park_score).toFixed(2)
                            : "-"}
                    </div>
                    <div>
                        <b>Metro Score:</b>{" "}
                        {hoverInfo.properties?.metro_score != null
                            ? Number(hoverInfo.properties.metro_score).toFixed(2)
                            : "-"}
                    </div>
                </div>
            )}

            {selectedHex && (
                <div className="absolute top-3 right-3 bg-white/95 shadow-lg px-4 py-3 rounded border text-sm z-10">
                    <div className="font-semibold mb-2">Selected Hex</div>
                    <div>
                        <b>H3:</b> {selectedHex.properties?.h3 ?? "-"}
                    </div>
                    <div>
                        <b>Urban Score:</b>{" "}
                        {selectedHex.properties?.score != null
                            ? Number(selectedHex.properties.score).toFixed(2)
                            : "-"}
                    </div>
                    <div>
                        <b>Park Distance:</b>{" "}
                        {selectedHex.properties?.d_park != null
                            ? `${Number(selectedHex.properties.d_park).toFixed(0)} m`
                            : "-"}
                    </div>
                    <div>
                        <b>Metro Distance:</b>{" "}
                        {selectedHex.properties?.d_metro != null
                            ? `${Number(selectedHex.properties.d_metro).toFixed(0)} m`
                            : "-"}
                    </div>
                    <div>
                        <b>Park Score:</b>{" "}
                        {selectedHex.properties?.park_score != null
                            ? Number(selectedHex.properties.park_score).toFixed(2)
                            : "-"}
                    </div>
                    <div>
                        <b>Metro Score:</b>{" "}
                        {selectedHex.properties?.metro_score != null
                            ? Number(selectedHex.properties.metro_score).toFixed(2)
                            : "-"}
                    </div>
                </div>
            )}
        </div>
    );
}