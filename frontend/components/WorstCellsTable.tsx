type Props = {
    cells: any[];
};

export default function WorstCellsTable({ cells }: Props) {
    if (!cells || cells.length === 0) {
        return (
            <div className="text-sm text-slate-500">
                No worst cells data
            </div>
        );
    }

    return (
        <div className="rounded-2xl border bg-white shadow-sm">
            <div className="p-4 border-b">
                <h4 className="text-lg font-semibold">
                    Worst Urban Areas
                </h4>
            </div>

            <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-600">
                    <tr>
                        <th className="text-left p-3">H3</th>
                        <th className="text-left p-3">Urban Score</th>
                        <th className="text-left p-3">Park Dist</th>
                        <th className="text-left p-3">Metro Dist</th>
                    </tr>
                </thead>

                <tbody>
                    {cells.map((cell, i) => (
                        <tr
                            key={cell.h3}
                            className="border-t hover:bg-slate-50"
                        >
                            <td className="p-3 font-mono text-xs">
                                {cell.h3}
                            </td>

                            <td className="p-3">
                                {Number(cell.score).toFixed(2)}
                            </td>

                            <td className="p-3">
                                {Number(cell.d_park).toFixed(0)} m
                            </td>

                            <td className="p-3">
                                {Number(cell.d_metro).toFixed(0)} m
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}