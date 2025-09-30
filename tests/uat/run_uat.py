#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAT実行スクリプト

メルカリ風C2CサービスのUATを実行するメインスクリプトです。
"""

import os
import sys
import argparse
import json
from datetime import datetime

# UATモジュールをインポート
from uat_automation import UATAutomation
from test_data_generator import UATTestDataGenerator
from uat_test_cases import UATTestSuite


def print_banner():
    """バナーを表示"""
    print("=" * 80)
    print("🧪 メルカリ風C2Cサービス UAT実行スクリプト")
    print("=" * 80)
    print("ユーザーアクセプタンステストを自動実行します")
    print(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print("=" * 80)


def run_data_generation():
    """テストデータ生成のみ実行"""
    print("\n📊 テストデータ生成を実行します...")
    
    try:
        generator = UATTestDataGenerator()
        success = generator.generate_all_data()
        
        if success:
            print("✅ テストデータ生成が完了しました")
            return True
        else:
            print("❌ テストデータ生成に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ テストデータ生成エラー: {e}")
        return False


def run_test_execution():
    """テスト実行のみ実行"""
    print("\n🧪 UATテストを実行します...")
    
    try:
        test_suite = UATTestSuite()
        results = test_suite.run_all_tests()
        
        # 結果を表示
        print(f"\n📊 テスト結果:")
        print(f"  総テスト数: {results['total_tests']}")
        print(f"  成功: {results['passed_tests']}")
        print(f"  失敗: {results['failed_tests']}")
        print(f"  成功率: {results['success_rate']:.1f}%")
        
        # 受け入れ判定
        if results['success_rate'] >= 95.0:
            print("✅ UATテストが成功しました！")
            return True
        else:
            print("❌ UATテストが失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False


def run_priority_tests(priority: str):
    """優先度別テスト実行"""
    print(f"\n🎯 {priority}優先度のテストを実行します...")
    
    try:
        test_suite = UATTestSuite()
        results = test_suite.run_priority_tests(priority)
        
        # 結果を表示
        print(f"\n📊 {priority}優先度テスト結果:")
        print(f"  総テスト数: {results['total_tests']}")
        print(f"  成功: {results['passed_tests']}")
        print(f"  失敗: {results['failed_tests']}")
        print(f"  成功率: {results['success_rate']:.1f}%")
        
        return results['success_rate'] >= 95.0
        
    except Exception as e:
        print(f"❌ 優先度別テスト実行エラー: {e}")
        return False


def run_full_uat(config_file: str = None):
    """完全なUAT実行"""
    print("\n🚀 完全なUATを実行します...")
    
    try:
        automation = UATAutomation(config_file)
        success = automation.run_full_uat()
        
        if success:
            print("🎉 完全なUATが成功しました！")
            return True
        else:
            print("❌ 完全なUATが失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ 完全なUAT実行エラー: {e}")
        return False


def show_test_cases():
    """テストケース一覧を表示"""
    print("\n📋 利用可能なテストケース:")
    print("-" * 50)
    
    test_suite = UATTestSuite()
    
    for i, test_case in enumerate(test_suite.test_cases, 1):
        status_icon = "✅" if test_case.result else "❌" if test_case.result is False else "⏳"
        print(f"{i:2d}. {status_icon} {test_case.test_id}: {test_case.description}")
        print(f"    優先度: {test_case.priority}")
        if test_case.execution_time > 0:
            print(f"    実行時間: {test_case.execution_time:.2f}秒")
        print()


def show_config_info(config_file: str):
    """設定情報を表示"""
    print(f"\n⚙️  設定ファイル: {config_file}")
    print("-" * 50)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📊 テストデータ設定:")
        test_data = config.get('test_data', {})
        print(f"  ユーザー数: {test_data.get('users_count', 'N/A')}")
        print(f"  商品数: {test_data.get('products_count', 'N/A')}")
        print(f"  取引数: {test_data.get('transactions_count', 'N/A')}")
        
        print("\n🧪 テスト実行設定:")
        test_exec = config.get('test_execution', {})
        print(f"  全テスト実行: {test_exec.get('run_all', 'N/A')}")
        print(f"  優先度フィルター: {test_exec.get('priority_filter', 'N/A')}")
        print(f"  タイムアウト: {test_exec.get('timeout', 'N/A')}秒")
        
        print("\n📋 レポート設定:")
        reporting = config.get('reporting', {})
        print(f"  HTMLレポート: {reporting.get('generate_html', 'N/A')}")
        print(f"  JSONレポート: {reporting.get('generate_json', 'N/A')}")
        print(f"  出力ディレクトリ: {reporting.get('output_dir', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 設定ファイル読み込みエラー: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='メルカリ風C2Cサービス UAT実行スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python run_uat.py                    # 完全なUAT実行
  python run_uat.py --data-only        # テストデータ生成のみ
  python run_uat.py --test-only        # テスト実行のみ
  python run_uat.py --priority High    # 高優先度テストのみ
  python run_uat.py --list-cases       # テストケース一覧表示
  python run_uat.py --config config.json # 設定ファイル指定
        """
    )
    
    parser.add_argument('--config', '-c', 
                       help='設定ファイルのパス (デフォルト: uat_config.json)')
    parser.add_argument('--data-only', action='store_true',
                       help='テストデータ生成のみ実行')
    parser.add_argument('--test-only', action='store_true',
                       help='テスト実行のみ実行')
    parser.add_argument('--priority', '-p', 
                       choices=['High', 'Medium', 'Low'],
                       help='指定された優先度のテストのみ実行')
    parser.add_argument('--list-cases', action='store_true',
                       help='テストケース一覧を表示')
    parser.add_argument('--show-config', action='store_true',
                       help='設定情報を表示')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='詳細なログを表示')
    
    args = parser.parse_args()
    
    # バナーを表示
    print_banner()
    
    # 設定ファイルのパスを決定
    config_file = args.config
    if not config_file:
        config_file = os.path.join(os.path.dirname(__file__), "uat_config.json")
    
    # 設定情報を表示
    if args.show_config:
        show_config_info(config_file)
        return 0
    
    # テストケース一覧を表示
    if args.list_cases:
        show_test_cases()
        return 0
    
    # 各モードで実行
    success = False
    
    try:
        if args.data_only:
            success = run_data_generation()
        elif args.test_only:
            success = run_test_execution()
        elif args.priority:
            success = run_priority_tests(args.priority)
        else:
            success = run_full_uat(config_file)
        
        # 最終結果
        print("\n" + "=" * 80)
        if success:
            print("🎉 UAT実行が成功しました！")
            print("✅ システムは受け入れ基準を満たしています。")
        else:
            print("❌ UAT実行が失敗しました。")
            print("⚠️  システムは受け入れ基準を満たしていません。")
        print("=" * 80)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによって中断されました。")
        return 1
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
