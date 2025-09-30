#!/bin/bash
# HTML to Excel 変換スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境をアクティベート
source venv_html_converter/bin/activate

# HTML to Excel 変換プログラムを実行
python src/html_to_excel_converter.py "$@"


