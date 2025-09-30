#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQLデータベースセットアップスクリプト
TODO管理アプリケーション用のデータベースとテーブルを作成します。

使用方法:
1. PostgreSQLがインストールされ、サービスが起動していることを確認
2. 環境変数を設定（オプション）
3. python setup_postgresql.py を実行

環境変数:
- DB_HOST: データベースホスト (デフォルト: localhost)
- DB_PORT: データベースポート (デフォルト: 5432)
- DB_NAME: データベース名 (デフォルト: todo_app)
- DB_USER: データベースユーザー (デフォルト: postgres)
- DB_PASSWORD: データベースパスワード (デフォルト: password)
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database():
    """データベースを作成"""
    # 接続パラメータ
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '5432'))
    database = os.getenv('DB_NAME', 'todo_app')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'password')
    
    print(f"PostgreSQLデータベースセットアップを開始します...")
    print(f"ホスト: {host}:{port}")
    print(f"データベース: {database}")
    print(f"ユーザー: {user}")
    
    try:
        # まずpostgresデータベースに接続してデータベースを作成
        conn = psycopg2.connect(
            host=host,
            port=port,
            database='postgres',  # デフォルトデータベース
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # データベースが存在するかチェック
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            if cursor.fetchone():
                print(f"データベース '{database}' は既に存在します。")
            else:
                # データベースを作成
                cursor.execute(f'CREATE DATABASE "{database}"')
                print(f"データベース '{database}' を作成しました。")
        
        conn.close()
        
        # 作成したデータベースに接続してテーブルを作成
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        with conn.cursor() as cursor:
            # テーブルを作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    priority VARCHAR(10) DEFAULT '中',
                    due_date DATE,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP
                )
            ''')
            
            # インデックスを作成（パフォーマンス向上のため）
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_todos_completed 
                ON todos(completed)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_todos_priority 
                ON todos(priority)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_todos_due_date 
                ON todos(due_date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_todos_created_at 
                ON todos(created_at)
            ''')
            
            conn.commit()
            print("テーブル 'todos' を作成しました。")
            print("インデックスを作成しました。")
        
        conn.close()
        print("セットアップが完了しました！")
        return True
        
    except psycopg2.Error as e:
        print(f"エラーが発生しました: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return False


def test_connection():
    """データベース接続をテスト"""
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '5432'))
    database = os.getenv('DB_NAME', 'todo_app')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'password')
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"PostgreSQL接続テスト成功: {version}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"接続テスト失敗: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TODO管理アプリケーション - PostgreSQLセットアップ")
    print("=" * 60)
    
    # 接続テスト
    print("\n1. データベース接続をテスト中...")
    if not test_connection():
        print("\nPostgreSQLに接続できません。以下を確認してください:")
        print("- PostgreSQLがインストールされているか")
        print("- PostgreSQLサービスが起動しているか")
        print("- 接続情報（ホスト、ポート、ユーザー、パスワード）が正しいか")
        print("- 環境変数が正しく設定されているか")
        sys.exit(1)
    
    # データベース作成
    print("\n2. データベースとテーブルを作成中...")
    if create_database():
        print("\n✅ セットアップが正常に完了しました！")
        print("\nTODO管理アプリケーションを起動できます:")
        print("python main.py")
    else:
        print("\n❌ セットアップに失敗しました。")
        sys.exit(1)
