import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://localhost:8000";

function resolveBackendUrl(): string {
  const envUrl = process.env.RESUME_MATCHER_BACKEND_URL;
  const baseUrl = envUrl?.trim() || DEFAULT_BACKEND_URL;
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

export async function POST(request: Request) {
  const backendUrl = resolveBackendUrl();

  try {
    const formData = await request.formData();

    const response = await fetch(`${backendUrl}/api/resume-processor`, {
      method: "POST",
      body: formData,
    });

    const contentType = response.headers.get("content-type") || "";

    if (!response.ok) {
      const details = await response.text();
      return NextResponse.json(
        {
          error: `Backend responded with status ${response.status}`,
          details,
        },
        { status: 502 }
      );
    }

    if (contentType.includes("application/json")) {
      const data = await response.json();
      return NextResponse.json(data);
    }

    const details = await response.text();

    return NextResponse.json(
      {
        error: "Unexpected content type from backend response.",
        details,
      },
      { status: 502 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to reach backend for resume processing.",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 502 }
    );
  }
}
