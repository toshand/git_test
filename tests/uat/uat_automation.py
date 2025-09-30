#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAT自動化スクリプト

メルカリ風C2CサービスのUATを自動化するスクリプトです。
- テストデータの準備
- テストケースの実行
- 結果の分析とレポート生成
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

# テストモジュールをインポート
from test_data_generator import UATTestDataGenerator
from uat_test_cases import UATTestSuite


class UATAutomation:
    """UAT自動化クラス"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.test_data_generator = None
        self.test_suite = None
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        default_config = {
            "database": {
                "path": "uat_test.db",
                "backup": True
            },
            "test_data": {
                "users_count": 6,
                "products_count": 50,
                "transactions_count": 30,
                "messages_count": 20,
                "reviews_count": 15
            },
            "test_execution": {
                "run_all": True,
                "priority_filter": None,
                "timeout": 300
            },
            "reporting": {
                "generate_html": True,
                "generate_json": True,
                "output_dir": "uat_reports"
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # デフォルト設定とユーザー設定をマージ
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"⚠️  設定ファイル読み込みエラー: {e}")
                print("デフォルト設定を使用します。")
        
        return default_config
    
    def _merge_config(self, default: Dict, user: Dict):
        """設定をマージ"""
        for key, value in user.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def prepare_test_environment(self) -> bool:
        """テスト環境を準備"""
        print("🔧 テスト環境を準備しています...")
        print("=" * 50)
        
        try:
            # 出力ディレクトリを作成
            output_dir = self.config["reporting"]["output_dir"]
            os.makedirs(output_dir, exist_ok=True)
            
            # データベースのバックアップ
            if self.config["database"]["backup"]:
                self._backup_database()
            
            # テストデータ生成器を初期化
            db_path = os.path.join(os.path.dirname(__file__), self.config["database"]["path"])
            self.test_data_generator = UATTestDataGenerator(db_path)
            
            print("✅ テスト環境の準備が完了しました")
            return True
            
        except Exception as e:
            print(f"❌ テスト環境準備エラー: {e}")
            return False
    
    def _backup_database(self):
        """データベースをバックアップ"""
        db_path = os.path.join(os.path.dirname(__file__), self.config["database"]["path"])
        if os.path.exists(db_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{db_path}.backup_{timestamp}"
            try:
                import shutil
                shutil.copy2(db_path, backup_path)
                print(f"📁 データベースをバックアップしました: {backup_path}")
            except Exception as e:
                print(f"⚠️  バックアップエラー: {e}")
    
    def generate_test_data(self) -> bool:
        """テストデータを生成"""
        print("\n📊 テストデータを生成しています...")
        print("=" * 50)
        
        try:
            if not self.test_data_generator:
                print("❌ テストデータ生成器が初期化されていません")
                return False
            
            # テストデータを生成
            success = self.test_data_generator.generate_all_data()
            
            if success:
                # テストデータをエクスポート
                output_dir = self.config["reporting"]["output_dir"]
                output_file = os.path.join(output_dir, "uat_test_data.json")
                self.test_data_generator.export_test_data(output_file)
                print("✅ テストデータの生成が完了しました")
                return True
            else:
                print("❌ テストデータの生成に失敗しました")
                return False
                
        except Exception as e:
            print(f"❌ テストデータ生成エラー: {e}")
            return False
    
    def run_tests(self) -> bool:
        """テストを実行"""
        print("\n🧪 UATテストを実行しています...")
        print("=" * 50)
        
        try:
            self.test_suite = UATTestSuite()
            
            # テスト実行設定に基づいてテストを実行
            if self.config["test_execution"]["run_all"]:
                self.results = self.test_suite.run_all_tests()
            else:
                priority = self.config["test_execution"]["priority_filter"]
                if priority:
                    self.results = self.test_suite.run_priority_tests(priority)
                else:
                    self.results = self.test_suite.run_all_tests()
            
            print("✅ UATテストの実行が完了しました")
            return True
            
        except Exception as e:
            print(f"❌ UATテスト実行エラー: {e}")
            return False
    
    def generate_reports(self) -> bool:
        """レポートを生成"""
        print("\n📋 レポートを生成しています...")
        print("=" * 50)
        
        try:
            output_dir = self.config["reporting"]["output_dir"]
            
            # JSONレポートを生成
            if self.config["reporting"]["generate_json"]:
                json_file = os.path.join(output_dir, "uat_test_results.json")
                self.test_suite.export_results(json_file)
            
            # HTMLレポートを生成
            if self.config["reporting"]["generate_html"]:
                html_file = os.path.join(output_dir, "uat_test_report.html")
                self._generate_html_report(html_file)
            
            print("✅ レポートの生成が完了しました")
            return True
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
            return False
    
    def _generate_html_report(self, output_file: str):
        """HTMLレポートを生成"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UATテストレポート - メルカリ風C2Cサービス</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .summary-card p {{
            margin: 0;
            opacity: 0.9;
        }}
        .test-results {{
            margin-top: 30px;
        }}
        .test-case {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        .test-case-header {{
            padding: 15px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-case.passed .test-case-header {{
            background-color: #d4edda;
            border-color: #c3e6cb;
        }}
        .test-case.failed .test-case-header {{
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }}
        .test-id {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .test-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .test-status.passed {{
            background-color: #28a745;
        }}
        .test-status.failed {{
            background-color: #dc3545;
        }}
        .test-details {{
            padding: 15px;
        }}
        .test-steps {{
            margin-top: 15px;
        }}
        .test-step {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .test-step:last-child {{
            border-bottom: none;
        }}
        .step-status {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .step-status.passed {{
            background-color: #28a745;
        }}
        .step-status.failed {{
            background-color: #dc3545;
        }}
        .step-status.not-executed {{
            background-color: #6c757d;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 UATテストレポート</h1>
            <h2>メルカリ風C2Cサービス</h2>
            <p>実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{self.results.get('total_tests', 0)}</h3>
                <p>総テスト数</p>
            </div>
            <div class="summary-card">
                <h3>{self.results.get('passed_tests', 0)}</h3>
                <p>成功</p>
            </div>
            <div class="summary-card">
                <h3>{self.results.get('failed_tests', 0)}</h3>
                <p>失敗</p>
            </div>
            <div class="summary-card">
                <h3>{self.results.get('success_rate', 0):.1f}%</h3>
                <p>成功率</p>
            </div>
        </div>
        
        <div class="test-results">
            <h3>📋 テストケース詳細</h3>
"""
        
        # テストケースの詳細を追加
        for result in self.results.get('results', []):
            status_class = 'passed' if result.get('result') else 'failed'
            status_text = 'PASSED' if result.get('result') else 'FAILED'
            
            html_content += f"""
            <div class="test-case {status_class}">
                <div class="test-case-header">
                    <div>
                        <div class="test-id">{result.get('test_id', 'N/A')}</div>
                        <div>{result.get('description', 'N/A')}</div>
                    </div>
                    <div class="test-status {status_class}">{status_text}</div>
                </div>
                <div class="test-details">
                    <p><strong>優先度:</strong> {result.get('priority', 'N/A')}</p>
                    <p><strong>実行時間:</strong> {result.get('execution_time', 0):.2f}秒</p>
"""
            
            if result.get('error_message'):
                html_content += f"<p><strong>エラー:</strong> {result.get('error_message')}</p>"
            
            # テストステップを追加
            if result.get('steps'):
                html_content += """
                    <div class="test-steps">
                        <h4>テストステップ:</h4>
"""
                for step in result.get('steps', []):
                    step_status = step.get('status', 'not-executed')
                    html_content += f"""
                        <div class="test-step">
                            <span class="step-status {step_status}"></span>
                            <strong>{step.get('description', 'N/A')}</strong><br>
                            <small>期待結果: {step.get('expected_result', 'N/A')}</small>
                        </div>
"""
                html_content += "</div>"
            
            html_content += """
                </div>
            </div>
"""
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>UAT自動化ツール v1.0 | メルカリ風C2Cサービス</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def run_full_uat(self) -> bool:
        """完全なUATを実行"""
        self.start_time = time.time()
        
        print("🚀 メルカリ風C2Cサービス UAT自動化を開始します")
        print("=" * 60)
        
        try:
            # 1. テスト環境の準備
            if not self.prepare_test_environment():
                return False
            
            # 2. テストデータの生成
            if not self.generate_test_data():
                return False
            
            # 3. テストの実行
            if not self.run_tests():
                return False
            
            # 4. レポートの生成
            if not self.generate_reports():
                return False
            
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            
            # 最終結果の表示
            print("\n" + "=" * 60)
            print("🎉 UAT自動化が完了しました！")
            print("=" * 60)
            print(f"総実行時間: {execution_time:.2f}秒")
            print(f"成功率: {self.results.get('success_rate', 0):.1f}%")
            
            # 受け入れ判定
            if self.results.get('success_rate', 0) >= 95.0:
                print("✅ システムは受け入れ基準を満たしています。")
                return True
            else:
                print("❌ システムは受け入れ基準を満たしていません。")
                return False
                
        except Exception as e:
            print(f"❌ UAT自動化エラー: {e}")
            return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='UAT自動化スクリプト')
    parser.add_argument('--config', '-c', help='設定ファイルのパス')
    parser.add_argument('--data-only', action='store_true', help='テストデータ生成のみ実行')
    parser.add_argument('--test-only', action='store_true', help='テスト実行のみ実行')
    parser.add_argument('--report-only', action='store_true', help='レポート生成のみ実行')
    
    args = parser.parse_args()
    
    # UAT自動化を初期化
    automation = UATAutomation(args.config)
    
    if args.data_only:
        # テストデータ生成のみ
        automation.prepare_test_environment()
        success = automation.generate_test_data()
    elif args.test_only:
        # テスト実行のみ
        automation.prepare_test_environment()
        success = automation.run_tests()
    elif args.report_only:
        # レポート生成のみ
        success = automation.generate_reports()
    else:
        # 完全なUAT実行
        success = automation.run_full_uat()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
