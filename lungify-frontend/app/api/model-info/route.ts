import { NextResponse } from "next/server";

import { createDemoModelInfo, createProxyDegradedModelInfo, requestBackend } from "@/src/lib/server/lungify-demo";

export const runtime = "nodejs";

export async function GET() {
  const backend = await requestBackend("/model-info");

  if (backend.kind === "missing") {
    return NextResponse.json(createDemoModelInfo());
  }

  if (backend.kind === "unreachable") {
    return NextResponse.json(createProxyDegradedModelInfo([`Configured backend ${backend.backendUrl} is unreachable.`]));
  }

  if (!backend.response.ok) {
    return NextResponse.json(
      createProxyDegradedModelInfo([`Configured backend returned HTTP ${backend.response.status} for /model-info.`]),
    );
  }

  const data = await backend.response.json();
  return NextResponse.json({
    ...data,
    warnings: Array.isArray(data?.warnings) ? data.warnings : [],
    backend_mode: "proxy",
  });
}
