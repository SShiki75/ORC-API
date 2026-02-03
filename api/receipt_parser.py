import re

def preprocess_text(text):
    """OCRテキストの前処理：よくある誤認識を修正"""
    # 価格の誤認識を修正
    text = re.sub(r'¥S', '¥5', text)  # S→5
    text = re.sub(r'¥O', '¥0', text)  # O→0
    text = re.sub(r'\\(\d)', r'¥\1', text)  # \108 → ¥108
    text = re.sub(r'(\d+)\s*軽', r'\1', text)  # 108軽 → 108
    text = re.sub(r'(\d+)\)', r'\1', text)  # 355) → 355
    text = re.sub(r'\(\s*(\d+)', r'\1', text)  # (26 → 26
    return text

def is_garbage_line(line):
    """ゴミ行を判定"""
    garbage_keywords = [
        "クーポン", "アプリ", "QRコード", "ダウンロード", "会員",
        "ギフトコード", "タップ", "受け取", "ストア", "限定",
        "こちらの", "から!", "入力", "確認", "送移",
        "FENo", "責No", "レジ", "電話", "登録番号",
        "東京都", "新宿", "渋谷", "港区", "千代田",
        "OMVERY", "xHIOK", "XXX", "※※", "**",
    ]
    # ゴミキーワードを含む
    if any(kw in line for kw in garbage_keywords):
        return True
    # 英字のみの短い行（誤認識されたゴミ）
    if re.match(r'^[A-Za-z\s\-|=]+$', line) and len(line) < 20:
        return True
    # 意味不明な記号列
    if re.match(r'^[\|\-=\s]+$', line):
        return True
    return False

def extract_price(line):
    """行から価格を抽出"""
    # ¥ + 数字パターン
    m = re.search(r'[¥\\￥][\s,]*(\d{1,3}(?:,?\d{3})*)', line)
    if m:
        return int(m.group(1).replace(",", ""))
    # 末尾の数字パターン（商品名 + 価格）
    m = re.search(r'\s(\d{2,5})\s*$', line)
    if m:
        return int(m.group(1))
    return None

def parse_receipt(text):
    # 前処理
    text = preprocess_text(text)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = []
    total_amount = 0

    price_pattern = re.compile(r"(\d{1,3}(?:,\d{3})*)")
    item_line_pattern = re.compile(
        r"([ぁ-んァ-ン一-龥A-Za-z0-9ー・\-\s]+?)\s+[¥\\￥]?(\d{1,3}(?:,\d{3})*)"
    )

    # ゴミ行を除外
    clean_lines = [l for l in lines if not is_garbage_line(l)]

    # 領収証の位置
    receipt_index = None
    for i, line in enumerate(clean_lines):
        if "領収" in line:
            receipt_index = i
            break

    # 領収証の上下どちらに商品があるか判定
    if receipt_index is not None:
        upper = clean_lines[:receipt_index]
        lower = clean_lines[receipt_index + 1:]

        def score(block):
            return sum(1 for l in block if price_pattern.search(l))

        target_lines = upper if score(upper) > score(lower) else lower
    else:
        target_lines = clean_lines

    # 合計金額を探す（複数パターン対応）
    for line in target_lines:
        if "合計" in line or "計" in line:
            m = price_pattern.search(line)
            if m:
                total_amount = int(m.group(1).replace(",", ""))
                break

    # 直接¥マークで始まる大きな金額も合計として検出
    if total_amount == 0:
        for line in lines:
            m = re.search(r'[¥\\￥]\s*(\d{1,3}(?:,\d{3})*)', line)
            if m:
                amount = int(m.group(1).replace(",", ""))
                if amount > 500:  # 合計は通常大きい
                    total_amount = amount
                    break

    # 商品行抽出
    noise_keywords = [
        "対象", "消費税", "支払", "残高", "クーポン", "ファミマ", "アプリ",
        "電話", "登録番号", "レジ", "責No", "円引き", "カード番号",
        "マネー", "通系", "FamilyMart", "sana", "2024年", "2025年", "2026年"
    ]

    for line in target_lines:
        m = item_line_pattern.search(line)
        if not m:
            continue

        name = m.group(1).strip()
        price = int(m.group(2).replace(",", ""))

        # ノイズ除外
        if any(x in name for x in noise_keywords):
            continue

        # 短すぎる名前は除外
        if len(name) < 2:
            continue

        # 価格が不自然に大きい/小さい場合は除外
        if price < 10 or price > 10000:
            continue

        items.append({"name": name, "price": price})

    if total_amount == 0 and items:
        total_amount = sum(item["price"] for item in items)

    return {"items": items, "total": total_amount}
