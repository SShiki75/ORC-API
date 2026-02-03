import os
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import psutil

from receipt_parser import parse_receipt
from utils import resize_image, save_log

app = Flask(__name__)

@app.get("/")
def index():
    return "OCR API running"

@app.get("/memory")
def memory():
    mem = psutil.Process().memory_info().rss / (1024 * 1024)
    return {"memory_mb": mem}

@app.post("/ocr")
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    img = Image.open(file.stream)

    # 画像縮小（最重要）
    img = resize_image(img)

    # OCR
    text = pytesseract.image_to_string(img, lang="jpn+eng")

    # パース
    parsed = parse_receipt(text)

    # ログ保存（直近2件）
    save_log(text)

    return jsonify({
        "raw_text": text,
        "parsed": parsed
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
