from __future__ import annotations

import os

os.environ["LUNGIFY_SKIP_MODEL_LOAD"] = "1"

from fastapi.testclient import TestClient

from app.main import app


def test_health_contract():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert "loaded_models" in body


def test_predict_sample_contract():
    with TestClient(app) as client:
        response = client.post("/predict/sample")
    assert response.status_code == 200
    body = response.json()
    assert body["model_status"] == "sample"
    assert body["final_assessment"]["label"] == "Malignant"
    assert "research prototype" in body["report"]["disclaimer"]


def test_invalid_file_rejected():
    with TestClient(app) as client:
        response = client.post("/predict", files={"scan": ("bad.pdf", b"nope", "application/pdf")})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "validation_error"

