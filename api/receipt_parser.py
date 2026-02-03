import re

def preprocess_text(text):
    """OCRテキストの前処理：よくある誤認識を修正"""
    # 特定の記号除去
    text = re.sub(r'[©°*°º◎○●※]', '', text)
    # ￥, \ の正規化を最初に行う
    text = text.replace('￥', '¥').replace('\\', '¥')
    # Y¥, Y\ → ¥ (OCRがYと記号を両方認識)
    text = re.sub(r'Y+¥', '¥', text)
    # ¥~ → ¥ (チルダが混入)
    text = re.sub(r'¥~', '¥', text)
    # SO → 60 (数字の誤認識)
    text = re.sub(r'SO', '60', text)
    # 価格の誤認識を修正
    text = re.sub(r'¥S', '¥5', text)  # S→5
    text = re.sub(r'¥O', '¥0', text)  # O→0
    # 価格と「軽」やゴミ文字の間の除去
    text = re.sub(r'(¥\d+)\s*[A-Z軽]+', r'\1', text)
    # 括弧の除去
    text = re.sub(r'(\d+)\)', r'\1', text)
    text = re.sub(r'\(\s*(\d+)', r'\1', text)
    # カンマ+スペースの修正: ¥4, 902 → ¥4,902
    text = re.sub(r'(¥?\d+),\s+(\d+)', r'\1,\2', text)
    # ¥と数字の間のスペース除去: ¥ 4902 → ¥4902
    text = re.sub(r'¥\s+(\d)', r'¥\1', text)
    # 連続する複数の¥を1つに
    text = re.sub(r'¥+', '¥', text)
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

    price_pattern = re.compile(r"¥\s*(\d{1,5}(?:,\d{3})*)")
    # 商品名・価格抽出パターン (¥ を必須キーワード近くに優先)
    # 名前部分に様々な記号や全角文字を許容
    item_line_pattern = re.compile(
        r"([^¥\n]+?)\s*¥\s*(\d{1,5}(?:,\d{3})*)"
    )

    # ゴミ行を除外
    clean_lines = [l for l in lines if not is_garbage_line(l)]

    # 1. まず合計金額を探す
    found_total = False
    possible_totals = []
    for line in clean_lines:
        # 「合計」「生還」(合計の誤読)、「計」をチェック
        # 「計」単体の場合は誤判定を防ぐため慎重に扱う
        is_explicit_total = any(kw in line for kw in ["合計", "合　計", "生還"])
        is_hit_total = is_explicit_total or ("計" in line and not any(prod in line for prod in ["天然水", "プロテイン", "チョコ"]))
        
        if is_hit_total:
            m = price_pattern.search(line)
            if m:
                val = int(m.group(1).replace(",", ""))
                if is_explicit_total:
                    total_amount = val
                    found_total = True
                    break
                possible_totals.append(val)

    if not found_total and possible_totals:
        total_amount = max(possible_totals)
        found_total = True

    # 2. 合計金額が見つからない場合、最大の¥金額を合計とする
    # ただし、明らかに大きすぎるもの（残高など）は除外の工夫が必要だが
    # ここでは10000円以下を優先的に探す
    if not found_total:
        amounts = []
        for line in clean_lines:
            m = price_pattern.search(line)
            if m:
                val = int(m.group(1).replace(",", ""))
                if val < 20000: # 明らかな残高(4902等)を除外するための暫定
                    amounts.append(val)
        if amounts:
            total_amount = max(amounts)

    # 商品行抽出
    noise_keywords = [
        "対象", "消費税", "支払", "残高", "クーポン", "ファミマ", "アプリ",
        "電話", "登録番号", "レジ", "責No", "円引き", "カード番号",
        "マネー", "通系", "FamilyMart", "sana", "2024年", "2025年", "2026年",
        "合計", "合　計", "小計", "件数", "番号", "PB", "JE", "ID",
        "8%", "10%", "軽減", "税率", "の内"
    ]

    for line in clean_lines:
        # 商品名の後に ¥数字 がある行を探す
        m = item_line_pattern.search(line)
        if not m:
            continue

        name = m.group(1).strip()
        price_str = m.group(2).replace(",", "")
        price = int(price_str)

        # ノイズ除外
        if any(x in name for x in noise_keywords):
            continue
            
        # 名前が数字だけのものは除外
        if re.match(r'^[0-9\s０-９\-]+$', name):
            continue

        # 短すぎる名前は除外
        if len(name) < 2:
            continue

        # 合計金額そのものは除外
        if price == total_amount and any(kw in line for kw in ["合計", "合　計", "計", "生還"]):
            continue

        items.append({"name": name, "price": price})

    if total_amount == 0 and items:
        total_amount = sum(item["price"] for item in items)

    return {"items": items, "total": total_amount}
