import sys
sys.stdout.reconfigure(encoding='utf-8')

from receipt_parser import parse_receipt

# レシート1: ザバスプロテインフルー ¥247、天然水 ¥108、合計 ¥355
text1 = r"""FamilyMart
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
text2 = r"""FamilyMart
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
text3 = r"""FamilyMart
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

# 最新ログ1: アポロチョコレート ¥198 (¥1998R)
text4 = r"""ere 導還
Perey     HT
aa FamilyMart
    北新宿店
東京都新宿区北新宿キートー1 7 PS
電話 : 03-5338-3703
登録番号 : 12011601026109
2024年12月13日 (金) 9:08   —
ツバ  4-2180_ 2 責No. 999   —
アポボロチョコレート © ¥1998R
生還       ¥198
( 8 6K       ¥198)
MP wth
ea です
交通系マ+-残                   \46 2
UES : en  ※ネ※※ ※ポ※※ 4203)"""

# 最新ログ2: ザバス ¥247(未取得?), 天然水 ¥108, 合計 ¥355
text5 = r"""nee           °
ea  FamilyMart |
北新宿店                         |
RRA ALL - 1-17 |
| EE : 03-5338-3703               |
登録番号 : 12011601026109
| 2024年12月13日 (金) 9:01          |
BS 4-4017 BRN. 999
.        領収 証-    —
ザパスプロテイソンフルー  MM  =
@天然水新潟県津南SO  Y\108軽 靖計計
( 8%対旬       \355) i
(内消費税等             \26) |
交通系?支払           ¥~355
『「軽」は軽減税率対象商品です。
交通系マネ-残高             \341        |
(カト「 番号 :PB**x KK ** 3602)"""

print("=" * 50)
print("最新ログ1のテスト")
print("期待: 合計=198, 商品: アポボロチョコレート")
result4 = parse_receipt(text4)
print(f"結果: 合計={result4['total']}")
print(f"商品: {result4['items']}")

print("\n" + "=" * 50)
print("最新ログ2のテスト")
print("期待: 合計=355, 商品: 天然水新潟県津南60")
result5 = parse_receipt(text5)
print(f"結果: 合計={result5['total']}")
print(f"商品: {result5['items']}")

# 全体結果判定
all_pass = True
if result1['total'] != 355:
    print(f"\n✗ レシート1: 合計が不正")
    all_pass = False
if result2['total'] != 168:
    print(f"\n✗ レシート2: 合計が不正")
    all_pass = False
if result3['total'] != 198:
    print(f"\n✗ レシート3: 合計が不正")
    all_pass = False
if result4['total'] != 198:
    print(f"\n✗ 最新ログ1: 合計が不正 (期待:198, 実際:{result4['total']})")
    all_pass = False
if result5['total'] != 355:
    print(f"\n✗ 最新ログ2: 合計が不正 (期待:355, 実際:{result5['total']})")
    all_pass = False

print("\n" + "=" * 50)
if all_pass:
    print("✓ 全てのテストに成功しました！")
else:
    print("✗ 一部のテストに失敗しました")
