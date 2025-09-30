# TODO管理アプリケーション (PostgreSQL版)

Tkinterを使用したGUI TODO管理ツールです。PostgreSQLデータベースを使用してデータを永続化します。

## 機能

- TODOアイテムの追加・編集・削除
- 優先度設定（高・中・低）
- 期限設定
- 完了状態の管理
- 検索・フィルタリング機能
- 統計情報の表示
- JSONからの自動データ移行

## 必要な環境

### 1. Python
- Python 3.7以上

### 2. PostgreSQL
- PostgreSQL 9.6以上
- PostgreSQLサービスが起動していること

### 3. Pythonライブラリ
```bash
pip install -r requirements.txt
```

## セットアップ

### 1. PostgreSQLのインストール

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
- [PostgreSQL公式サイト](https://www.postgresql.org/download/windows/)からインストーラーをダウンロードしてインストール

### 2. データベースのセットアップ

```bash
python setup_postgresql.py
```

このスクリプトは以下を実行します：
- `todo_app`データベースの作成
- `todos`テーブルの作成
- パフォーマンス向上のためのインデックスの作成

### 3. 環境変数の設定（オプション）

デフォルト値を使用しない場合は、以下の環境変数を設定してください：

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=todo_app
export DB_USER=postgres
export DB_PASSWORD=your_password
```

**Windows:**
```cmd
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=todo_app
set DB_USER=postgres
set DB_PASSWORD=your_password
```

## 使用方法

### アプリケーションの起動

```bash
python main.py
```

### 基本的な操作

1. **新規TODOの追加**
   - 「新規追加」ボタンをクリック
   - タイトル、説明、優先度、期限を入力
   - 「保存」ボタンをクリック

2. **TODOの編集**
   - リストからTODOを選択
   - 詳細パネルで内容を編集
   - 「保存」ボタンをクリック

3. **TODOの削除**
   - リストからTODOを選択
   - 「削除」ボタンをクリック
   - 確認ダイアログで「はい」を選択

4. **完了状態の切り替え**
   - リストからTODOを選択
   - 「完了/未完了」ボタンをクリック

5. **検索・フィルタリング**
   - 検索ボックスにキーワードを入力
   - フィルターで条件を選択

## データベーススキーマ

### todosテーブル

| カラム名 | データ型 | 制約 | 説明 |
|---------|---------|------|------|
| id | VARCHAR(255) | PRIMARY KEY | TODOの一意識別子 |
| title | VARCHAR(500) | NOT NULL | TODOのタイトル |
| description | TEXT | | TODOの説明 |
| priority | VARCHAR(10) | DEFAULT '中' | 優先度（高・中・低） |
| due_date | DATE | | 期限 |
| completed | BOOLEAN | DEFAULT FALSE | 完了状態 |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | | 更新日時 |

### インデックス

- `idx_todos_completed`: 完了状態での検索最適化
- `idx_todos_priority`: 優先度での検索最適化
- `idx_todos_due_date`: 期限での検索最適化
- `idx_todos_created_at`: 作成日時でのソート最適化

## データ移行

既存のJSONファイル（`data/todos.json`）がある場合、アプリケーション起動時に自動的にPostgreSQLデータベースに移行されます。

## トラブルシューティング

### データベース接続エラー

1. **PostgreSQLサービスが起動しているか確認**
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Ubuntu/Debian
   sudo systemctl status postgresql
   ```

2. **接続情報の確認**
   - ホスト、ポート、データベース名、ユーザー名、パスワードが正しいか
   - 環境変数が正しく設定されているか

3. **PostgreSQLユーザーの権限確認**
   ```sql
   -- PostgreSQLに接続して確認
   \du
   ```

### アプリケーションが起動しない

1. **必要なライブラリがインストールされているか確認**
   ```bash
   pip list | grep psycopg2
   ```

2. **Pythonバージョンの確認**
   ```bash
   python --version
   ```

## 開発者向け情報

### プロジェクト構造

```
todo_app/
├── main.py                 # メインアプリケーション
├── setup_postgresql.py     # データベースセットアップスクリプト
├── requirements.txt        # 必要なライブラリ
└── README.md              # このファイル
```

### データベース接続クラス

`TodoDatabase`クラスがPostgreSQLとの通信を管理します：

- `get_connection()`: データベース接続を取得
- `get_all_todos()`: すべてのTODOを取得
- `insert_todo()`: 新しいTODOを挿入
- `update_todo()`: TODOを更新
- `delete_todo()`: TODOを削除
- `search_todos()`: 検索・フィルタリング
- `get_statistics()`: 統計情報を取得

### カスタマイズ

データベース接続パラメータを変更する場合は、`TodoDatabase`クラスの`__init__`メソッドを修正するか、環境変数を設定してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。