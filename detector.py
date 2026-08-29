"""
detector.py
------------
A from-scratch classical CV disease/severity estimator.
"""

import cv2
import numpy as np

WORK_SIZE = (256, 256)

# HSV bounds are OpenCV convention: H in [0,179], S,V in [0,255]
LEAF_HEALTHY_HSV = [
    (np.array([25, 35, 35]), np.array([95, 255, 255])),   # green band
]
ROOT_HEALTHY_HSV = [
    (np.array([5, 10, 110]), np.array([35, 80, 255])),    # pale tan/white/cream
]

SEVERITY_LEVELS = [
    (0.06, "Healthy"),
    (0.18, "Mild"),
    (0.38, "Moderate"),
    (1.01, "Severe"),
]


def _subject_mask(hsv):
    """Foreground mask: isolate leaf/root subject from background."""
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    mask = ((s > 20) & (v > 20) & (v < 252)).astype(np.uint8) * 255
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def _healthy_mask(hsv, ranges):
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in ranges:
        mask |= cv2.inRange(hsv, lo, hi)
    return mask


def _severity_bucket(score):
    for threshold, label in SEVERITY_LEVELS:
        if score <= threshold:
            return label
    return "Severe"


class CropDiseaseDetector:
    """Stateless classical-CV analyzer. One instance is reused per request."""

    def analyze(self, image_path: str, part: str = "leaf") -> dict:
        img = cv2.imread(image_path)
        if img is None or img.size == 0:
            raise ValueError(f"Could not load image file at {image_path}. File may be corrupted.")

        img = cv2.resize(img, WORK_SIZE)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        subject = _subject_mask(hsv)
        subject_pixels = int(np.count_nonzero(subject))
        if subject_pixels < 100:
            # Fall back to whole frame if background segmentation filtered too much
            subject = np.full(hsv.shape[:2], 255, dtype=np.uint8)
            subject_pixels = subject.size

        healthy_ranges = LEAF_HEALTHY_HSV if part == "leaf" else ROOT_HEALTHY_HSV
        healthy = _healthy_mask(hsv, healthy_ranges)
        healthy = cv2.bitwise_and(healthy, subject)

        lesion = cv2.bitwise_and(cv2.bitwise_not(healthy), subject)
        lesion_pixels = int(np.count_nonzero(lesion))

        severity_score = round(lesion_pixels / float(subject_pixels), 4)
        severity_label = _severity_bucket(severity_score)
        is_diseased = severity_label != "Healthy"

        # Heuristic confidence calculation
        confidence = round(min(0.96, 0.65 + severity_score * 0.45), 2)

        return {
            "part": part,
            "diseased_area_percent": round(severity_score * 100, 1),
            "severity": severity_label,
            "is_diseased": is_diseased,
            "confidence": confidence,
        }
