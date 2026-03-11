export const dynamic = "force-dynamic";

export async function GET() {
    try {
        const res = await fetch("http://127.0.0.1:8000/v1/grid?full=true", {
            cache: "no-store",
        });

        if (!res.ok) {
            return new Response(
                JSON.stringify({ error: `Backend HTTP ${res.status}` }),
                {
                    status: res.status,
                    headers: { "Content-Type": "application/json" },
                }
            );
        }

        const data = await res.json();

        return new Response(JSON.stringify(data), {
            status: 200,
            headers: { "Content-Type": "application/json" },
        });
    } catch (err) {
        return new Response(
            JSON.stringify({
                error: "Proxy fetch failed",
                detail: String(err),
            }),
            {
                status: 500,
                headers: { "Content-Type": "application/json" },
            }
        );
    }
}