from PIL import Image, ImageFilter, ImageOps, ImageEnhance

def resize_image(img, max_size=1500):
    """画像をリサイズ（OCR精度のため少し大きめに）"""
    img.thumbnail((max_size, max_size))
    return img

def preprocess_for_ocr(img):
    """
    レシート画像のOCR前処理
    - グレースケール化
    - コントラスト強調
    - シャープ化
    """
    # RGBに変換（透明度チャンネルがある場合の対策）
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # グレースケール化
    img = ImageOps.grayscale(img)
    
    # コントラスト強調（適度に）
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # 明るさ調整（レシートを明るく）
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.1)
    
    # シャープ化
    img = img.filter(ImageFilter.SHARPEN)
    
    # ノイズ除去（軽めのぼかし後にシャープ化）
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.filter(ImageFilter.SHARPEN)
    
    return img

def save_log(entry, path="logs.txt"):
    """OCRログを保存（直近2件のみ）"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_entry = f"--- {timestamp} ---\n{entry}\n"
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        content = ""
    
    # 区切り文字で分割して直近2件を保持
    entries = content.split("--- ")
    entries = [e for e in entries if e.strip()]
    entries.append(f"{timestamp} ---\n{entry}\n")
    entries = entries[-2:]  # 直近2件だけ
    
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write("--- " + e)
