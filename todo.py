#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO管理アプリケーション（データベース版）
Tkinterを使用したGUI TODO管理ツール

機能:
- TODOアイテムの追加・編集・削除
- 優先度設定
- 期限設定
- 完了状態の管理
- データの永続化（SQLiteデータベース）
- 検索・フィルタリング機能
- JSONからの自動移行

作成日: 2024
作者: AI Assistant
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading


class TodoDatabase:
    """TODOデータベース管理クラス"""
    
    def __init__(self, db_path: str = "data/todos.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """データディレクトリの存在確認と作成"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """データベースの初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT '中',
                    due_date TEXT,
                    completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
            ''')
            conn.commit()
    
    def get_all_todos(self) -> List[Dict]:
        """すべてのTODOを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, description, priority, due_date, completed, created_at, updated_at
                FROM todos
                ORDER BY created_at DESC
            ''')
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_todo_by_id(self, todo_id: str) -> Optional[Dict]:
        """IDでTODOを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, description, priority, due_date, completed, created_at, updated_at
                FROM todos
                WHERE id = ?
            ''', (todo_id,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def insert_todo(self, todo_data: Dict) -> bool:
        """TODOを挿入"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO todos (id, title, description, priority, due_date, completed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    todo_data['id'],
                    todo_data['title'],
                    todo_data['description'],
                    todo_data['priority'],
                    todo_data['due_date'],
                    1 if todo_data['completed'] else 0,
                    todo_data['created_at'],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"TODO挿入エラー: {e}")
            return False
    
    def update_todo(self, todo_data: Dict) -> bool:
        """TODOを更新"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE todos
                    SET title = ?, description = ?, priority = ?, due_date = ?, 
                        completed = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    todo_data['title'],
                    todo_data['description'],
                    todo_data['priority'],
                    todo_data['due_date'],
                    1 if todo_data['completed'] else 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    todo_data['id']
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"TODO更新エラー: {e}")
            return False
    
    def delete_todo(self, todo_id: str) -> bool:
        """TODOを削除"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"TODO削除エラー: {e}")
            return False
    
    def search_todos(self, search_text: str = "", filter_type: str = "すべて") -> List[Dict]:
        """TODOを検索・フィルタリング"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 基本クエリ
            query = '''
                SELECT id, title, description, priority, due_date, completed, created_at, updated_at
                FROM todos
                WHERE 1=1
            '''
            params = []
            
            # 検索条件
            if search_text:
                query += ' AND (title LIKE ? OR description LIKE ?)'
                search_pattern = f'%{search_text}%'
                params.extend([search_pattern, search_pattern])
            
            # フィルター条件
            if filter_type == "未完了":
                query += ' AND completed = 0'
            elif filter_type == "完了":
                query += ' AND completed = 1'
            elif filter_type == "高優先度":
                query += ' AND priority = ?'
                params.append("高")
            elif filter_type == "期限切れ":
                query += ' AND due_date < ? AND due_date != ""'
                params.append(datetime.now().strftime("%Y-%m-%d"))
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 総数
            cursor.execute('SELECT COUNT(*) FROM todos')
            total = cursor.fetchone()[0]
            
            # 完了数
            cursor.execute('SELECT COUNT(*) FROM todos WHERE completed = 1')
            completed = cursor.fetchone()[0]
            
            # 未完了数
            cursor.execute('SELECT COUNT(*) FROM todos WHERE completed = 0')
            pending = cursor.fetchone()[0]
            
            # 高優先度数
            cursor.execute('SELECT COUNT(*) FROM todos WHERE priority = "高" AND completed = 0')
            high_priority = cursor.fetchone()[0]
            
            # 期限切れ数
            cursor.execute('SELECT COUNT(*) FROM todos WHERE due_date < ? AND due_date != "" AND completed = 0', 
                         (datetime.now().strftime("%Y-%m-%d"),))
            overdue = cursor.fetchone()[0]
            
            return {
                'total': total,
                'completed': completed,
                'pending': pending,
                'high_priority': high_priority,
                'overdue': overdue
            }
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """JSONファイルからデータベースに移行"""
        try:
            if not os.path.exists(json_file_path):
                return False
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for item in data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO todos (id, title, description, priority, due_date, completed, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['id'],
                        item['title'],
                        item['description'],
                        item['priority'],
                        item['due_date'],
                        1 if item['completed'] else 0,
                        item['created_at'],
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"JSON移行エラー: {e}")
            return False


class TodoItem:
    """TODOアイテムのクラス"""
    
    def __init__(self, title: str, description: str = "", priority: str = "中", 
                 due_date: str = "", completed: bool = False, created_at: str = ""):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id = f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date,
            'completed': self.completed,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        """辞書からオブジェクトを作成"""
        item = cls(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', '中'),
            due_date=data.get('due_date', ''),
            completed=bool(data.get('completed', False)),
            created_at=data.get('created_at', '')
        )
        item.id = data['id']
        return item


class TodoApp:
    """TODO管理アプリケーションのメインクラス"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TODO管理アプリケーション (データベース版)")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # データベースの初期化
        self.db = TodoDatabase()
        
        # TODOアイテムのリスト
        self.todos: List[TodoItem] = []
        self.filtered_todos: List[TodoItem] = []
        
        # 現在選択されているアイテム
        self.selected_item: Optional[TodoItem] = None
        
        # UIのセットアップ
        self.setup_ui()
        
        # データの読み込み
        self.load_data()
        
        # 初期表示
        self.refresh_todo_list()
    
    
    def setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左側パネル（TODOリスト）
        self.setup_todo_list_panel(main_frame)
        
        # 右側パネル（詳細・編集）
        self.setup_detail_panel(main_frame)
        
        # ステータスバー
        self.setup_status_bar(main_frame)
    
    def setup_todo_list_panel(self, parent):
        """TODOリストパネルのセットアップ"""
        # TODOリストフレーム
        list_frame = ttk.LabelFrame(parent, text="TODOリスト", padding="5")
        list_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # 検索・フィルターフレーム
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        # 検索ボックス
        ttk.Label(filter_frame, text="検索:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        # Python 3.13対応: trace_addを使用
        self.search_var.trace_add('write', self.on_search_change)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # フィルター
        ttk.Label(filter_frame, text="フィルター:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.filter_var = tk.StringVar(value="すべて")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["すべて", "未完了", "完了", "高優先度", "期限切れ"])
        filter_combo.grid(row=0, column=3, sticky=tk.W)
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # TODOリスト
        self.setup_todo_treeview(list_frame)
        
        # ボタンフレーム
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="新規追加", command=self.add_todo).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="編集", command=self.edit_todo).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="削除", command=self.delete_todo).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="完了/未完了", command=self.toggle_completion).grid(row=0, column=3)
    
    def setup_todo_treeview(self, parent):
        """TODOリストのTreeviewセットアップ"""
        # Treeviewの作成
        columns = ("id", "title", "priority", "due_date", "status")
        self.todo_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # 列の設定
        self.todo_tree.heading("id", text="ID")
        self.todo_tree.heading("title", text="タイトル")
        self.todo_tree.heading("priority", text="優先度")
        self.todo_tree.heading("due_date", text="期限")
        self.todo_tree.heading("status", text="状態")
        
        self.todo_tree.column("id", width=0, minwidth=0)  # ID列を非表示
        self.todo_tree.column("title", width=200)
        self.todo_tree.column("priority", width=80)
        self.todo_tree.column("due_date", width=100)
        self.todo_tree.column("status", width=80)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=scrollbar.set)
        
        # 配置
        self.todo_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # イベントバインド
        self.todo_tree.bind('<<TreeviewSelect>>', self.on_todo_select)
        self.todo_tree.bind('<Double-1>', self.edit_todo)
    
    def setup_detail_panel(self, parent):
        """詳細パネルのセットアップ"""
        detail_frame = ttk.LabelFrame(parent, text="詳細・編集", padding="5")
        detail_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(1, weight=1)
        
        # タイトル
        ttk.Label(detail_frame, text="タイトル:").grid(row=0, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(detail_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 説明
        ttk.Label(detail_frame, text="説明:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.description_text = tk.Text(detail_frame, height=6, width=40)
        self.description_text.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 優先度
        ttk.Label(detail_frame, text="優先度:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.priority_var = tk.StringVar(value="中")
        priority_combo = ttk.Combobox(detail_frame, textvariable=self.priority_var, 
                                     values=["高", "中", "低"], state="readonly")
        priority_combo.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        # 期限
        ttk.Label(detail_frame, text="期限:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.due_date_var = tk.StringVar()
        due_date_entry = ttk.Entry(detail_frame, textvariable=self.due_date_var, width=20)
        due_date_entry.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        ttk.Button(detail_frame, text="今日", command=self.set_today).grid(row=3, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        
        # 完了状態
        self.completed_var = tk.BooleanVar()
        completed_check = ttk.Checkbutton(detail_frame, text="完了", variable=self.completed_var)
        completed_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 作成日時
        ttk.Label(detail_frame, text="作成日時:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.created_at_var = tk.StringVar()
        created_at_label = ttk.Label(detail_frame, textvariable=self.created_at_var, foreground="gray")
        created_at_label.grid(row=5, column=1, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # 保存・キャンセルボタン
        button_frame = ttk.Frame(detail_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存", command=self.save_todo).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="キャンセル", command=self.cancel_edit).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="新規作成", command=self.new_todo).grid(row=0, column=2)
    
    def setup_status_bar(self, parent):
        """ステータスバーのセットアップ"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="準備完了")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 統計情報
        self.stats_var = tk.StringVar()
        stats_label = ttk.Label(status_frame, textvariable=self.stats_var)
        stats_label.grid(row=0, column=1, sticky=tk.E)
    
    def on_search_change(self, *args):
        """検索条件変更時の処理"""
        self.refresh_todo_list()
    
    def on_filter_change(self, *args):
        """フィルター変更時の処理"""
        self.refresh_todo_list()
    
    def on_todo_select(self, event):
        """TODO選択時の処理"""
        selection = self.todo_tree.selection()
        if selection:
            item_id = selection[0]
            todo_id = self.todo_tree.item(item_id)['values'][0] if self.todo_tree.item(item_id)['values'] else None
            if todo_id:
                # データベースからTODOを取得
                todo_data = self.db.get_todo_by_id(todo_id)
                if todo_data:
                    self.selected_item = TodoItem.from_dict(todo_data)
                    self.display_todo_details()
    
    def refresh_todo_list(self):
        """TODOリストの更新"""
        # 検索とフィルタリング
        search_text = self.search_var.get()
        filter_type = self.filter_var.get()
        
        # データベースから検索・フィルタリング結果を取得
        db_results = self.db.search_todos(search_text, filter_type)
        
        # データベース結果をTodoItemオブジェクトに変換
        self.filtered_todos = [TodoItem.from_dict(item) for item in db_results]
        
        # Treeviewの更新
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        
        for todo in self.filtered_todos:
            status = "完了" if todo.completed else "未完了"
            self.todo_tree.insert("", "end", values=(todo.id, todo.title, todo.priority, todo.due_date, status))
        
        # 統計情報の更新
        stats = self.db.get_statistics()
        self.stats_var.set(f"総数: {stats['total']} | 完了: {stats['completed']} | 未完了: {stats['pending']} | 高優先度: {stats['high_priority']} | 期限切れ: {stats['overdue']}")
    
    def display_todo_details(self):
        """選択されたTODOの詳細表示"""
        if self.selected_item:
            self.title_var.set(self.selected_item.title)
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, self.selected_item.description)
            self.priority_var.set(self.selected_item.priority)
            self.due_date_var.set(self.selected_item.due_date)
            self.completed_var.set(self.selected_item.completed)
            self.created_at_var.set(self.selected_item.created_at)
        else:
            self.clear_details()
    
    def clear_details(self):
        """詳細パネルのクリア"""
        self.title_var.set("")
        self.description_text.delete(1.0, tk.END)
        self.priority_var.set("中")
        self.due_date_var.set("")
        self.completed_var.set(False)
        self.created_at_var.set("")
        self.selected_item = None
    
    def add_todo(self):
        """新しいTODOの追加"""
        self.new_todo()
    
    def new_todo(self):
        """新規TODO作成モード"""
        self.clear_details()
        self.selected_item = None
        self.status_var.set("新規TODOを作成中...")
    
    def edit_todo(self, event=None):
        """TODOの編集"""
        if not self.selected_item:
            messagebox.showwarning("警告", "編集するTODOを選択してください。")
            return
        
        self.status_var.set(f"'{self.selected_item.title}' を編集中...")
    
    def delete_todo(self):
        """TODOの削除"""
        if not self.selected_item:
            messagebox.showwarning("警告", "削除するTODOを選択してください。")
            return
        
        if messagebox.askyesno("確認", f"'{self.selected_item.title}' を削除しますか？"):
            if self.db.delete_todo(self.selected_item.id):
                self.refresh_todo_list()
                self.clear_details()
                self.status_var.set("TODOを削除しました。")
            else:
                messagebox.showerror("エラー", "TODOの削除に失敗しました。")
    
    def toggle_completion(self):
        """完了状態の切り替え"""
        if not self.selected_item:
            messagebox.showwarning("警告", "切り替えるTODOを選択してください。")
            return
        
        self.selected_item.completed = not self.selected_item.completed
        
        if self.db.update_todo(self.selected_item.to_dict()):
            self.refresh_todo_list()
            self.display_todo_details()
            status = "完了" if self.selected_item.completed else "未完了"
            self.status_var.set(f"'{self.selected_item.title}' を{status}に変更しました。")
        else:
            messagebox.showerror("エラー", "TODOの更新に失敗しました。")
    
    def save_todo(self):
        """TODOの保存"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("エラー", "タイトルを入力してください。")
            return
        
        description = self.description_text.get(1.0, tk.END).strip()
        priority = self.priority_var.get()
        due_date = self.due_date_var.get().strip()
        completed = self.completed_var.get()
        
        if self.selected_item:
            # 既存アイテムの更新
            self.selected_item.title = title
            self.selected_item.description = description
            self.selected_item.priority = priority
            self.selected_item.due_date = due_date
            self.selected_item.completed = completed
            
            if self.db.update_todo(self.selected_item.to_dict()):
                self.status_var.set(f"'{title}' を更新しました。")
            else:
                messagebox.showerror("エラー", "TODOの更新に失敗しました。")
                return
        else:
            # 新規アイテムの作成
            new_todo = TodoItem(title, description, priority, due_date, completed)
            
            if self.db.insert_todo(new_todo.to_dict()):
                self.selected_item = new_todo
                self.status_var.set(f"'{title}' を作成しました。")
            else:
                messagebox.showerror("エラー", "TODOの作成に失敗しました。")
                return
        
        self.refresh_todo_list()
        self.display_todo_details()
    
    def cancel_edit(self):
        """編集のキャンセル"""
        if self.selected_item:
            self.display_todo_details()
        else:
            self.clear_details()
        self.status_var.set("編集をキャンセルしました。")
    
    def set_today(self):
        """今日の日付を設定"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.due_date_var.set(today)
    
    def load_data(self):
        """データの読み込み"""
        try:
            # データベースからすべてのTODOを取得
            db_results = self.db.get_all_todos()
            self.todos = [TodoItem.from_dict(item) for item in db_results]
            
            # JSONファイルが存在する場合は移行を試行
            json_file = "data/todos.json"
            if os.path.exists(json_file):
                if self.db.migrate_from_json(json_file):
                    # 移行後に再取得
                    db_results = self.db.get_all_todos()
                    self.todos = [TodoItem.from_dict(item) for item in db_results]
                    self.status_var.set(f"{len(self.todos)}件のTODOを読み込みました（JSONから移行）。")
                else:
                    self.status_var.set(f"{len(self.todos)}件のTODOを読み込みました。")
            else:
                self.status_var.set(f"{len(self.todos)}件のTODOを読み込みました。")
        except Exception as e:
            messagebox.showerror("エラー", f"データの読み込みに失敗しました: {str(e)}")
            self.todos = []
    
    def save_data(self):
        """データの保存（データベース版では不要）"""
        # データベース版では個別のCRUD操作で自動保存されるため、このメソッドは不要
        pass


def main():
    """メイン関数"""
    root = tk.Tk()
    app = TodoApp(root)
    
    # ウィンドウクローズ時の処理
    def on_closing():
        # データベース版では自動保存されるため、特別な処理は不要
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()