import { NextResponse } from "next/server";

import { createSamplePrediction, requestBackend } from "@/src/lib/server/lungify-demo";

export const runtime = "nodejs";

export async function POST() {
  const backend = await requestBackend("/predict/sample", { method: "POST" });

  if (backend.kind === "ok") {
    return backend.response;
  }

  if (backend.kind === "unreachable") {
    return NextResponse.json(
      createSamplePrediction([`Configured backend ${backend.backendUrl} is unreachable, so this sample response was served locally.`]),
    );
  }

  return NextResponse.json(createSamplePrediction());
}
