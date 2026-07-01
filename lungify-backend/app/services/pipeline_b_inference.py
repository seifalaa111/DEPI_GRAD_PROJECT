from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch
import torch.nn.functional as F

from app.models.pipeline_b_architecture import LIDCClassifier, UNet3D
from app.services.dicom_loader import load_dicom_series
from app.services.preprocessing_b import center_patch, place_patch_mask, prepare_volume_b
from app.services.segmentation_service import export_segmentation_images


class PipelineBService:
    classifier_name = "Multiclass Extension Engine"
    segmentation_name = "3D U-Net Tumor Segmentation"

    def __init__(self, artifact_dir: Path, device: torch.device):
        self.artifact_dir = artifact_dir
        self.device = device
        self.bundles: list[dict[str, Any]] = []
        self.classifiers: list[LIDCClassifier] = []
        self.segmenters: list[UNet3D] = []

    @property
    def loaded(self) -> bool:
        return bool(self.classifiers) and bool(self.segmenters) and bool(self.bundles)

    def load(self) -> None:
        self.bundles.clear()
        self.classifiers.clear()
        self.segmenters.clear()
        for pkl_path in sorted(self.artifact_dir.glob("pipeline_b_fold*.pkl")):
            bundle = joblib.load(pkl_path)
            clf = LIDCClassifier(bundle["num_classes"], bundle["in_channels"], bundle["embed_dim"]).to(self.device)
            seg = UNet3D(bundle["unet_in_channels"]).to(self.device)
            clf.load_state_dict(bundle["clf_state_dict"])
            seg.load_state_dict(bundle["seg_state_dict"])
            clf.eval()
            seg.eval()
            self.bundles.append(bundle)
            self.classifiers.append(clf)
            self.segmenters.append(seg)
        if not self.bundles:
            raise FileNotFoundError(f"No Pipeline B fold bundles found in {self.artifact_dir}")

    def predict(self, dicom_dir: Path) -> dict[str, Any]:
        if not self.loaded:
            raise RuntimeError("Pipeline B models are not loaded.")
        volume, spacing = load_dicom_series(dicom_dir)
        image_np = prepare_volume_b(volume, spacing, self.bundles[0])
        image = torch.tensor(image_np[None, ...], dtype=torch.float32, device=self.device)

        probs = []
        with torch.no_grad():
            for clf in self.classifiers:
                probs.append(F.softmax(clf(image), dim=1).detach().cpu().numpy()[0])
        avg_probs = np.mean(np.stack(probs, axis=0), axis=0)
        class_names = list(self.bundles[0]["class_names"])
        pred_idx = int(avg_probs.argmax())

        patch_np, region = center_patch(image_np)
        patch = torch.tensor(patch_np[None, ...], dtype=torch.float32, device=self.device)
        with torch.no_grad():
            seg_logits = self.segmenters[0](patch)
            seg_patch = (torch.sigmoid(seg_logits) >= float(self.bundles[0].get("seg_threshold", 0.5))).cpu().numpy()[0, 0]
        mask = place_patch_mask(seg_patch.astype(np.float32), tuple(image_np.shape[1:]), region)
        images = export_segmentation_images(image_np, mask)

        return {
            "label": class_names[pred_idx],
            "confidence": float(avg_probs[pred_idx]),
            "probabilities": {class_names[i]: float(avg_probs[i]) for i in range(len(class_names))},
            "source": self.classifier_name,
            "segmentation": {
                "available": True,
                "source": self.segmentation_name,
                "localization_scope": "center-patch prototype localization",
                **images,
            },
        }

