#!/usr/bin/env python3
"""
要員アサイン管理アプリケーション起動スクリプト

このスクリプトを使用してアプリケーションを起動します。
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app import create_app

if __name__ == "__main__":
    print("要員アサイン管理システムを起動しています...")
    print("ブラウザで http://localhost:5001 にアクセスしてください")
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
