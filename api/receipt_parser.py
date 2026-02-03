import re

def parse_receipt(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = []
    total_amount = 0

    price_pattern = re.compile(r"(\d{1,3}(?:,\d{3})*)")
    item_line_pattern = re.compile(
        r"([ぁ-んァ-ン一-龥A-Za-z0-9ー・\-\s]+?)\s+(\d{1,3}(?:,\d{3})*)"
    )

    # 領収証の位置
    receipt_index = None
    for i, line in enumerate(lines):
        if "領収" in line:
            receipt_index = i
            break

    # 領収証の上下どちらに商品があるか判定
    if receipt_index is not None:
        upper = lines[:receipt_index]
        lower = lines[receipt_index + 1:]

        def score(block):
            return sum(1 for l in block if price_pattern.search(l))

        target_lines = upper if score(upper) > score(lower) else lower
    else:
        target_lines = lines

    # 合計金額
    for line in target_lines:
        if "合計" in line:
            m = price_pattern.search(line)
            if m:
                total_amount = int(m.group(1).replace(",", ""))

    # 商品行抽出
    for line in target_lines:
        m = item_line_pattern.search(line)
        if not m:
            continue

        name = m.group(1).strip()
        price = int(m.group(2).replace(",", ""))

        # ノイズ除外
        if any(x in name for x in [
            "対象","消費税","支払","残高","クーポン","ファミマ","アプリ",
            "東京都","電話","登録番号","レジ","責No","円引き","カード番号"
        ]):
            continue

        if len(name) < 2:
            continue

        items.append({"name": name, "price": price})

    if total_amount == 0 and items:
        total_amount = sum(item["price"] for item in items)

    return {"items": items, "total": total_amount}
