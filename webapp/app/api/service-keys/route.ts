import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://localhost:8000";

function resolveBackendUrl(): string {
  const envUrl = process.env.RESUME_MATCHER_BACKEND_URL;
  const baseUrl = envUrl?.trim() || DEFAULT_BACKEND_URL;
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

export async function GET() {
  const backendUrl = resolveBackendUrl();

  try {
    const response = await fetch(`${backendUrl}/api/service-keys`, {
      method: "GET",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }

    const details = await response.text();

    return NextResponse.json({
      config_keys: {},
      error: `Backend responded with status ${response.status}`,
      details,
    });
  } catch (error) {
    return NextResponse.json(
      {
        config_keys: {},
        error: "Failed to reach backend for service keys.",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 200 }
    );
  }
}
