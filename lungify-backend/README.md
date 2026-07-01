---
title: Lungify Backend
emoji: 🫁
colorFrom: blue
colorTo: teal
sdk: docker
app_port: 7860
pinned: false
---

# Lungify Backend

FastAPI backend for the Lungify CT screening prototype.

## What It Runs

- Binary cancer screening with the exported FusionModel artifact.
- Multiclass subtype support with the five exported Pipeline B fold bundles.
- Prototype tumor localization using the fold-1 3D U-Net on a deterministic center patch.
- A single unified Lungify AI Report response for the frontend.

## Local Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Main Endpoints

- `GET /`
- `GET /health`
- `GET /model-info`
- `POST /predict`
- `POST /predict/sample`

`POST /predict` expects `multipart/form-data` with `scan`. Real inference requires a de-identified DICOM series ZIP.

## Notes

This is a research prototype only. It is not for clinical diagnosis or a replacement for radiology review.

