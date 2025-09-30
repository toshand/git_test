#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAT用テストデータ生成スクリプト

メルカリ風C2CサービスのUAT用テストデータを生成します。
- ユーザーデータ
- 商品データ
- 取引データ
- カテゴリデータ
"""

import sqlite3
import random
import hashlib
import datetime
import json
import os
from typing import List, Dict, Any


class UATTestDataGenerator:
    """UAT用テストデータ生成クラス"""
    
    def __init__(self, db_path: str = "uat_test.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # テストデータの定義
        self.categories = [
            "電子機器", "ファッション", "本・雑誌", "スポーツ", "ホビー",
            "家電", "食品", "美容・健康", "自動車", "不動産"
        ]
        
        self.product_names = {
            "電子機器": [
                "iPhone 13", "MacBook Pro", "iPad Air", "AirPods Pro",
                "Nintendo Switch", "PlayStation 5", "Samsung Galaxy S21",
                "Surface Pro", "Apple Watch", "Google Pixel"
            ],
            "ファッション": [
                "ナイキ スニーカー", "ユニクロ ダウンジャケット", "ZARA コート",
                "GU ジーンズ", "無印良品 シャツ", "アディダス トレーナー",
                "コーチ バッグ", "ルイヴィトン 財布", "シャネル 香水",
                "ティファニー ネックレス"
            ],
            "本・雑誌": [
                "Python入門書", "ビジネス書", "小説", "漫画", "雑誌",
                "技術書", "料理本", "旅行ガイド", "写真集", "辞典"
            ],
            "スポーツ": [
                "ヨガマット", "ランニングシューズ", "テニスラケット",
                "ゴルフクラブ", "自転車", "スキー板", "サーフボード",
                "バスケットボール", "サッカーボール", "トレーニングウェア"
            ],
            "ホビー": [
                "カメラ", "フィギュア", "模型", "楽器", "ゲーム",
                "アート用品", "手芸用品", "園芸用品", "釣り道具",
                "コレクションアイテム"
            ]
        }
        
        self.conditions = ["新品", "美品", "良品", "可", "悪い"]
        self.statuses = ["active", "sold", "inactive"]
        self.transaction_statuses = ["pending", "completed", "cancelled"]
        self.payment_methods = ["credit_card", "bank_transfer", "cash"]
        
        # ユーザーデータ
        self.users = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "full_name": "管理者",
                "phone": "090-0000-0000",
                "is_admin": True
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "user123",
                "full_name": "田中太郎",
                "phone": "090-1111-1111",
                "is_admin": False
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "user123",
                "full_name": "佐藤花子",
                "phone": "090-2222-2222",
                "is_admin": False
            },
            {
                "username": "user3",
                "email": "user3@example.com",
                "password": "user123",
                "full_name": "山田次郎",
                "phone": "090-3333-3333",
                "is_admin": False
            },
            {
                "username": "user4",
                "email": "user4@example.com",
                "password": "user123",
                "full_name": "鈴木一郎",
                "phone": "090-4444-4444",
                "is_admin": False
            },
            {
                "username": "user5",
                "email": "user5@example.com",
                "password": "user123",
                "full_name": "高橋美咲",
                "phone": "090-5555-5555",
                "is_admin": False
            }
        ]
    
    def connect(self) -> bool:
        """データベース接続"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"DB接続エラー: {e}")
            return False
    
    def disconnect(self):
        """データベース切断"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self) -> bool:
        """テーブル作成"""
        try:
            # ユーザーテーブル
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    profile_image TEXT,
                    rating REAL DEFAULT 5.0,
                    review_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    is_admin BOOLEAN DEFAULT 0
                )
            """)
            
            # 商品カテゴリテーブル
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    parent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 商品テーブル
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    category_id INTEGER,
                    condition TEXT NOT NULL,
                    images TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (seller_id) REFERENCES users(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)
            
            # 取引テーブル
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    buyer_id INTEGER NOT NULL,
                    seller_id INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    payment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (buyer_id) REFERENCES users(id),
                    FOREIGN KEY (seller_id) REFERENCES users(id)
                )
            """)
            
            # メッセージテーブル
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    FOREIGN KEY (receiver_id) REFERENCES users(id)
                )
            """)
            
            # レビューテーブル
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    reviewer_id INTEGER NOT NULL,
                    reviewee_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (reviewer_id) REFERENCES users(id),
                    FOREIGN KEY (reviewee_id) REFERENCES users(id)
                )
            """)
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"テーブル作成エラー: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """パスワードハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_users(self) -> bool:
        """ユーザーデータ生成"""
        try:
            for user_data in self.users:
                password_hash = self.hash_password(user_data["password"])
                self.cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (username, email, password_hash, full_name, phone, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_data["username"],
                    user_data["email"],
                    password_hash,
                    user_data["full_name"],
                    user_data["phone"],
                    user_data["is_admin"]
                ))
            
            self.connection.commit()
            print(f"✅ ユーザーデータ生成完了: {len(self.users)}件")
            return True
            
        except sqlite3.Error as e:
            print(f"ユーザーデータ生成エラー: {e}")
            return False
    
    def generate_categories(self) -> bool:
        """カテゴリデータ生成"""
        try:
            for category_name in self.categories:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO categories (name)
                    VALUES (?)
                """, (category_name,))
            
            self.connection.commit()
            print(f"✅ カテゴリデータ生成完了: {len(self.categories)}件")
            return True
            
        except sqlite3.Error as e:
            print(f"カテゴリデータ生成エラー: {e}")
            return False
    
    def generate_products(self, count: int = 50) -> bool:
        """商品データ生成"""
        try:
            # ユーザーIDとカテゴリIDを取得
            self.cursor.execute("SELECT id FROM users WHERE is_admin = 0")
            user_ids = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT id, name FROM categories")
            categories = {row[1]: row[0] for row in self.cursor.fetchall()}
            
            products_created = 0
            
            for _ in range(count):
                # ランダムなカテゴリを選択
                category_name = random.choice(list(self.product_names.keys()))
                category_id = categories.get(category_name)
                
                # ランダムな商品名を選択
                product_name = random.choice(self.product_names[category_name])
                
                # ランダムな価格を生成
                price = random.randint(100, 100000)
                
                # ランダムな状態を選択
                condition = random.choice(self.conditions)
                status = random.choice(self.statuses)
                
                # ランダムな出品者を選択
                seller_id = random.choice(user_ids)
                
                # 商品説明を生成
                description = f"{product_name}の{condition}です。詳細はお問い合わせください。"
                
                self.cursor.execute("""
                    INSERT INTO products 
                    (seller_id, title, description, price, category_id, condition, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (seller_id, product_name, description, price, category_id, condition, status))
                
                products_created += 1
            
            self.connection.commit()
            print(f"✅ 商品データ生成完了: {products_created}件")
            return True
            
        except sqlite3.Error as e:
            print(f"商品データ生成エラー: {e}")
            return False
    
    def generate_transactions(self, count: int = 30) -> bool:
        """取引データ生成"""
        try:
            # 商品とユーザーを取得
            self.cursor.execute("""
                SELECT p.id, p.seller_id, p.price 
                FROM products p 
                WHERE p.status = 'active'
            """)
            products = self.cursor.fetchall()
            
            self.cursor.execute("SELECT id FROM users WHERE is_admin = 0")
            user_ids = [row[0] for row in self.cursor.fetchall()]
            
            transactions_created = 0
            
            for _ in range(min(count, len(products))):
                if not products:
                    break
                
                # ランダムな商品を選択
                product = random.choice(products)
                product_id, seller_id, price = product
                
                # 出品者以外のユーザーを購入者として選択
                buyer_candidates = [uid for uid in user_ids if uid != seller_id]
                if not buyer_candidates:
                    continue
                
                buyer_id = random.choice(buyer_candidates)
                
                # ランダムな取引状態を選択
                status = random.choice(self.transaction_statuses)
                payment_method = random.choice(self.payment_methods)
                
                # 取引を作成
                self.cursor.execute("""
                    INSERT INTO transactions 
                    (product_id, buyer_id, seller_id, price, status, payment_method)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_id, buyer_id, seller_id, price, status, payment_method))
                
                # 取引が完了した場合、商品の状態を更新
                if status == "completed":
                    self.cursor.execute("""
                        UPDATE products SET status = 'sold' WHERE id = ?
                    """, (product_id,))
                
                transactions_created += 1
                
                # 使用した商品をリストから削除
                products.remove(product)
            
            self.connection.commit()
            print(f"✅ 取引データ生成完了: {transactions_created}件")
            return True
            
        except sqlite3.Error as e:
            print(f"取引データ生成エラー: {e}")
            return False
    
    def generate_messages(self, count: int = 20) -> bool:
        """メッセージデータ生成"""
        try:
            # 取引を取得
            self.cursor.execute("SELECT id, buyer_id, seller_id FROM transactions")
            transactions = self.cursor.fetchall()
            
            messages_created = 0
            
            for _ in range(min(count, len(transactions))):
                if not transactions:
                    break
                
                transaction = random.choice(transactions)
                transaction_id, buyer_id, seller_id = transaction
                
                # ランダムな送信者を選択（購入者または出品者）
                sender_id = random.choice([buyer_id, seller_id])
                receiver_id = seller_id if sender_id == buyer_id else buyer_id
                
                # ランダムなメッセージを生成
                messages = [
                    "商品について質問があります。",
                    "配送について教えてください。",
                    "ありがとうございます。",
                    "商品の状態はいかがですか？",
                    "取引を進めさせていただきます。",
                    "よろしくお願いします。"
                ]
                message = random.choice(messages)
                
                self.cursor.execute("""
                    INSERT INTO messages 
                    (transaction_id, sender_id, receiver_id, message)
                    VALUES (?, ?, ?, ?)
                """, (transaction_id, sender_id, receiver_id, message))
                
                messages_created += 1
            
            self.connection.commit()
            print(f"✅ メッセージデータ生成完了: {messages_created}件")
            return True
            
        except sqlite3.Error as e:
            print(f"メッセージデータ生成エラー: {e}")
            return False
    
    def generate_reviews(self, count: int = 15) -> bool:
        """レビューデータ生成"""
        try:
            # 完了した取引を取得
            self.cursor.execute("""
                SELECT id, buyer_id, seller_id FROM transactions 
                WHERE status = 'completed'
            """)
            transactions = self.cursor.fetchall()
            
            reviews_created = 0
            
            for _ in range(min(count, len(transactions))):
                if not transactions:
                    break
                
                transaction = random.choice(transactions)
                transaction_id, buyer_id, seller_id = transaction
                
                # ランダムな評価を生成
                rating = random.randint(1, 5)
                
                # ランダムなコメントを生成
                comments = [
                    "とても良い商品でした。",
                    "迅速な対応ありがとうございました。",
                    "商品の状態が良かったです。",
                    "また機会があれば取引したいです。",
                    "梱包も丁寧でした。",
                    "説明通りでした。"
                ]
                comment = random.choice(comments)
                
                # 購入者から出品者へのレビュー
                self.cursor.execute("""
                    INSERT INTO reviews 
                    (transaction_id, reviewer_id, reviewee_id, rating, comment)
                    VALUES (?, ?, ?, ?, ?)
                """, (transaction_id, buyer_id, seller_id, rating, comment))
                
                reviews_created += 1
            
            self.connection.commit()
            print(f"✅ レビューデータ生成完了: {reviews_created}件")
            return True
            
        except sqlite3.Error as e:
            print(f"レビューデータ生成エラー: {e}")
            return False
    
    def generate_all_data(self) -> bool:
        """全テストデータ生成"""
        print("🚀 UAT用テストデータ生成を開始します...")
        print("=" * 50)
        
        if not self.connect():
            return False
        
        if not self.create_tables():
            return False
        
        # 既存データをクリア
        tables = ["reviews", "messages", "transactions", "products", "categories", "users"]
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table}")
        self.connection.commit()
        print("🗑️  既存データをクリアしました")
        
        # データ生成
        success = True
        success &= self.generate_users()
        success &= self.generate_categories()
        success &= self.generate_products(50)
        success &= self.generate_transactions(30)
        success &= self.generate_messages(20)
        success &= self.generate_reviews(15)
        
        if success:
            print("=" * 50)
            print("🎉 全テストデータ生成が完了しました！")
            self.print_data_summary()
        else:
            print("❌ テストデータ生成中にエラーが発生しました")
        
        self.disconnect()
        return success
    
    def print_data_summary(self):
        """データサマリーを表示"""
        if not self.connection:
            return
        
        print("\n📊 生成されたデータサマリー:")
        print("-" * 30)
        
        tables = [
            ("users", "ユーザー"),
            ("categories", "カテゴリ"),
            ("products", "商品"),
            ("transactions", "取引"),
            ("messages", "メッセージ"),
            ("reviews", "レビュー")
        ]
        
        for table, name in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"{name}: {count}件")
        
        print("-" * 30)
    
    def export_test_data(self, output_file: str = "uat_test_data.json"):
        """テストデータをJSONファイルにエクスポート"""
        if not self.connect():
            return False
        
        try:
            test_data = {}
            
            # 各テーブルのデータを取得
            tables = ["users", "categories", "products", "transactions", "messages", "reviews"]
            
            for table in tables:
                self.cursor.execute(f"SELECT * FROM {table}")
                rows = self.cursor.fetchall()
                test_data[table] = [dict(row) for row in rows]
            
            # JSONファイルに保存
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ テストデータをエクスポートしました: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ テストデータエクスポートエラー: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """メイン関数"""
    print("メルカリ風C2Cサービス UAT用テストデータ生成ツール")
    print("=" * 60)
    
    # データベースファイルのパス
    db_path = os.path.join(os.path.dirname(__file__), "uat_test.db")
    
    # データ生成器を作成
    generator = UATTestDataGenerator(db_path)
    
    # 全データを生成
    success = generator.generate_all_data()
    
    if success:
        # テストデータをエクスポート
        output_file = os.path.join(os.path.dirname(__file__), "uat_test_data.json")
        generator.export_test_data(output_file)
        
        print(f"\n📁 データベースファイル: {db_path}")
        print(f"📁 エクスポートファイル: {output_file}")
        print("\n✅ UAT用テストデータの準備が完了しました！")
        return 0
    else:
        print("\n❌ テストデータ生成に失敗しました")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
