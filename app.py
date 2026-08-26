"""
app.py
-------
Flask backend for the crop disease detection system.

Routes
------
GET  /              Modern web UI shell
POST /predict        HTML form submission route (renders result.html fallback)
POST /api/predict     Asynchronous JSON API pipeline endpoint
GET  /api/crops       List of supported crops, parts, and metadata
GET  /api/sample      Analyze a sample pre-generated dataset image
"""

import os
import time
import uuid
from flask import Flask, jsonify, render_template, request, url_for
from werkzeug.utils import secure_filename

from model.detector import CropDiseaseDetector
from model.knowledge_base import CROPS, PARTS, get_diagnosis

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
DATASET_DIR = os.path.join(os.path.dirname(__file__), "data", "dataset")
ALLOWED_EXT = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_DIR, exist_ok=True)

detector = CropDiseaseDetector()


def _cleanup_old_uploads(max_age_seconds: int = 3600):
    """Purge upload files older than max_age_seconds to prevent disk leaks."""
    try:
        now = time.time()
        for fname in os.listdir(UPLOAD_DIR):
            fpath = os.path.join(UPLOAD_DIR, fname)
            if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > max_age_seconds:
                os.remove(fpath)
    except Exception:
        pass


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def _run_pipeline(crop: str, part: str, saved_path: str) -> dict:
    """Shared logic between the HTML form flow and the JSON API."""
    crop = crop.lower().strip()
    part = part.lower().strip()

    if crop not in CROPS:
        raise ValueError(f"Unsupported crop '{crop}'. Choose from: {', '.join(CROPS)}")
    if part not in PARTS:
        raise ValueError(f"Unsupported part '{part}'. Choose from: {', '.join(PARTS)}")

    result = detector.analyze(saved_path, part=part)
    result["crop"] = crop

    if result["is_diseased"]:
        diagnosis = get_diagnosis(crop, part)
        if diagnosis:
            result["disease"] = diagnosis["disease"]
            result["cause"] = diagnosis["cause"]
            result["management"] = diagnosis["management"]
        else:
            result["disease"] = "Unspecified Plant Pathology"
            result["cause"] = "Pathogen requires laboratory assay"
            result["management"] = [
                "Isolate affected plants to restrict spread.",
                "Consult your local agricultural extension service.",
                "Apply broad-spectrum organic bio-fungicide if spread continues."
            ]
    else:
        result["disease"] = "Healthy (No Pathology Found)"
        result["cause"] = "N/A - Normal Plant Physiology"
        result["management"] = [
            f"No visible signs of disease detected on this {part}.",
            "Maintain optimal watering, balanced fertilization, and routine field scouting."
        ]

    return result


def _save_upload(file_storage) -> tuple[str, str]:
    if not file_storage or file_storage.filename == "":
        raise ValueError("No image file was provided.")
    if not _allowed_file(file_storage.filename):
        raise ValueError("Unsupported file format. Please upload a PNG, JPG, or JPEG image.")

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    path = os.path.join(UPLOAD_DIR, filename)
    file_storage.save(path)
    return filename, path


@app.route("/")
def index():
    _cleanup_old_uploads()
    return render_template("index.html", crops=CROPS, parts=PARTS)


@app.route("/predict", methods=["POST"])
@app.route("/api/predict", methods=["POST"])
def predict():
    _cleanup_old_uploads()
    crop = request.form.get("crop", "")
    part = request.form.get("part", "")
    saved_path = None

    try:
        filename, saved_path = _save_upload(request.files.get("image"))
        result = _run_pipeline(crop, part, saved_path)
        result["image_url"] = url_for("static", filename=f"uploads/{filename}", _external=False)
    except ValueError as exc:
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
        return jsonify({"error": f"Internal server error: {str(exc)}"}), 500

    return jsonify(result)




@app.route("/api/sample", methods=["GET"])
def api_sample():
    """Returns analysis for a sample image from the dataset folder."""
    _cleanup_old_uploads()
    crop = request.args.get("crop", "rice").lower()
    part = request.args.get("part", "leaf").lower()
    condition = request.args.get("condition", "diseased").lower()

    if crop not in CROPS or part not in PARTS or condition not in ["healthy", "diseased"]:
        return jsonify({"error": "Invalid sample parameters"}), 400

    sample_dir = os.path.join(DATASET_DIR, crop, part, condition)
    if not os.path.exists(sample_dir) or not os.listdir(sample_dir):
        return jsonify({"error": "Sample dataset not generated yet. Run python data/generate_dataset.py"}), 404

    sample_file = os.listdir(sample_dir)[0]
    sample_path = os.path.join(sample_dir, sample_file)

    ext = sample_file.rsplit(".", 1)[1].lower() if "." in sample_file else "png"
    dest_filename = secure_filename(f"sample_{crop}_{part}_{condition}_{uuid.uuid4().hex[:6]}.{ext}")
    dest_path = os.path.join(UPLOAD_DIR, dest_filename)

    with open(sample_path, "rb") as src, open(dest_path, "wb") as dst:
        dst.write(src.read())

    try:
        result = _run_pipeline(crop, part, dest_path)
        result["image_url"] = url_for("static", filename=f"uploads/{dest_filename}", _external=False)
        result["is_sample"] = True
        return jsonify(result)
    except Exception as exc:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/crops")
def api_crops():
    crop_icons = {
        "rice": "🌾",
        "wheat": "🌾",
        "maize": "🌽",
        "tomato": "🍅",
        "potato": "🥔",
        "cotton": "☁️",
        "sugarcane": "🎋",
        "chili": "🌶️"
    }
    dataset_ready = os.path.exists(DATASET_DIR)
    return jsonify({
        "crops": CROPS,
        "parts": PARTS,
        "crop_icons": crop_icons,
        "dataset_ready": dataset_ready
    })


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Image payload too large (maximum limit is 8MB)."}), 413


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
