from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import numpy as np
import cv2
import HelperFunction
import base64
import re
import os

app = Flask(__name__, template_folder='../client', static_folder='../client')

model = None

def get_model():
    global model
    if model is None:
        model = YOLO("models/playingCards.pt")
    return model

# model = YOLO(os.path.join("models", "playingCards.pt"))

classNames = [
    '10C','10D','10H','10S','2C','2D','2H','2S','3C','3D','3H','3S',
    '4C','4D','4H','4S','5C','5D','5H','5S','6C','6D','6H','6S',
    '7C','7D','7H','7S','8C','8D','8H','8S','9C','9D','9H','9S',
    'AC','AD','AH','AS','JC','JD','JH','JS','KC','KD','KH','KS',
    'QC','QD','QH','QS'
]

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
