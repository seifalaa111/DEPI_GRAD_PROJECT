import { NextResponse } from "next/server";

import { createDemoHealth, createProxyDegradedHealth, requestBackend } from "@/src/lib/server/lungify-demo";

export const runtime = "nodejs";

export async function GET() {
  const backend = await requestBackend("/health");

  if (backend.kind === "missing") {
    return NextResponse.json(createDemoHealth());
  }

  if (backend.kind === "unreachable") {
    return NextResponse.json(createProxyDegradedHealth([`Configured backend ${backend.backendUrl} is unreachable.`]));
  }

  if (!backend.response.ok) {
    return NextResponse.json(
      createProxyDegradedHealth([`Configured backend returned HTTP ${backend.response.status} for /health.`]),
    );
  }

  const data = await backend.response.json();
  return NextResponse.json({
    ...data,
    warnings: Array.isArray(data?.warnings) ? data.warnings : [],
    backend_mode: "proxy",
  });
}
