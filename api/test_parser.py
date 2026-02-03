import sys
sys.stdout.reconfigure(encoding='utf-8')

from receipt_parser import parse_receipt

# レシート1: ザバスプロテインフルー ¥247、天然水 ¥108、合計 ¥355
text1 = """FamilyMart
北新宿店
東京都新宿区北新宿１ー１ー１７
電話：03-5338-3703
登録番号：T2011601026109
2024年12月13日（金）9:01
レジ 4-4617               責No. 999
領　収　証
ザバスプロテインフルー　¥247軽
◎天然水新潟県津南６０　¥108軽
合　計　　　　　　　　　¥355
（　８％対象　　　　　　¥355）
（内消費税等　　　　　　¥26）
交通系マネー支払　　　　¥355
交通系マネー残高　　　　¥341
（カード番号：PB*** **** **** 3602）"""

# レシート2: チョコバターメロンパ ¥168、合計 ¥168
text2 = """FamilyMart
北新宿店
2024年12月13日（金）9:15
レジ 4-8068               責No. 999
領　収　証
◎チョコバターメロンパ　¥168軽
合　計　　　　　　　　　¥168
（　８％対象　　　　　　¥168）
（内消費税等　　　　　　¥12）
交通系マネー支払　　　　¥168
交通系マネー残高　　　　¥4,902
（カード番号：JE*** **** **** 2823）
ファミマのアプリ ファミペイ限定
30円引き
クーポンを受け取ろう!"""

# レシート3: アポロチョコレート ¥198、合計 ¥198
text3 = """FamilyMart
北新宿店
2024年12月13日（金）9:08
レジ 4-2180               責No. 999
領　収　証
アポロチョコレート　¥198軽
合　計　　　　　　　¥198
（　８％対象　　　　¥198）
（内消費税等　　　　¥14）
交通系マネー支払　　¥198
交通系マネー残高　　¥462
（カード番号：PB*** **** **** 4203）"""

print("=" * 50)
print("レシート1のテスト")
print("期待: 合計=355, 商品: ザバスプロテインフルー ¥247, 天然水 ¥108")
result1 = parse_receipt(text1)
print(f"結果: 合計={result1['total']}")
print(f"商品: {result1['items']}")

print("\n" + "=" * 50)
print("レシート2のテスト")
print("期待: 合計=168, 商品: チョコバターメロンパ ¥168")
result2 = parse_receipt(text2)
print(f"結果: 合計={result2['total']}")
print(f"商品: {result2['items']}")

print("\n" + "=" * 50)
print("レシート3のテスト")
print("期待: 合計=198, 商品: アポロチョコレート ¥198")
result3 = parse_receipt(text3)
print(f"結果: 合計={result3['total']}")
print(f"商品: {result3['items']}")

# 結果判定
all_pass = True
if result1['total'] != 355:
    print(f"\n✗ レシート1: 合計が不正 (期待:355, 実際:{result1['total']})")
    all_pass = False
if result2['total'] != 168:
    print(f"\n✗ レシート2: 合計が不正 (期待:168, 実際:{result2['total']})")
    all_pass = False
if result3['total'] != 198:
    print(f"\n✗ レシート3: 合計が不正 (期待:198, 実際:{result3['total']})")
    all_pass = False

print("\n" + "=" * 50)
if all_pass:
    print("✓ 全てのテストに成功しました！")
else:
    print("✗ 一部のテストに失敗しました")
