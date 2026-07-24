from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for
)
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
from disease_info import disease_details

import os
import json
import numpy as np
from uuid import uuid4


app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "ai-leaf-scan-secret-key"
)

CORS(app)


# -------------------------------------------------
# Upload folder
# -------------------------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------------------------------
# Load model
# -------------------------------------------------
model = load_model("model/model.h5")

print("Model loaded successfully")
print("Output Shape:", model.output_shape)


# -------------------------------------------------
# Load labels
# -------------------------------------------------
with open("model/labels.json", "r", encoding="utf-8") as file:
    categories = json.load(file)


# -------------------------------------------------
# UI translations
# -------------------------------------------------
UI_TEXT = {
    "en": {
        "app_name": "AI Leaf Scan",
        "subtitle": "Smart Crop Disease Detection",
        "hero_title": "Protect Your Crops with AI-Powered Leaf Analysis",
        "hero_description": (
            "Upload a leaf image and instantly detect crop diseases "
            "using artificial intelligence."
        ),
        "fast_detection": "Fast Detection",
        "high_accuracy": "High Accuracy",
        "recommendations": "Smart Recommendations",
        "upload_title": "Upload Leaf Image",
        "upload_description": "Choose a clear image of the affected leaf.",
        "choose_image": "Choose Image",
        "scan_leaf": "Scan Leaf",
        "analyzing": "Analyzing Leaf...",
        "result_title": "Analysis Result",
        "crop": "Crop",
        "disease": "Disease",
        "disease_affected": "Disease Affected",
        "healthy": "Healthy Plant",
        "confidence": "Prediction Confidence",
        "cause": "Cause",
        "symptoms": "Symptoms",
        "solutions": "Recommendations",
        "scan_another": "Scan Another Leaf",
        "footer": "AI-powered crop disease detection",
        "no_image": "No image uploaded.",
        "no_file": "No file selected.",
        "invalid_file": "Invalid file name.",
        "information_unavailable": "Information not available.",
        "consult_expert": "Consult an agricultural expert."
    },

    "kn": {
        "app_name": "ಎಐ ಎಲೆ ಪರೀಕ್ಷೆ",
        "subtitle": "ಸ್ಮಾರ್ಟ್ ಬೆಳೆ ರೋಗ ಪತ್ತೆ",
        "hero_title": "ಎಐ ಆಧಾರಿತ ಎಲೆ ವಿಶ್ಲೇಷಣೆಯಿಂದ ನಿಮ್ಮ ಬೆಳೆಗಳನ್ನು ರಕ್ಷಿಸಿ",
        "hero_description": (
            "ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯ "
            "ಮೂಲಕ ಬೆಳೆ ರೋಗವನ್ನು ತಕ್ಷಣ ಪತ್ತೆಹಚ್ಚಿ."
        ),
        "fast_detection": "ವೇಗವಾದ ಪತ್ತೆ",
        "high_accuracy": "ಹೆಚ್ಚಿನ ನಿಖರತೆ",
        "recommendations": "ಸ್ಮಾರ್ಟ್ ಶಿಫಾರಸುಗಳು",
        "upload_title": "ಎಲೆಯ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "upload_description": "ಬಾಧಿತ ಎಲೆಯ ಸ್ಪಷ್ಟ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
        "choose_image": "ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",
        "scan_leaf": "ಎಲೆಯನ್ನು ಪರೀಕ್ಷಿಸಿ",
        "analyzing": "ಎಲೆಯನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        "result_title": "ವಿಶ್ಲೇಷಣೆಯ ಫಲಿತಾಂಶ",
        "crop": "ಬೆಳೆ",
        "disease": "ರೋಗ",
        "disease_affected": "ರೋಗಬಾಧಿತ",
        "healthy": "ಆರೋಗ್ಯಕರ ಗಿಡ",
        "confidence": "ಭವಿಷ್ಯವಾಣಿಯ ವಿಶ್ವಾಸಾರ್ಹತೆ",
        "cause": "ಕಾರಣ",
        "symptoms": "ಲಕ್ಷಣಗಳು",
        "solutions": "ಶಿಫಾರಸುಗಳು",
        "scan_another": "ಮತ್ತೊಂದು ಎಲೆಯನ್ನು ಪರೀಕ್ಷಿಸಿ",
        "footer": "ಎಐ ಆಧಾರಿತ ಬೆಳೆ ರೋಗ ಪತ್ತೆ",
        "no_image": "ಯಾವುದೇ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿಲ್ಲ.",
        "no_file": "ಯಾವುದೇ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿಲ್ಲ.",
        "invalid_file": "ಅಮಾನ್ಯ ಫೈಲ್ ಹೆಸರು.",
        "information_unavailable": "ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",
        "consult_expert": "ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ."
    }
}


# -------------------------------------------------
# Crop-name translations
# -------------------------------------------------
CROP_NAMES = {
    "Apple": {"en": "Apple", "kn": "ಸೇಬು"},
    "Blueberry": {"en": "Blueberry", "kn": "ಬ್ಲೂಬೆರಿ"},
    "Cherry_(including_sour)": {
        "en": "Cherry",
        "kn": "ಚೆರಿ"
    },
    "Corn_(maize)": {
        "en": "Corn",
        "kn": "ಮೆಕ್ಕೆಜೋಳ"
    },
    "Grape": {"en": "Grape", "kn": "ದ್ರಾಕ್ಷಿ"},
    "Orange": {"en": "Orange", "kn": "ಕಿತ್ತಳೆ"},
    "Peach": {"en": "Peach", "kn": "ಪೀಚ್"},
    "Pepper,_bell": {
        "en": "Bell Pepper",
        "kn": "ದೊಣ್ಣೆ ಮೆಣಸಿನಕಾಯಿ"
    },
    "Potato": {"en": "Potato", "kn": "ಆಲೂಗಡ್ಡೆ"},
    "Raspberry": {"en": "Raspberry", "kn": "ರಾಸ್ಪ್ಬೆರಿ"},
    "Soybean": {"en": "Soybean", "kn": "ಸೋಯಾಬೀನ್"},
    "Squash": {"en": "Squash", "kn": "ಸ್ಕ್ವಾಶ್"},
    "Strawberry": {"en": "Strawberry", "kn": "ಸ್ಟ್ರಾಬೆರಿ"},
    "Tomato": {"en": "Tomato", "kn": "ಟೊಮೇಟೊ"}
}


# -------------------------------------------------
# Disease-name translations
# -------------------------------------------------
DISEASE_NAMES = {
    "Apple_scab": {
        "en": "Apple Scab",
        "kn": "ಸೇಬಿನ ಸ್ಕ್ಯಾಬ್ ರೋಗ"
    },
    "Black_rot": {
        "en": "Black Rot",
        "kn": "ಕಪ್ಪು ಕೊಳೆ ರೋಗ"
    },
    "Cedar_apple_rust": {
        "en": "Cedar Apple Rust",
        "kn": "ಸೀಡರ್ ಸೇಬಿನ ತುಕ್ಕು ರೋಗ"
    },
    "healthy": {
        "en": "Healthy",
        "kn": "ಆರೋಗ್ಯಕರ"
    },
    "Powdery_mildew": {
        "en": "Powdery Mildew",
        "kn": "ಬೂದಿ ರೋಗ"
    },
    "Cercospora_leaf_spot Gray_leaf_spot": {
        "en": "Cercospora Gray Leaf Spot",
        "kn": "ಸೆರ್ಕೋಸ್ಪೋರಾ ಬೂದು ಎಲೆ ಕಲೆ ರೋಗ"
    },
    "Common_rust_": {
        "en": "Common Rust",
        "kn": "ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ"
    },
    "Northern_Leaf_Blight": {
        "en": "Northern Leaf Blight",
        "kn": "ಉತ್ತರ ಎಲೆ ಅಂಗಮಾರಿ ರೋಗ"
    },
    "Esca_(Black_Measles)": {
        "en": "Esca (Black Measles)",
        "kn": "ಎಸ್ಕಾ ಕಪ್ಪು ಮಚ್ಚೆ ರೋಗ"
    },
    "Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "en": "Leaf Blight",
        "kn": "ಎಲೆ ಅಂಗಮಾರಿ ರೋಗ"
    },
    "Haunglongbing_(Citrus_greening)": {
        "en": "Huanglongbing (Citrus Greening)",
        "kn": "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ"
    },
    "Bacterial_spot": {
        "en": "Bacterial Spot",
        "kn": "ಬ್ಯಾಕ್ಟೀರಿಯಾ ಕಲೆ ರೋಗ"
    },
    "Early_blight": {
        "en": "Early Blight",
        "kn": "ಆರಂಭಿಕ ಅಂಗಮಾರಿ ರೋಗ"
    },
    "Late_blight": {
        "en": "Late Blight",
        "kn": "ತಡ ಅಂಗಮಾರಿ ರೋಗ"
    },
    "Leaf_Mold": {
        "en": "Leaf Mold",
        "kn": "ಎಲೆ ಬೂಷ್ಟು ರೋಗ"
    },
    "Septoria_leaf_spot": {
        "en": "Septoria Leaf Spot",
        "kn": "ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಕಲೆ ರೋಗ"
    },
    "Spider_mites Two-spotted_spider_mite": {
        "en": "Two-Spotted Spider Mite",
        "kn": "ಎರಡು ಮಚ್ಚೆಯ ಜೇಡ ಹುಳು"
    },
    "Target_Spot": {
        "en": "Target Spot",
        "kn": "ಟಾರ್ಗೆಟ್ ಕಲೆ ರೋಗ"
    },
    "Tomato_Yellow_Leaf_Curl_Virus": {
        "en": "Tomato Yellow Leaf Curl Virus",
        "kn": "ಟೊಮೇಟೊ ಹಳದಿ ಎಲೆ ಮುರುಟು ವೈರಸ್"
    },
    "Tomato_mosaic_virus": {
        "en": "Tomato Mosaic Virus",
        "kn": "ಟೊಮೇಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್"
    }
}


# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def get_language():
    language = session.get("language", "en")

    if language not in ("en", "kn"):
        language = "en"

    return language


def get_crop_name(crop_key, language):
    crop_data = CROP_NAMES.get(crop_key)

    if crop_data:
        return crop_data.get(language, crop_data["en"])

    return crop_key.replace("_", " ").replace(",", "")


def get_disease_name(disease_key, language):
    disease_data = DISEASE_NAMES.get(disease_key)

    if disease_data:
        return disease_data.get(language, disease_data["en"])

    return disease_key.replace("_", " ")


def get_disease_information(disease_key, language):
    details = disease_details.get(disease_key)

    if not details:
        return {
            "cause": UI_TEXT[language]["information_unavailable"],
            "symptoms": [
                UI_TEXT[language]["information_unavailable"]
            ],
            "solution": [
                UI_TEXT[language]["consult_expert"]
            ]
        }

    # New bilingual disease_info.py structure
    if "en" in details or "kn" in details:
        selected_details = (
            details.get(language)
            or details.get("en")
            or {}
        )

        return {
            "cause": selected_details.get(
                "cause",
                UI_TEXT[language]["information_unavailable"]
            ),
            "symptoms": selected_details.get(
                "symptoms",
                [UI_TEXT[language]["information_unavailable"]]
            ),
            "solution": selected_details.get(
                "solution",
                [UI_TEXT[language]["consult_expert"]]
            )
        }

    # Temporary support for your current English-only file
    return {
        "cause": details.get(
            "cause",
            UI_TEXT[language]["information_unavailable"]
        ),
        "symptoms": details.get(
            "symptoms",
            [UI_TEXT[language]["information_unavailable"]]
        ),
        "solution": details.get(
            "solution",
            [UI_TEXT[language]["consult_expert"]]
        )
    }


def create_prediction_context(disease_key, confidence, language):
    parts = disease_key.split("___", 1)

    crop_key = parts[0]
    disease_name_key = parts[1] if len(parts) > 1 else disease_key

    details = get_disease_information(
        disease_key,
        language
    )

    return {
        "prediction": True,
        "crop": get_crop_name(crop_key, language),
        "disease": get_disease_name(
            disease_name_key,
            language
        ),
        "is_healthy": disease_name_key.lower() == "healthy",
        "confidence": f"{confidence:.2f}",
        "cause": details["cause"],
        "symptoms": details["symptoms"],
        "solution": details["solution"]
    }


def render_home():
    language = get_language()

    context = {
        "lang": language,
        "ui": UI_TEXT[language],
        "prediction": False
    }

    last_prediction = session.get("last_prediction")

    if last_prediction:
        context.update(
            create_prediction_context(
                last_prediction["disease_key"],
                last_prediction["confidence"],
                language
            )
        )

    return render_template(
        "index.html",
        **context
    )


# -------------------------------------------------
# Home page
# -------------------------------------------------
@app.route("/")
def home():
    return render_home()


# -------------------------------------------------
# Change language
# -------------------------------------------------
@app.route(
    "/language/<language>",
    methods=["GET", "POST"]
)
def change_language(language):
    if language not in ("en", "kn"):
        language = "en"

    session["language"] = language

    if request.method == "POST":
        return jsonify({
            "success": True,
            "language": language
        })

    return redirect(url_for("home"))


# -------------------------------------------------
# Upload and predict
# -------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload_image():
    language = get_language()

    if "image" not in request.files:
        return jsonify({
            "error": UI_TEXT[language]["no_image"]
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "error": UI_TEXT[language]["no_file"]
        }), 400

    safe_name = secure_filename(file.filename)

    if not safe_name:
        return jsonify({
            "error": UI_TEXT[language]["invalid_file"]
        }), 400

    unique_name = f"{uuid4().hex}_{safe_name}"
    filepath = os.path.join(
        UPLOAD_FOLDER,
        unique_name
    )

    file.save(filepath)

    try:
        # Image preprocessing
        img = image.load_img(
            filepath,
            target_size=(224, 224)
        )

        img = image.img_to_array(img)
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        # Prediction
        prediction = model.predict(
            img,
            verbose=0
        )

        index = int(np.argmax(prediction))
        confidence = float(
            np.max(prediction)
        ) * 100

        disease_key = categories[index]

        print("Prediction:", disease_key)
        print("Confidence:", confidence)

        # Store result so it remains when language changes
        session["last_prediction"] = {
            "disease_key": disease_key,
            "confidence": confidence
        }

        context = {
            "lang": language,
            "ui": UI_TEXT[language]
        }

        context.update(
            create_prediction_context(
                disease_key,
                confidence,
                language
            )
        )

        return render_template(
            "index.html",
            **context
        )

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# -------------------------------------------------
# Clear previous prediction
# -------------------------------------------------
@app.route("/clear-result")
def clear_result():
    session.pop("last_prediction", None)
    return redirect(url_for("home"))


# -------------------------------------------------
# Run Flask
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)