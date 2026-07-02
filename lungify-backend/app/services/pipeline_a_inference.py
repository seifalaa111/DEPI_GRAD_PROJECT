from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import torch

from app.models.pipeline_a_architecture import FusionModel
from app.services.dicom_loader import load_dicom_series
from app.services.preprocessing_a import prepare_tabular_a, prepare_volume_a


class PipelineAService:
    name = "Binary Cancer Screening Engine"

    def __init__(self, artifact_path: Path, device: torch.device):
        self.artifact_path = artifact_path
        self.device = device
        self.bundle: dict[str, Any] | None = None
        self.model: FusionModel | None = None

    @property
    def loaded(self) -> bool:
        return self.model is not None and self.bundle is not None

    def load(self) -> None:
        bundle = joblib.load(self.artifact_path)
        model = FusionModel(int(bundle["n_tabular"])).to(self.device)
        model.load_state_dict(bundle["model_state_dict"])
        model.eval()
        self.bundle = bundle
        self.model = model

    def predict(self, dicom_dir: Path, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.loaded:
            raise RuntimeError("Pipeline A model is not loaded.")
        assert self.bundle is not None
        assert self.model is not None
        volume, spacing = load_dicom_series(dicom_dir)
        image_np = prepare_volume_a(volume, spacing, self.bundle)
        tab_np = prepare_tabular_a(metadata, self.bundle)
        image = torch.tensor(image_np, dtype=torch.float32, device=self.device)
        tabular = torch.tensor(tab_np, dtype=torch.float32, device=self.device)
        with torch.no_grad():
            logit = self.model(image, tabular)
            malignant_probability = float(torch.sigmoid(logit).detach().cpu().numpy()[0])
        threshold = float(self.bundle.get("threshold", 0.5))
        label = "Malignant" if malignant_probability >= threshold else "Benign/Unknown"
        confidence = malignant_probability if label == "Malignant" else 1.0 - malignant_probability
        return {
            "label": label,
            "malignant_probability": malignant_probability,
            "confidence": confidence,
            "threshold": threshold,
            "source": self.name,
        }

