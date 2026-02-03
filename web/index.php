<?php
session_start();

// 設定
// 後でデプロイした Render アプリの URL に変更してください
$api_url = 'https://receipt-ocr-api-1.onrender.com';
$log_file = 'ocr.log';

// Clear old session data on fresh page load to ensure state is transient
if ($_SERVER['REQUEST_METHOD'] === 'GET' && (!isset($_GET['action']) || $_GET['action'] !== 'download')) {
    unset($_SESSION['last_result']);
}

$result = null;
$error = null;

// CSV ダウンロードの処理
if (isset($_GET['action']) && $_GET['action'] === 'download' && isset($_SESSION['last_result'])) {
    $data = $_SESSION['last_result'];

    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="receipt_' . date('YmdHis') . '.csv"');

    $output = fopen('php://output', 'w');

    // Excel 互換性のために BOM を追加
    fputs($output, "\xEF\xBB\xBF");

    fputcsv($output, ['商品名', '価格']);

    if (isset($data['parsed_data']['items'])) {
        foreach ($data['parsed_data']['items'] as $item) {
            fputcsv($output, [$item['name'], $item['price']]);
        }
    }

    // 合計行を追加
    if (isset($data['parsed_data']['total'])) {
        fputcsv($output, ['', '']);
        fputcsv($output, ['合計', $data['parsed_data']['total']]);
    }

    fclose($output);
    exit;
}

// ファイルアップロードの処理
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['receipt_image'])) {
    if ($_FILES['receipt_image']['error'] === UPLOAD_ERR_OK) {
        $tmp_name = $_FILES['receipt_image']['tmp_name'];
        $file_name = $_FILES['receipt_image']['name'];
        $cfile = new CURLFile($tmp_name, $_FILES['receipt_image']['type'], $file_name);

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $api_url);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, ['image' => $cfile]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        // ローカル環境や適切な証明書がない無料ホスティングでのテスト用に SSL 検証を無効化する必要がある場合があります
        // curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); 

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        if (curl_errno($ch)) {
            $error = 'Curl エラー: ' . curl_error($ch);
        } elseif ($http_code !== 200) {
            $error = 'API エラー: ' . $response;
        } else {
            $data = json_decode($response, true);
            if ($data) {
                $result = $data;
                $_SESSION['last_result'] = $data;

                // 生テキストのログ記録 (直近2件のみ保持)
                if (isset($data['raw_text'])) {
                    $current_log = file_exists($log_file) ? file_get_contents($log_file) : '';
                    $new_entry = "--- " . date('Y-m-d H:i:s') . " ---\n" . $data['raw_text'] . "\n\n";

                    // 区切り文字で分割
                    $pattern = '/(--- \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ---)/';
                    $parts = preg_split($pattern, $current_log . $new_entry, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);

                    // 直近2件（ヘッダー+本文で1件なので、最大4要素）を保持
                    $keep_parts = array_slice($parts, -4);
                    $new_log_content = implode('', $keep_parts);

                    file_put_contents($log_file, $new_log_content);
                }
            } else {
                $error = 'API から無効な JSON レスポンスが返されました';
            }
        }
        curl_close($ch);
    } else {
        $error = 'アップロードエラー (コード: ' . $_FILES['receipt_image']['error'] . ')';
    }
}
?>
<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Easy Receipt OCR</title>
    <link rel="stylesheet" href="style.css">
    <link
        href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Outfit:wght@400;700&display=swap"
        rel="stylesheet">
</head>

<body>
    <div class="container">
        <header>
            <h1>Receipt OCR</h1>
            <p>簡単・無料・登録不要のレシート読み取り</p>
        </header>

        <section class="upload-section">
            <form action="" method="post" enctype="multipart/form-data" id="uploadForm">
                <label for="fileInput" class="upload-label">
                    <span class="icon">📷</span>
                    <span class="text">レシートを撮影 / 選択</span>
                </label>
                <input type="file" name="receipt_image" id="fileInput" accept="image/*" capture="environment" hidden
                    onchange="document.getElementById('uploadForm').submit(); document.getElementById('loading').style.display='block';">
            </form>
            <div id="loading" style="display:none; margin-top: 20px;">
                <div class="spinner"></div>
                <p>解析中...</p>
            </div>
        </section>

        <?php if ($error): ?>
            <div class="alert error">
                <?= htmlspecialchars($error) ?>
            </div>
        <?php endif; ?>

        <?php if ($result): ?>
            <section class="result-section">
                <h2>解析結果</h2>

                <div class="total-display">
                    <span class="label">合計金額</span>
                    <span class="amount">¥<?= number_format($result['parsed_data']['total'] ?? 0) ?></span>
                </div>

                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>商品名</th>
                                <th>価格</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php if (isset($result['parsed_data']['items']) && count($result['parsed_data']['items']) > 0): ?>
                                <?php foreach ($result['parsed_data']['items'] as $item): ?>
                                    <tr>
                                        <td><?= htmlspecialchars($item['name']) ?></td>
                                        <td>¥<?= number_format($item['price']) ?></td>
                                    </tr>
                                <?php endforeach; ?>
                            <?php else: ?>
                                <tr>
                                    <td colspan="2" style="text-align:center;">明細をうまく読み取れませんでした</td>
                                </tr>
                            <?php endif; ?>
                        </tbody>
                    </table>
                </div>

                <div class="actions">
                    <a href="?action=download" class="btn download-btn">CSV ダウンロード</a>
                    <a href="ocr.log" class="btn log-btn" target="_blank">ログ確認 (検証用)</a>
                </div>

                <details class="raw-text">
                    <summary>認識された生テキストを表示</summary>
                    <pre><?= htmlspecialchars($result['raw_text'] ?? '') ?></pre>
                </details>
            </section>
        <?php endif; ?>
    </div>
</body>

</html>