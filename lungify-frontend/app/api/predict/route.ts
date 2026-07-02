import { NextResponse } from "next/server";

import { createPreviewPrediction, isZipUpload, requestBackend } from "@/src/lib/server/lungify-demo";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const formData = await request.formData();
  const scan = formData.get("scan");
  const filename = scan instanceof File ? scan.name : null;

  const backend = await requestBackend("/predict", {
    method: "POST",
    body: formData,
  });

  if (backend.kind === "ok") {
    return backend.response;
  }

  if (backend.kind === "unreachable") {
    return NextResponse.json(
      {
        message: `Configured backend ${backend.backendUrl} is unreachable. Real inference is temporarily unavailable.`,
      },
      { status: 503 },
    );
  }

  const warning = isZipUpload(filename)
    ? "This deployment is running without the FastAPI inference backend, so ZIP uploads stay in preview mode."
    : "Single .dcm, .png, and .jpg uploads are preview-only in the built-in Vercel demo.";

  return NextResponse.json(createPreviewPrediction(warning));
}
