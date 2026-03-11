"use client";

import { useEffect, useState } from "react";
import MapView from "./MapView";
import WorstCellsTable from "./WorstCellsTable";

export default function Dashboard() {
    const [summary, setSummary] = useState<any>(null);
    const [error, setError] = useState("");

    useEffect(() => {
        fetch("/api/summary")
            .then((res) => {
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }
                return res.json();
            })
            .then((data) => {
                console.log("SUMMARY OK:", data);
                setSummary(data);
            })
            .catch((err) => {
                console.error("Summary fetch error:", err);
                setError(String(err));
            });
    }, []);

    return (
        <div className="p-6 bg-slate-50 min-h-screen">

            {/* HEADER */}

            <div className="mb-6">
                <h3 className="text-3xl font-bold text-slate-900">
                    City Overview
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                    Ankara urban accessibility dashboard
                </p>
            </div>

            {/* ERROR */}

            {error && (
                <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm">
                    Summary hata: {error}
                </div>
            )}

            {/* KPI CARDS */}

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

                {/* Urban Score */}

                <div className="bg-white p-6 rounded-2xl border shadow-sm">
                    <div className="text-sm font-medium text-slate-500">
                        Urban Score
                    </div>

                    <div className="mt-3 text-3xl font-bold text-emerald-600">
                        {summary?.avg_urban_score != null
                            ? Number(summary.avg_urban_score).toFixed(2)
                            : "-"}
                    </div>

                    <div className="mt-2 text-xs text-slate-400">
                        Ortalama birleşik erişim skoru
                    </div>
                </div>

                {/* Park Score */}

                <div className="bg-white p-6 rounded-2xl border shadow-sm">
                    <div className="text-sm font-medium text-slate-500">
                        Park Score
                    </div>

                    <div className="mt-3 text-3xl font-bold text-blue-600">
                        {summary?.avg_park_score != null
                            ? Number(summary.avg_park_score).toFixed(2)
                            : "-"}
                    </div>

                    <div className="mt-2 text-xs text-slate-400">
                        Park erişimi ortalama skoru
                    </div>
                </div>

                {/* Avg Park Distance */}

                <div className="bg-white p-6 rounded-2xl border shadow-sm">
                    <div className="text-sm font-medium text-slate-500">
                        Avg Park Distance
                    </div>

                    <div className="mt-3 text-3xl font-bold text-purple-600">
                        {summary?.avg_d_park != null
                            ? `${Number(summary.avg_d_park).toFixed(0)} m`
                            : "-"}
                    </div>

                    <div className="mt-2 text-xs text-slate-400">
                        En yakın parka ortalama mesafe
                    </div>
                </div>

                {/* Bad Access */}

                <div className="bg-white p-6 rounded-2xl border shadow-sm">
                    <div className="text-sm font-medium text-slate-500">
                        Bad Access Cells
                    </div>

                    <div className="mt-3 text-3xl font-bold text-red-600">
                        {summary?.bad_access_cell_count != null
                            ? String(summary.bad_access_cell_count)
                            : "-"}
                    </div>

                    <div className="mt-2 text-xs text-slate-400">
                        Düşük erişim tespit edilen hex sayısı
                    </div>
                </div>

            </div>

            {/* MAP PANEL */}

            <div className="mt-8 rounded-2xl border bg-white p-4 shadow-sm">

                <div className="mb-4">
                    <h4 className="text-lg font-semibold text-slate-900">
                        Urban Health Heatmap
                    </h4>

                    <p className="text-sm text-slate-500">
                        H3 hex grid üzerinde park ve metro erişimine göre hesaplanan urban score dağılımı
                    </p>
                </div>

                <MapView />

            </div>

            {/* WORST CELLS TABLE */}

            <div className="mt-8">

                <WorstCellsTable
                    cells={summary?.worst_cells ?? []}
                />

            </div>

        </div>
    );
}