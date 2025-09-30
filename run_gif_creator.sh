#!/bin/bash
# アニメーションGIF作成ツール実行スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境をアクティベート
source venv/bin/activate

# GIF作成ツールを実行
python src/gif_creator.py
