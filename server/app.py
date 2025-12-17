from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import numpy as np
import cv2
import HelperFunction
import base64
import re
import os
import gdown  # for downloading from Google Drive
cv2.ocl.setUseOpenCL(False)  # Disable OpenCL
cv2.setNumThreads(0) 
app = Flask(__name__, template_folder='../client', static_folder='../client')

# ---------------------------
# Model setup
# ---------------------------
MODEL_PATH = "playingCards.pt"  # Save in same directory as app.py
MODEL_URL = "https://drive.google.com/uc?id=1AgTsbIcYQXAFubcEoJVVfOXPA7pmwTJA"

# Download model if it doesn't exist
if not os.path.exists(MODEL_PATH):
    print("Downloading YOLO model from Google Drive...")
    gdown.download(MODEL_URL, MODEL_PATH, quiet=False)
    print("Model downloaded successfully!")

# ---------------------------
# YOLO lazy load
# ---------------------------
model = None
def get_model():
    global model
    if model is None:
        model = YOLO(MODEL_PATH)
        model.to("cpu")
    return model

# ---------------------------
# Card names
# ---------------------------
classNames = [
    '10C','10D','10H','10S','2C','2D','2H','2S','3C','3D','3H','3S',
    '4C','4D','4H','4S','5C','5D','5H','5S','6C','6D','6H','6S',
    '7C','7D','7H','7S','8C','8D','8H','8S','9C','9D','9H','9S',
    'AC','AD','AH','AS','JC','JD','JH','JS','KC','KD','KH','KS',
    'QC','QD','QH','QS'
]

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/detect', methods=['POST'])
def detect():
    data = request.json['image']
    img_data = re.sub('^data:image/.+;base64,', '', data)
    nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    model = get_model()
    results = model(img)
    
    detected = []
    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            if conf > 0.5:
                detected.append(classNames[cls])

    detected = list(set(detected))
    poker_hand = "Not enough cards detected"
    if len(detected) >= 5:
        poker_hand = HelperFunction.findPokerHand(detected[:5])

    return jsonify({
        "cards": detected,
        "hand": poker_hand
    })

# ---------------------------
# Run locally
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
