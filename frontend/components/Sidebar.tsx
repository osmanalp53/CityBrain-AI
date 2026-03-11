export default function Sidebar() {
    return (
        <div className="w-64 h-screen bg-slate-900 text-white p-6">
            <h1 className="text-2xl font-bold mb-10">CityBrain</h1>

            <ul className="space-y-4">
                <li className="hover:text-gray-300 cursor-pointer">Dashboard</li>
                <li className="hover:text-gray-300 cursor-pointer">Map</li>
                <li className="hover:text-gray-300 cursor-pointer">Recommendations</li>
                <li className="hover:text-gray-300 cursor-pointer">Reports</li>
            </ul>
        </div>
    );
}