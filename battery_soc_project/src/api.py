"""
SOC Tahmin REST API
Flask ile SOC tahmin servisi
"""

from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
import json
from datetime import datetime
import logging

# Flask uygulaması
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global değişkenler
model = None
model_info = None
feature_names = None

# Model yükleme fonksiyonu
def load_model_artifacts():
    global model, model_info, feature_names

    models_dir = os.path.join(os.path.dirname(__file__), "../models")
    model_path = os.path.join(models_dir, "battery_soc_model.pkl")
    info_path = os.path.join(models_dir, "model_info.json")

    if not os.path.exists(model_path) or not os.path.exists(info_path):
        logger.error("❌ Model veya model_info.json bulunamadı.")
        return False

    try:
        model = joblib.load(model_path)
        with open(info_path, "r") as f:
            model_info = json.load(f)

        feature_names = model_info.get("feature_names", [])
        logger.info(f"✓ Model yüklendi: {model_info.get('best_model_name')}")
        return True
    except Exception as e:
        logger.error(f"❌ Model yükleme hatası: {e}")
        return False

# Hata yakalama decorator
def handle_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Hatası: {e}")
            return jsonify({
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }), 500
    wrapper.__name__ = f.__name__
    return wrapper

# Health check
@app.route("/health", methods=["GET"])
@handle_errors
def health_check():
    status = {
        "status": "healthy" if model else "unhealthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }
    if model_info:
        status["model_name"] = model_info.get("best_model_name", "Unknown")
        status["model_metrics"] = model_info.get("metrics", {})
    return jsonify(status)

# Model info
@app.route("/model-info", methods=["GET"])
@handle_errors
def get_model_info():
    if not model_info:
        return jsonify({"error": "Model bilgisi bulunamadı", "status": "error"}), 404
    return jsonify({
        "model_info": model_info,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

# Tekli tahmin
@app.route("/predict", methods=["POST"])
@handle_errors
def predict_soc():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş", "status": "error"}), 503

    data = request.get_json()
    if not data or "features" not in data:
        return jsonify({
            "error": '"features" alanı gerekli',
            "status": "error"
        }), 400

    features = data["features"]
    if feature_names and len(features) != len(feature_names):
        return jsonify({
            "error": f'Özellik sayısı uyumsuz. Beklenen: {len(feature_names)}, Gelen: {len(features)}',
            "status": "error"
        }), 400

    features_array = np.array(features).reshape(1, -1)
    prediction = model.predict(features_array)[0]
    predicted_soc = max(0, min(100, float(prediction)))

    return jsonify({
        "predicted_soc": predicted_soc,
        "model_name": model_info.get("best_model_name", "Unknown"),
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

# Toplu tahmin
@app.route("/batch-predict", methods=["POST"])
@handle_errors
def batch_predict():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş", "status": "error"}), 503

    data = request.get_json()
    if not data or "batch_features" not in data:
        return jsonify({"error": '"batch_features" gerekli', "status": "error"}), 400

    batch_features = data["batch_features"]
    predictions = []
    for i, features in enumerate(batch_features):
        try:
            features_array = np.array(features).reshape(1, -1)
            prediction = model.predict(features_array)[0]
            predicted_soc = max(0, min(100, float(prediction)))
            predictions.append({"index": i, "predicted_soc": predicted_soc, "status": "success"})
        except Exception as e:
            predictions.append({"index": i, "error": str(e), "status": "error"})

    return jsonify({
        "predictions": predictions,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🔋 SOC Tahmin API",
        "endpoints": [
            "GET /health",
            "GET /model-info",
            "GET /features",
            "POST /predict",
            "POST /batch-predict"
        ],
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })


# Başlangıçta modeli yükle
if __name__ == "__main__":
    print("🚀 SOC Tahmin API başlatılıyor...")
    if load_model_artifacts():
        print("✓ Model yüklendi, API hazır!")
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("❌ Model yüklenemedi, API başlatılamadı.")
                        