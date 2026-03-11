import "./globals.css";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body className="bg-gray-100">

        <div className="flex">

          <Sidebar />

          <div className="flex-1">

            <Topbar />

            {children}

          </div>

        </div>

      </body>
    </html>
  );
}