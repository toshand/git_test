"""
要員アサイン管理アプリケーション - アプリケーション起動スクリプト

このスクリプトを実行してFlaskアプリケーションを起動します。
"""

import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
