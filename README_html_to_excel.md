# HTML to Excel 変換プログラム

HTMLファイルをレイアウトを保持したままExcelファイルに変換するPythonプログラムです。

## 機能

- HTMLファイルの読み込みと解析
- テーブルデータの自動抽出とExcelへの変換
- テキストコンテンツ（見出し、段落、リスト）の構造化された変換
- レイアウト情報の保持
- 複数のHTMLファイルの一括処理
- 詳細なログ機能とエラーハンドリング
- 美しいExcelフォーマット（色分け、フォント設定、列幅調整）

## 必要なライブラリ

```bash
pip install pandas openpyxl beautifulsoup4 lxml html5lib
```

または、requirements.txtを使用：

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 単一ファイル変換

```bash
python src/html_to_excel_converter.py input.html -o output.xlsx
```

### 2. 一括変換

```bash
python src/html_to_excel_converter.py input_directory --batch -o output_directory
```

### 3. ログレベル指定

```bash
python src/html_to_excel_converter.py input.html --log-level DEBUG
```

## コマンドライン引数

- `input`: 入力HTMLファイルまたはディレクトリのパス（必須）
- `-o, --output`: 出力Excelファイルまたはディレクトリのパス（省略時は自動生成）
- `-l, --log-level`: ログレベル（DEBUG, INFO, WARNING, ERROR）
- `--batch`: ディレクトリ内のHTMLファイルを一括変換

## 出力形式

変換されたExcelファイルには以下のシートが含まれます：

1. **サマリー**: 変換結果の概要
2. **テーブル_X**: 抽出されたテーブルデータ（複数ある場合）
3. **コンテンツ**: テキストコンテンツ（見出し、段落、リストなど）

## 使用例

### Pythonスクリプトでの使用

```python
from src.html_to_excel_converter import HTMLToExcelConverter

# コンバーターを初期化
converter = HTMLToExcelConverter(log_level="INFO")

# 単一ファイル変換
output_file = converter.convert_html_to_excel("input.html", "output.xlsx")

# 一括変換
converted_files = converter.batch_convert("input_directory", "output_directory")
```

### サンプル実行

```bash
python src/html_to_excel_example.py
```

## 対応するHTML要素

### テーブル
- `<table>`: 完全なテーブル構造を保持
- ヘッダー行の自動検出
- セル結合の対応

### テキストコンテンツ
- `<h1>` - `<h6>`: 見出し（レベル別のフォントサイズ）
- `<p>`: 段落
- `<ul>`, `<ol>`: リスト
- `<section>`, `<div>`: セクション

## スタイル設定

### テーブル
- ヘッダー行: 青背景、白文字、太字
- 列幅の自動調整
- 境界線の設定

### テキスト
- 見出し: レベルに応じたフォントサイズ
- 段落: 自動改行対応
- リスト: インデント設定

## エラーハンドリング

- ファイル読み込みエラー
- HTML解析エラー
- テーブル抽出エラー
- 詳細なログ出力

## ログファイル

変換処理のログは `html_to_excel_conversion.log` に保存されます。

## 制限事項

- 複雑なCSSレイアウトは完全には再現されません
- JavaScriptで動的に生成されるコンテンツは抽出できません
- 画像やメディアファイルはテキストとして処理されます

## トラブルシューティング

### よくある問題

1. **ファイルが見つからない**
   - ファイルパスが正しいか確認
   - ファイルの存在確認

2. **テーブルが抽出されない**
   - HTMLのテーブル構造が正しいか確認
   - ログレベルをDEBUGに設定して詳細を確認

3. **文字化け**
   - HTMLファイルの文字エンコーディングがUTF-8か確認

### デバッグ方法

```bash
python src/html_to_excel_converter.py input.html --log-level DEBUG
```

## ライセンス

このプログラムはMITライセンスの下で提供されています。

## 貢献

バグ報告や機能要望は、GitHubのIssuesページでお知らせください。

## 更新履歴

- v1.0.0: 初回リリース
  - 基本的なHTML to Excel変換機能
  - テーブルとテキストコンテンツの抽出
  - 一括変換機能
  - ログ機能


