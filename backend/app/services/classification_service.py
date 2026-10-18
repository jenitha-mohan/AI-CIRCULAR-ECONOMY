"""
AI Material Image Classification Service — MobileNetV2 Real Inference
====================================================================
Loads the trained 7-class MobileNetV2 checkpoint once at startup.
Runs genuine PyTorch inference on every request.

Supported classes (alphabetical — matches training class order):
  Cardboard, E-waste, Glass, Other, Paper, Plastic, Textile

NOT supported (no training data):
  Aluminum, Copper, Steel

Never generates random predictions. Returns a clear error if the
checkpoint or metadata is missing.
"""

import os
import json
import io
import logging
from typing import Dict, Any, List, Optional

from PIL import Image
from backend.app.config import settings

logger = logging.getLogger("circular_economy.classification")

# ── Paths ─────────────────────────────────────────────────────────────────────
MODEL_PATH    = os.path.join(settings.MODEL_DIR, "material_classifier_mobilenetv2_7class.pth")
METADATA_PATH = os.path.join(settings.MODEL_DIR, "material_classifier_7class_metadata.json")

# ── Constants ──────────────────────────────────────────────────────────────────
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

# Broad category mapping for all 10 marketplace materials
CATEGORY_MAP: Dict[str, str] = {
    "Plastic":   "Polymer",
    "Aluminum":  "Metal",
    "Copper":    "Metal",
    "Steel":     "Metal",
    "Paper":     "Fibre",
    "Glass":     "Mineral",
    "Textile":   "Fibre",
    "E-waste":   "Electronics",
    "Cardboard": "Fibre",
    "Other":     "Mixed",
}

METAL_CLASSES = {"Aluminum", "Copper", "Steel"}
# Evidence-based validation calibration threshold:
# On the validation set, predictions below 0.60 have a 59.9% error rate (vs 15.9% false alarm rate on correct predictions).
CONFIDENCE_UNCERTAINTY_THRESHOLD = 0.60


class MaterialClassificationService:
    """
    MobileNetV2-based material classifier.

    Loads the trained checkpoint once. Exposes classify_image() which
    accepts raw image bytes and returns a structured prediction dict.
    The interface is backward-compatible with the previous heuristic
    service so all existing API routes and tests continue to work.
    """

    def __init__(self) -> None:
        self._model = None          # lazy-loaded on first use
        self._metadata: Dict[str, Any] = {}
        self._class_names: List[str] = []
        self._image_size: int = 224
        self._model_ready: bool = False
        self._load_error: Optional[str] = None

        self._load_metadata()
        self._load_model()

    # ── Private helpers ────────────────────────────────────────────────────────

    def _load_metadata(self) -> None:
        if not os.path.exists(METADATA_PATH):
            self._load_error = f"Metadata file not found: {METADATA_PATH}"
            logger.error(self._load_error)
            return
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
            self._class_names = self._metadata.get("class_names", [])
            self._image_size  = self._metadata.get("image_size", 224)
            logger.info(
                "[ClassificationService] Metadata loaded. "
                "Classes: %s  ImageSize: %d",
                self._class_names, self._image_size,
            )
        except Exception as exc:
            self._load_error = f"Failed to parse metadata: {exc}"
            logger.error(self._load_error)

    def _load_model(self) -> None:
        if self._load_error:
            return  # metadata already failed
        if not os.path.exists(MODEL_PATH):
            self._load_error = f"Model checkpoint not found: {MODEL_PATH}"
            logger.error(self._load_error)
            return
        if not self._class_names:
            self._load_error = "No class_names in metadata — cannot build model."
            logger.error(self._load_error)
            return
        try:
            import torch
            from torchvision import models

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = models.mobilenet_v2()
            model.classifier[1] = torch.nn.Linear(
                model.last_channel, len(self._class_names)
            )
            model.load_state_dict(
                torch.load(MODEL_PATH, map_location=device, weights_only=True)
            )
            model = model.to(device)
            model.eval()

            self._model  = model
            self._device = device
            self._model_ready = True
            logger.info(
                "[ClassificationService] MobileNetV2 checkpoint loaded on %s. "
                "Classes: %s",
                device, self._class_names,
            )
        except Exception as exc:
            self._load_error = f"Model load failed: {exc}"
            logger.error(self._load_error)

    def _preprocess(self, image_bytes: bytes):
        """Decode bytes -> PIL -> normalised tensor. Returns (tensor, pil_image)."""
        import torch
        from torchvision import transforms

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            raise ValueError(f"Corrupted or invalid image file: {exc}") from exc

        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(self._image_size),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])
        tensor = transform(img).unsqueeze(0).to(self._device)
        return tensor, img

    # ── Public interface (backward-compatible) ─────────────────────────────────

    @property
    def model_version(self) -> str:
        return self._metadata.get("model_version", "7class-mobilenetv2-v1")

    @property
    def model_name(self) -> str:
        return self._metadata.get("model_architecture", "MobileNetV2")

    @property
    def supported_classes(self) -> List[str]:
        return list(self._class_names)

    def classify_image(self, image_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        """
        Classify raw image bytes using the trained MobileNetV2 checkpoint.

        Returns a dict with keys:
            material, category, confidence,
            top_predictions, secondary_classes (legacy compat),
            model_name, model_version, mode,
            is_fallback, prototype, supported_classes, limitations

        Raises RuntimeError if the model is not ready.
        """
        if not self._model_ready:
            raise RuntimeError(
                f"Classifier is not ready: {self._load_error or 'unknown error'}"
            )

        import torch

        try:
            tensor, _ = self._preprocess(image_bytes)

            with torch.no_grad():
                logits = self._model(tensor)
                probs  = torch.nn.functional.softmax(logits[0], dim=0)

            sorted_probs, sorted_idx = torch.sort(probs, descending=True)

            # Top-N predictions
            top3 = [
                {
                    "material":    self._class_names[sorted_idx[i].item()],
                    "confidence":  round(sorted_probs[i].item(), 6),
                    "category":    CATEGORY_MAP.get(
                                       self._class_names[sorted_idx[i].item()], "Mixed"
                                   ),
                }
                for i in range(min(3, len(self._class_names)))
            ]

            best       = top3[0]["material"]
            confidence = top3[0]["confidence"]
            is_uncertain = confidence < CONFIDENCE_UNCERTAINTY_THRESHOLD
            uncertainty_warning = (
                f"Low prediction confidence ({round(confidence * 100, 1)}% < {int(CONFIDENCE_UNCERTAINTY_THRESHOLD * 100)}%). "
                "The model detected multiple competing material features or ambiguous visual patterns. "
                "Please verify and manually select the appropriate material before publishing."
            ) if is_uncertain else None

            return {
                # Primary result
                "material":   best,
                "category":   CATEGORY_MAP.get(best, "Mixed"),
                "confidence": confidence,
                "is_uncertain": is_uncertain,
                "uncertainty_warning": uncertainty_warning,

                # Structured top-3
                "top_predictions": top3,

                # Legacy compat key (secondary_classes = top-3 excluding top-1)
                "secondary_classes": top3[1:],

                # Model provenance
                "model_name":    self.model_name,
                "model_version": self.model_version,
                "mode":          settings.ML_MODE,

                # Prototype flags
                "is_fallback":       False,
                "prototype":         True,
                "supported_classes": self._class_names,
                "limitations": (
                    "This is a 7-class prototype. Aluminum, Copper, and Steel "
                    "are not supported as dedicated output classes. Images of "
                    "these metals may be misclassified as Other or another class."
                ),
            }

        except ValueError:
            raise
        except Exception as exc:
            logger.exception("[ClassificationService] Inference error: %s", exc)
            raise RuntimeError(f"Inference failed: {exc}") from exc


# ── Singleton ─────────────────────────────────────────────────────────────────
# Instantiated once at import time (backend startup).
classification_service = MaterialClassificationService()
