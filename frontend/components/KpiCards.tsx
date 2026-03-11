type Props = {
    summary: any;
};

export default function KpiCards({ summary }: Props) {
    if (!summary) return null;

    const cards = [
        {
            title: "Urban Score",
            value:
                summary.avg_urban_score != null
                    ? Number(summary.avg_urban_score).toFixed(2)
                    : "-",
        },
        {
            title: "Park Score",
            value:
                summary.avg_park_score != null
                    ? Number(summary.avg_park_score).toFixed(2)
                    : "-",
        },
        {
            title: "Avg Park Distance",
            value:
                summary.avg_d_park != null
                    ? `${Number(summary.avg_d_park).toFixed(0)} m`
                    : "-",
        },
        {
            title: "Bad Access Cells",
            value:
                summary.bad_access_cell_count != null
                    ? String(summary.bad_access_cell_count)
                    : "-",
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {cards.map((card) => (
                <div
                    key={card.title}
                    className="rounded-xl border bg-white p-4 shadow-sm"
                >
                    <div className="text-sm text-slate-500">{card.title}</div>
                    <div className="mt-2 text-2xl font-semibold text-slate-900">
                        {card.value}
                    </div>
                </div>
            ))}
        </div>
    );
}