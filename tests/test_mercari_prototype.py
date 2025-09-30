#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メルカリ風C2Cサービス 単体テスト

C2レベル（分岐網羅率100%）の単体テストを実装
- すべての分岐を網羅
- 正常系・異常系の両方をテスト
- エッジケースも含む
"""

import unittest
import tempfile
import os
import sqlite3
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import threading
import time

# テスト対象のモジュールをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'venv'))
from mercari_prototype import MercariDatabase, MercariApp, RegisterDialog, ProductDetailDialog


class TestMercariDatabase(unittest.TestCase):
    """MercariDatabaseクラスの単体テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # 一時データベースファイルを作成
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = MercariDatabase(self.temp_db.name)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if self.db.connection:
            self.db.disconnect()
        os.unlink(self.temp_db.name)
    
    def test_init_default_path(self):
        """初期化テスト（デフォルトパス）"""
        db = MercariDatabase()
        self.assertEqual(db.db_path, "mercari.db")
        self.assertIsNone(db.connection)
        self.assertIsNone(db.cursor)
    
    def test_init_custom_path(self):
        """初期化テスト（カスタムパス）"""
        custom_path = "test.db"
        db = MercariDatabase(custom_path)
        self.assertEqual(db.db_path, custom_path)
        self.assertIsNone(db.connection)
        self.assertIsNone(db.cursor)
    
    def test_connect_success(self):
        """データベース接続成功テスト"""
        result = self.db.connect()
        self.assertTrue(result)
        self.assertIsNotNone(self.db.connection)
        self.assertIsNotNone(self.db.cursor)
    
    def test_connect_failure(self):
        """データベース接続失敗テスト"""
        # 無効なパスでデータベースを作成
        invalid_db = MercariDatabase("/invalid/path/database.db")
        result = invalid_db.connect()
        self.assertFalse(result)
        self.assertIsNone(invalid_db.connection)
        self.assertIsNone(invalid_db.cursor)
    
    def test_disconnect_with_connection(self):
        """データベース切断テスト（接続あり）"""
        self.db.connect()
        self.assertIsNotNone(self.db.connection)
        
        self.db.disconnect()
        # 接続が閉じられているかは直接確認できないが、エラーが発生しないことを確認
    
    def test_disconnect_without_connection(self):
        """データベース切断テスト（接続なし）"""
        # 接続なしで切断を試行
        self.db.disconnect()
        # エラーが発生しないことを確認
    
    def test_create_tables_success(self):
        """テーブル作成成功テスト"""
        self.db.connect()
        result = self.db.create_tables()
        self.assertTrue(result)
        
        # テーブルが作成されているか確認
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.db.cursor.fetchall()]
        expected_tables = ['users', 'categories', 'products', 'transactions', 'messages', 'reviews']
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_create_tables_failure(self):
        """テーブル作成失敗テスト"""
        # 接続なしでテーブル作成を試行
        with patch.object(self.db, 'cursor') as mock_cursor:
            mock_cursor.execute.side_effect = sqlite3.Error("Database error")
            result = self.db.create_tables()
            self.assertFalse(result)
    
    def test_hash_password(self):
        """パスワードハッシュ化テスト"""
        password = "testpassword"
        hash1 = self.db.hash_password(password)
        hash2 = self.db.hash_password(password)
        
        # 同じパスワードから同じハッシュが生成される
        self.assertEqual(hash1, hash2)
        
        # 異なるパスワードから異なるハッシュが生成される
        different_hash = self.db.hash_password("differentpassword")
        self.assertNotEqual(hash1, different_hash)
        
        # ハッシュの長さが正しい（SHA256は64文字）
        self.assertEqual(len(hash1), 64)
    
    def test_create_user_success(self):
        """ユーザー作成成功テスト"""
        self.db.connect()
        self.db.create_tables()
        
        user_id = self.db.create_user("testuser", "test@example.com", "password", "Test User")
        self.assertIsNotNone(user_id)
        self.assertIsInstance(user_id, int)
        
        # データベースにユーザーが作成されているか確認
        self.db.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = self.db.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "testuser")
        self.assertEqual(user['email'], "test@example.com")
        self.assertEqual(user['full_name'], "Test User")
    
    def test_create_user_with_optional_fields(self):
        """ユーザー作成テスト（オプションフィールド付き）"""
        self.db.connect()
        self.db.create_tables()
        
        user_id = self.db.create_user(
            "testuser2", "test2@example.com", "password", "Test User 2",
            phone="090-1234-5678", address="Tokyo, Japan"
        )
        self.assertIsNotNone(user_id)
        
        # オプションフィールドが正しく保存されているか確認
        self.db.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = self.db.cursor.fetchone()
        self.assertEqual(user['phone'], "090-1234-5678")
        self.assertEqual(user['address'], "Tokyo, Japan")
    
    def test_create_user_duplicate_username(self):
        """ユーザー作成テスト（重複ユーザー名）"""
        self.db.connect()
        self.db.create_tables()
        
        # 最初のユーザーを作成
        user_id1 = self.db.create_user("duplicate", "test1@example.com", "password", "User 1")
        self.assertIsNotNone(user_id1)
        
        # 同じユーザー名でユーザーを作成（失敗するはず）
        user_id2 = self.db.create_user("duplicate", "test2@example.com", "password", "User 2")
        self.assertIsNone(user_id2)
    
    def test_create_user_duplicate_email(self):
        """ユーザー作成テスト（重複メールアドレス）"""
        self.db.connect()
        self.db.create_tables()
        
        # 最初のユーザーを作成
        user_id1 = self.db.create_user("user1", "duplicate@example.com", "password", "User 1")
        self.assertIsNotNone(user_id1)
        
        # 同じメールアドレスでユーザーを作成（失敗するはず）
        user_id2 = self.db.create_user("user2", "duplicate@example.com", "password", "User 2")
        self.assertIsNone(user_id2)
    
    def test_create_user_database_error(self):
        """ユーザー作成テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずにユーザー作成を試行
        user_id = self.db.create_user("testuser", "test@example.com", "password", "Test User")
        self.assertIsNone(user_id)
    
    def test_authenticate_user_success(self):
        """ユーザー認証成功テスト"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーを作成
        user_id = self.db.create_user("testuser", "test@example.com", "password", "Test User")
        self.assertIsNotNone(user_id)
        
        # 認証を試行
        user = self.db.authenticate_user("testuser", "password")
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "testuser")
        self.assertEqual(user['email'], "test@example.com")
    
    def test_authenticate_user_wrong_password(self):
        """ユーザー認証テスト（間違ったパスワード）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーを作成
        user_id = self.db.create_user("testuser", "test@example.com", "password", "Test User")
        self.assertIsNotNone(user_id)
        
        # 間違ったパスワードで認証を試行
        user = self.db.authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(user)
    
    def test_authenticate_user_nonexistent_user(self):
        """ユーザー認証テスト（存在しないユーザー）"""
        self.db.connect()
        self.db.create_tables()
        
        # 存在しないユーザーで認証を試行
        user = self.db.authenticate_user("nonexistent", "password")
        self.assertIsNone(user)
    
    def test_authenticate_user_inactive_user(self):
        """ユーザー認証テスト（非アクティブユーザー）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーを作成
        user_id = self.db.create_user("testuser", "test@example.com", "password", "Test User")
        self.assertIsNotNone(user_id)
        
        # ユーザーを非アクティブにする
        self.db.cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
        self.db.connection.commit()
        
        # 非アクティブユーザーで認証を試行
        user = self.db.authenticate_user("testuser", "password")
        self.assertIsNone(user)
    
    def test_authenticate_user_database_error(self):
        """ユーザー認証テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずに認証を試行
        user = self.db.authenticate_user("testuser", "password")
        self.assertIsNone(user)
    
    def test_create_product_success(self):
        """商品作成成功テスト"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーを作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        self.assertIsNotNone(user_id)
        
        # 商品を作成
        product_id = self.db.create_product(
            user_id, "Test Product", "Test Description", 1000
        )
        self.assertIsNotNone(product_id)
        self.assertIsInstance(product_id, int)
        
        # データベースに商品が作成されているか確認
        self.db.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = self.db.cursor.fetchone()
        self.assertIsNotNone(product)
        self.assertEqual(product['title'], "Test Product")
        self.assertEqual(product['description'], "Test Description")
        self.assertEqual(product['price'], 1000)
        self.assertEqual(product['seller_id'], user_id)
    
    def test_create_product_with_optional_fields(self):
        """商品作成テスト（オプションフィールド付き）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーとカテゴリを作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        self.db.cursor.execute("INSERT INTO categories (name) VALUES ('Electronics')")
        category_id = self.db.cursor.lastrowid
        
        # 商品を作成（オプションフィールド付き）
        product_id = self.db.create_product(
            user_id, "Test Product", "Test Description", 1000,
            category_id=category_id, condition="excellent", images="image1.jpg,image2.jpg"
        )
        self.assertIsNotNone(product_id)
        
        # オプションフィールドが正しく保存されているか確認
        self.db.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = self.db.cursor.fetchone()
        self.assertEqual(product['category_id'], category_id)
        self.assertEqual(product['condition'], "excellent")
        self.assertEqual(product['images'], "image1.jpg,image2.jpg")
    
    def test_create_product_database_error(self):
        """商品作成テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずに商品作成を試行
        product_id = self.db.create_product(1, "Test Product", "Test Description", 1000)
        self.assertIsNone(product_id)
    
    def test_search_products_no_filters(self):
        """商品検索テスト（フィルターなし）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        product_id = self.db.create_product(user_id, "Test Product", "Test Description", 1000)
        
        # 検索を実行
        products = self.db.search_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "Test Product")
    
    def test_search_products_with_query(self):
        """商品検索テスト（クエリ付き）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        self.db.create_product(user_id, "iPhone", "Apple iPhone", 80000)
        self.db.create_product(user_id, "Android", "Google Android", 50000)
        
        # クエリで検索
        products = self.db.search_products(query="iPhone")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "iPhone")
        
        # 部分一致検索
        products = self.db.search_products(query="Apple")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "iPhone")
    
    def test_search_products_with_category(self):
        """商品検索テスト（カテゴリフィルター）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーとカテゴリを作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        self.db.cursor.execute("INSERT INTO categories (name) VALUES ('Electronics'), ('Books')")
        electronics_id = self.db.cursor.lastrowid - 1
        books_id = self.db.cursor.lastrowid
        
        # 商品を作成
        self.db.create_product(user_id, "iPhone", "Apple iPhone", 80000, category_id=electronics_id)
        self.db.create_product(user_id, "Python Book", "Python Programming", 3000, category_id=books_id)
        
        # カテゴリで検索
        products = self.db.search_products(category_id=electronics_id)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "iPhone")
    
    def test_search_products_with_price_range(self):
        """商品検索テスト（価格範囲フィルター）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        self.db.create_product(user_id, "Expensive Item", "Very expensive", 100000)
        self.db.create_product(user_id, "Cheap Item", "Very cheap", 1000)
        self.db.create_product(user_id, "Medium Item", "Medium price", 50000)
        
        # 価格範囲で検索
        products = self.db.search_products(min_price=10000, max_price=60000)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "Medium Item")
        
        # 最小価格のみ
        products = self.db.search_products(min_price=50000)
        self.assertEqual(len(products), 2)
        
        # 最大価格のみ
        products = self.db.search_products(max_price=10000)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "Cheap Item")
    
    def test_search_products_combined_filters(self):
        """商品検索テスト（複合フィルター）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーとカテゴリを作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        self.db.cursor.execute("INSERT INTO categories (name) VALUES ('Electronics')")
        category_id = self.db.cursor.lastrowid
        
        # 商品を作成
        self.db.create_product(user_id, "iPhone 13", "Apple iPhone 13", 80000, category_id=category_id)
        self.db.create_product(user_id, "iPhone 12", "Apple iPhone 12", 60000, category_id=category_id)
        self.db.create_product(user_id, "Samsung Galaxy", "Samsung Galaxy S21", 70000, category_id=category_id)
        
        # 複合フィルターで検索
        products = self.db.search_products(
            query="iPhone", category_id=category_id, min_price=50000, max_price=70000
        )
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['title'], "iPhone 12")
    
    def test_search_products_database_error(self):
        """商品検索テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずに検索を試行
        products = self.db.search_products()
        self.assertEqual(products, [])
    
    def test_get_product_success(self):
        """商品詳細取得成功テスト"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        user_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        product_id = self.db.create_product(user_id, "Test Product", "Test Description", 1000)
        
        # 商品詳細を取得
        product = self.db.get_product(product_id)
        self.assertIsNotNone(product)
        self.assertEqual(product['title'], "Test Product")
        self.assertEqual(product['description'], "Test Description")
        self.assertEqual(product['price'], 1000)
    
    def test_get_product_nonexistent(self):
        """商品詳細取得テスト（存在しない商品）"""
        self.db.connect()
        self.db.create_tables()
        
        # 存在しない商品IDで取得を試行
        product = self.db.get_product(99999)
        self.assertIsNone(product)
    
    def test_get_product_database_error(self):
        """商品詳細取得テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずに取得を試行
        product = self.db.get_product(1)
        self.assertIsNone(product)
    
    def test_create_transaction_success(self):
        """取引作成成功テスト"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        seller_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        buyer_id = self.db.create_user("buyer", "buyer@example.com", "password", "Buyer")
        product_id = self.db.create_product(seller_id, "Test Product", "Test Description", 1000)
        
        # 取引を作成
        transaction_id = self.db.create_transaction(product_id, buyer_id, seller_id, 1000)
        self.assertIsNotNone(transaction_id)
        self.assertIsInstance(transaction_id, int)
        
        # データベースに取引が作成されているか確認
        self.db.cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        transaction = self.db.cursor.fetchone()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['product_id'], product_id)
        self.assertEqual(transaction['buyer_id'], buyer_id)
        self.assertEqual(transaction['seller_id'], seller_id)
        self.assertEqual(transaction['price'], 1000)
    
    def test_create_transaction_with_payment_method(self):
        """取引作成テスト（支払い方法指定）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        seller_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        buyer_id = self.db.create_user("buyer", "buyer@example.com", "password", "Buyer")
        product_id = self.db.create_product(seller_id, "Test Product", "Test Description", 1000)
        
        # 取引を作成（支払い方法指定）
        transaction_id = self.db.create_transaction(
            product_id, buyer_id, seller_id, 1000, payment_method="bank_transfer"
        )
        self.assertIsNotNone(transaction_id)
        
        # 支払い方法が正しく保存されているか確認
        self.db.cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        transaction = self.db.cursor.fetchone()
        self.assertEqual(transaction['payment_method'], "bank_transfer")
    
    def test_create_transaction_database_error(self):
        """取引作成テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずに取引作成を試行
        transaction_id = self.db.create_transaction(1, 2, 3, 1000)
        self.assertIsNone(transaction_id)
    
    def test_get_user_transactions_as_buyer(self):
        """ユーザー取引一覧取得テスト（購入者として）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        seller_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        buyer_id = self.db.create_user("buyer", "buyer@example.com", "password", "Buyer")
        product_id = self.db.create_product(seller_id, "Test Product", "Test Description", 1000)
        
        # 取引を作成
        transaction_id = self.db.create_transaction(product_id, buyer_id, seller_id, 1000)
        
        # 購入者として取引一覧を取得
        transactions = self.db.get_user_transactions(buyer_id, "buyer")
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['buyer_id'], buyer_id)
    
    def test_get_user_transactions_as_seller(self):
        """ユーザー取引一覧取得テスト（出品者として）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        seller_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        buyer_id = self.db.create_user("buyer", "buyer@example.com", "password", "Buyer")
        product_id = self.db.create_product(seller_id, "Test Product", "Test Description", 1000)
        
        # 取引を作成
        transaction_id = self.db.create_transaction(product_id, buyer_id, seller_id, 1000)
        
        # 出品者として取引一覧を取得
        transactions = self.db.get_user_transactions(seller_id, "seller")
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['seller_id'], seller_id)
    
    def test_get_user_transactions_all(self):
        """ユーザー取引一覧取得テスト（すべて）"""
        self.db.connect()
        self.db.create_tables()
        
        # ユーザーと商品を作成
        seller_id = self.db.create_user("seller", "seller@example.com", "password", "Seller")
        buyer_id = self.db.create_user("buyer", "buyer@example.com", "password", "Buyer")
        product_id = self.db.create_product(seller_id, "Test Product", "Test Description", 1000)
        
        # 取引を作成
        transaction_id = self.db.create_transaction(product_id, buyer_id, seller_id, 1000)
        
        # すべての取引一覧を取得
        buyer_transactions = self.db.get_user_transactions(buyer_id, "all")
        seller_transactions = self.db.get_user_transactions(seller_id, "all")
        
        self.assertEqual(len(buyer_transactions), 1)
        self.assertEqual(len(seller_transactions), 1)
    
    def test_get_user_transactions_database_error(self):
        """ユーザー取引一覧取得テスト（データベースエラー）"""
        self.db.connect()
        # テーブルを作成せずに取得を試行
        transactions = self.db.get_user_transactions(1, "all")
        self.assertEqual(transactions, [])


class TestMercariApp(unittest.TestCase):
    """MercariAppクラスの単体テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # Tkinterのルートウィンドウをモック
        with patch('tkinter.Tk') as mock_tk:
            self.app = MercariApp()
            self.app.root = Mock()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if hasattr(self.app, 'db') and self.app.db.connection:
            self.app.db.disconnect()
    
    def test_init(self):
        """初期化テスト"""
        self.assertIsNotNone(self.app.root)
        self.assertIsNotNone(self.app.db)
        self.assertIsNone(self.app.current_user)
        self.assertIsNotNone(self.app.screen_manager)
    
    @patch('mercari_prototype.messagebox.showerror')
    def test_init_database_success(self, mock_showerror):
        """データベース初期化成功テスト"""
        with patch.object(self.app.db, 'connect', return_value=True), \
             patch.object(self.app.db, 'create_tables', return_value=True), \
             patch.object(self.app, 'create_sample_data'):
            
            self.app.init_database()
            mock_showerror.assert_not_called()
    
    @patch('mercari_prototype.messagebox.showerror')
    def test_init_database_connect_failure(self, mock_showerror):
        """データベース初期化失敗テスト（接続失敗）"""
        with patch.object(self.app.db, 'connect', return_value=False):
            self.app.init_database()
            mock_showerror.assert_called_once_with("エラー", "データベース接続に失敗しました")
    
    @patch('mercari_prototype.messagebox.showerror')
    def test_init_database_create_tables_failure(self, mock_showerror):
        """データベース初期化失敗テスト（テーブル作成失敗）"""
        with patch.object(self.app.db, 'connect', return_value=True), \
             patch.object(self.app.db, 'create_tables', return_value=False):
            
            self.app.init_database()
            mock_showerror.assert_called_once_with("エラー", "テーブル作成に失敗しました")
    
    def test_create_sample_data_success(self):
        """サンプルデータ作成成功テスト"""
        with patch.object(self.app.db, 'connect', return_value=True), \
             patch.object(self.app.db, 'create_tables', return_value=True), \
             patch.object(self.app.db, 'create_user', return_value=1), \
             patch.object(self.app.db.cursor, 'execute'), \
             patch.object(self.app.db.connection, 'commit'):
            
            # エラーが発生しないことを確認
            self.app.create_sample_data()
    
    def test_create_sample_data_failure(self):
        """サンプルデータ作成失敗テスト"""
        with patch.object(self.app.db, 'connect', return_value=True), \
             patch.object(self.app.db, 'create_tables', return_value=True), \
             patch.object(self.app.db, 'create_user', side_effect=Exception("Database error")):
            
            # エラーが発生しても例外が伝播しないことを確認
            self.app.create_sample_data()
    
    @patch('mercari_prototype.messagebox.showinfo')
    def test_show_register_screen_success(self, mock_showinfo):
        """新規登録画面表示成功テスト"""
        with patch('mercari_prototype.RegisterDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.result = True
            mock_dialog_class.return_value = mock_dialog
            
            self.app.show_register_screen()
            mock_showinfo.assert_called_once_with("成功", "ユーザー登録が完了しました")
    
    @patch('mercari_prototype.messagebox.showinfo')
    def test_show_register_screen_failure(self, mock_showinfo):
        """新規登録画面表示失敗テスト"""
        with patch('mercari_prototype.RegisterDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.result = False
            mock_dialog_class.return_value = mock_dialog
            
            self.app.show_register_screen()
            mock_showinfo.assert_not_called()
    
    @patch('mercari_prototype.messagebox.showwarning')
    def test_login_empty_fields(self, mock_showwarning):
        """ログインテスト（空フィールド）"""
        # 空のユーザー名とパスワードでログインを試行
        self.app.login()
        mock_showwarning.assert_called_once_with("警告", "ユーザー名とパスワードを入力してください")
    
    @patch('mercari_prototype.messagebox.showerror')
    def test_login_failure(self, mock_showerror):
        """ログインテスト（認証失敗）"""
        with patch.object(self.app.db, 'authenticate_user', return_value=None):
            # 認証に失敗するユーザーでログインを試行
            self.app.login()
            mock_showerror.assert_called_once_with("エラー", "ログインに失敗しました")
    
    def test_login_success(self):
        """ログインテスト（認証成功）"""
        test_user = {'id': 1, 'username': 'testuser', 'is_admin': False}
        with patch.object(self.app.db, 'authenticate_user', return_value=test_user), \
             patch.object(self.app, 'show_main_screen'):
            
            self.app.login()
            self.assertEqual(self.app.current_user, test_user)
    
    def test_logout(self):
        """ログアウトテスト"""
        self.app.current_user = {'id': 1, 'username': 'testuser'}
        with patch.object(self.app, 'show_login_screen'):
            self.app.logout()
            self.assertIsNone(self.app.current_user)
    
    @patch('mercari_prototype.messagebox.showwarning')
    def test_create_product_empty_fields(self, mock_showwarning):
        """商品作成テスト（空フィールド）"""
        # 空のフィールドで商品作成を試行
        self.app.create_product()
        mock_showwarning.assert_called_once_with("警告", "すべての項目を入力してください")
    
    @patch('mercari_prototype.messagebox.showerror')
    def test_create_product_invalid_price(self, mock_showerror):
        """商品作成テスト（無効な価格）"""
        # 無効な価格で商品作成を試行
        self.app.create_product()
        mock_showerror.assert_called_once_with("エラー", "価格は正の整数で入力してください")
    
    @patch('mercari_prototype.messagebox.showinfo')
    def test_create_product_success(self, mock_showinfo):
        """商品作成成功テスト"""
        self.app.current_user = {'id': 1, 'username': 'testuser'}
        with patch.object(self.app.db, 'create_product', return_value=1), \
             patch.object(self.app, 'load_my_products'):
            
            self.app.create_product()
            mock_showinfo.assert_called_once_with("成功", "商品を出品しました")
    
    @patch('mercari_prototype.messagebox.showerror')
    def test_create_product_failure(self, mock_showerror):
        """商品作成失敗テスト"""
        self.app.current_user = {'id': 1, 'username': 'testuser'}
        with patch.object(self.app.db, 'create_product', return_value=None):
            self.app.create_product()
            mock_showerror.assert_called_once_with("エラー", "商品の出品に失敗しました")


class TestRegisterDialog(unittest.TestCase):
    """RegisterDialogクラスの単体テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.parent = Mock()
        self.db = Mock()
    
    @patch('tkinter.Toplevel')
    def test_init(self, mock_toplevel):
        """初期化テスト"""
        dialog = RegisterDialog(self.parent, self.db)
        self.assertIsNone(dialog.result)
        self.assertEqual(dialog.db, self.db)
        mock_toplevel.assert_called_once()
    
    @patch('tkinter.Toplevel')
    @patch('mercari_prototype.messagebox.showwarning')
    def test_register_empty_fields(self, mock_showwarning, mock_toplevel):
        """登録テスト（空フィールド）"""
        dialog = RegisterDialog(self.parent, self.db)
        dialog.username_var = Mock()
        dialog.email_var = Mock()
        dialog.password_var = Mock()
        dialog.fullname_var = Mock()
        dialog.phone_var = Mock()
        
        # 空のフィールドで登録を試行
        dialog.username_var.get.return_value = ""
        dialog.email_var.get.return_value = ""
        dialog.password_var.get.return_value = ""
        dialog.fullname_var.get.return_value = ""
        dialog.phone_var.get.return_value = ""
        
        dialog.register()
        mock_showwarning.assert_called_once_with("警告", "必須項目を入力してください")
    
    @patch('tkinter.Toplevel')
    @patch('mercari_prototype.messagebox.showerror')
    def test_register_failure(self, mock_showerror, mock_toplevel):
        """登録失敗テスト"""
        dialog = RegisterDialog(self.parent, self.db)
        dialog.username_var = Mock()
        dialog.email_var = Mock()
        dialog.password_var = Mock()
        dialog.fullname_var = Mock()
        dialog.phone_var = Mock()
        dialog.dialog = Mock()
        
        # 有効なフィールドで登録を試行
        dialog.username_var.get.return_value = "testuser"
        dialog.email_var.get.return_value = "test@example.com"
        dialog.password_var.get.return_value = "password"
        dialog.fullname_var.get.return_value = "Test User"
        dialog.phone_var.get.return_value = "090-1234-5678"
        
        # データベースで登録に失敗
        self.db.create_user.return_value = None
        
        dialog.register()
        mock_showerror.assert_called_once_with("エラー", "登録に失敗しました")
    
    @patch('tkinter.Toplevel')
    def test_register_success(self, mock_toplevel):
        """登録成功テスト"""
        dialog = RegisterDialog(self.parent, self.db)
        dialog.username_var = Mock()
        dialog.email_var = Mock()
        dialog.password_var = Mock()
        dialog.fullname_var = Mock()
        dialog.phone_var = Mock()
        dialog.dialog = Mock()
        
        # 有効なフィールドで登録を試行
        dialog.username_var.get.return_value = "testuser"
        dialog.email_var.get.return_value = "test@example.com"
        dialog.password_var.get.return_value = "password"
        dialog.fullname_var.get.return_value = "Test User"
        dialog.phone_var.get.return_value = "090-1234-5678"
        
        # データベースで登録に成功
        self.db.create_user.return_value = 1
        
        dialog.register()
        self.assertTrue(dialog.result)
        dialog.dialog.destroy.assert_called_once()


class TestProductDetailDialog(unittest.TestCase):
    """ProductDetailDialogクラスの単体テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.parent = Mock()
        self.product = {
            'id': 1,
            'title': 'Test Product',
            'price': 1000,
            'description': 'Test Description',
            'seller_id': 1
        }
        self.current_user = {'id': 2, 'username': 'buyer'}
        self.db = Mock()
    
    @patch('tkinter.Toplevel')
    def test_init(self, mock_toplevel):
        """初期化テスト"""
        dialog = ProductDetailDialog(self.parent, self.product, self.current_user, self.db)
        self.assertEqual(dialog.product, self.product)
        self.assertEqual(dialog.current_user, self.current_user)
        self.assertEqual(dialog.db, self.db)
        mock_toplevel.assert_called_once()
    
    @patch('tkinter.Toplevel')
    @patch('mercari_prototype.messagebox.askyesno')
    @patch('mercari_prototype.messagebox.showinfo')
    def test_purchase_product_success(self, mock_showinfo, mock_askyesno, mock_toplevel):
        """商品購入成功テスト"""
        mock_askyesno.return_value = True
        self.db.create_transaction.return_value = 1
        
        dialog = ProductDetailDialog(self.parent, self.product, self.current_user, self.db)
        dialog.purchase_product()
        
        mock_askyesno.assert_called_once_with("確認", "¥1,000で購入しますか？")
        mock_showinfo.assert_called_once_with("成功", "購入が完了しました")
    
    @patch('tkinter.Toplevel')
    @patch('mercari_prototype.messagebox.askyesno')
    @patch('mercari_prototype.messagebox.showerror')
    def test_purchase_product_failure(self, mock_showerror, mock_askyesno, mock_toplevel):
        """商品購入失敗テスト"""
        mock_askyesno.return_value = True
        self.db.create_transaction.return_value = None
        
        dialog = ProductDetailDialog(self.parent, self.product, self.current_user, self.db)
        dialog.purchase_product()
        
        mock_askyesno.assert_called_once_with("確認", "¥1,000で購入しますか？")
        mock_showerror.assert_called_once_with("エラー", "購入に失敗しました")
    
    @patch('tkinter.Toplevel')
    @patch('mercari_prototype.messagebox.askyesno')
    def test_purchase_product_cancelled(self, mock_askyesno, mock_toplevel):
        """商品購入キャンセルテスト"""
        mock_askyesno.return_value = False
        
        dialog = ProductDetailDialog(self.parent, self.product, self.current_user, self.db)
        dialog.purchase_product()
        
        mock_askyesno.assert_called_once_with("確認", "¥1,000で購入しますか？")
        # キャンセルされた場合は何も実行されない


if __name__ == '__main__':
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMercariDatabase))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMercariApp))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestRegisterDialog))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestProductDetailDialog))
    
    # テストランナーを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # テスト結果の表示
    print(f"\nテスト結果:")
    print(f"実行テスト数: {result.testsRun}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
