"""
データベース接続とセッション管理

このモジュールには、データベース接続の設定とセッション管理機能が含まれています。
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from .models import Base


class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, database_url: str = None):
        """
        データベースマネージャーを初期化
        
        Args:
            database_url: データベースURL（Noneの場合はSQLiteを使用）
        """
        if database_url is None:
            # SQLiteを使用（開発環境）
            database_url = "sqlite:///staff_assignment.db"
        
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """テーブルを作成"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """テーブルを削除"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        データベースセッションを取得
        
        Yields:
            Session: SQLAlchemyセッション
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """
        同期セッションを取得（テスト用）
        
        Returns:
            Session: SQLAlchemyセッション
        """
        return self.SessionLocal()


# グローバルデータベースマネージャーインスタンス
db_manager = DatabaseManager()


def get_database_url() -> str:
    """
    環境変数からデータベースURLを取得
    
    Returns:
        str: データベースURL
    """
    return os.getenv("DATABASE_URL", "sqlite:///staff_assignment.db")


def init_database():
    """データベースを初期化"""
    global db_manager
    database_url = get_database_url()
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI/Flask用の依存性注入関数
    
    Yields:
        Session: データベースセッション
    """
    yield from db_manager.get_session()
