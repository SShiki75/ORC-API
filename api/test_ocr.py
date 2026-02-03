"""
レシート画像のOCR前処理テスト
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image
from utils import preprocess_for_ocr, resize_image

# テスト用画像パス
image_paths = [
    r"C:/Users/fuumi/.gemini/antigravity/brain/e9b06abc-6132-4379-ab69-e5473572cd4c/uploaded_media_0_1770134291038.jpg",
    r"C:/Users/fuumi/.gemini/antigravity/brain/e9b06abc-6132-4379-ab69-e5473572cd4c/uploaded_media_1_1770134291038.jpg",
    r"C:/Users/fuumi/.gemini/antigravity/brain/e9b06abc-6132-4379-ab69-e5473572cd4c/uploaded_media_2_1770134291038.jpg",
]

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False

from receipt_parser import parse_receipt

for i, path in enumerate(image_paths, 1):
    print(f"\n{'='*60}")
    print(f"レシート {i}")
    print('='*60)
    
    try:
        img = Image.open(path)
        img = resize_image(img)
        img_processed = preprocess_for_ocr(img)
        
        # 処理後画像を保存（確認用）
        output_path = f"processed_receipt_{i}.png"
        img_processed.save(output_path)
        print(f"前処理済み画像を保存: {output_path}")
        
        if TESSERACT_AVAILABLE:
            custom_config = r'--psm 6 --oem 3'
            text = pytesseract.image_to_string(img_processed, lang="jpn+eng", config=custom_config)
            print(f"\nOCR結果:")
            print("-" * 40)
            print(text[:500])  # 最初の500文字
            print("-" * 40)
            
            result = parse_receipt(text)
            print(f"\n解析結果:")
            print(f"  合計: ¥{result['total']}")
            print(f"  商品: {result['items']}")
        else:
            print("Tesseractがインストールされていません")
    except Exception as e:
        print(f"エラー: {e}")
