from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch

from app.config import Settings
from app.services.pipeline_a_inference import PipelineAService
from app.services.pipeline_b_inference import PipelineBService


class ModelRegistry:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.device = self._select_device(settings.device)
        self.pipeline_a = PipelineAService(settings.pipeline_a_weight, self.device)
        self.pipeline_b = PipelineBService(settings.pipeline_b_weights_dir, self.device)
        self.load_errors: dict[str, str] = {}

    @staticmethod
    def _select_device(pref: str) -> torch.device:
        if pref == "cuda":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if pref == "cpu":
            return torch.device("cpu")
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load(self) -> None:
        if self.settings.skip_model_load:
            self.load_errors["models"] = "Model loading skipped by LUNGIFY_SKIP_MODEL_LOAD=1."
            return
        for name, service in (("pipeline_a", self.pipeline_a), ("pipeline_b", self.pipeline_b)):
            try:
                service.load()
            except Exception as exc:
                self.load_errors[name] = str(exc)

    def health(self) -> dict[str, Any]:
        return {
            "pipeline_a": {
                "loaded": self.pipeline_a.loaded,
                "artifact": str(self.settings.pipeline_a_weight),
            },
            "pipeline_b": {
                "loaded": self.pipeline_b.loaded,
                "artifacts": len(list(self.settings.pipeline_b_weights_dir.glob("pipeline_b_fold*.pkl"))),
            },
            "errors": self.load_errors,
        }

    def model_info(self) -> dict[str, Any]:
        return {
            "pipeline_a": _read_json(self.settings.pipeline_a_params),
            "pipeline_b": _read_json(self.settings.pipeline_b_params),
            "cv_summary": _read_json(self.settings.cv_summary),
        }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

