#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト実行スクリプト

mercari_prototype.pyの単体テストを実行し、C2レベル（分岐網羅率100%）を確認
"""

import sys
import os
import subprocess
import unittest

# テストディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

def run_unit_tests():
    """単体テストを実行"""
    print("=" * 80)
    print("メルカリ風C2Cサービス 単体テスト実行")
    print("=" * 80)
    print()
    
    # テストモジュールをインポート
    try:
        from test_mercari_prototype import (
            TestMercariDatabase, TestMercariApp,
            TestRegisterDialog, TestProductDetailDialog
        )
        print("✅ テストモジュールのインポートに成功しました")
    except ImportError as e:
        print(f"❌ テストモジュールのインポートに失敗しました: {e}")
        return False
    
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    test_classes = [
        TestMercariDatabase,
        TestMercariApp,
        TestRegisterDialog,
        TestProductDetailDialog
    ]
    
    for test_class in test_classes:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
    
    print(f"📋 テストクラス数: {len(test_classes)}")
    print(f"📋 総テスト数: {test_suite.countTestCases()}")
    print()
    
    # テストランナーを実行
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # 結果の表示
    print()
    print("=" * 80)
    print("テスト実行結果")
    print("=" * 80)
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ 失敗したテスト:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    理由: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n❌ エラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    理由: {traceback.split('\\n')[-2]}")
    
    return len(result.failures) == 0 and len(result.errors) == 0


def run_coverage_analysis():
    """カバレッジ分析を実行"""
    print("\n" + "=" * 80)
    print("カバレッジ分析実行")
    print("=" * 80)
    
    try:
        from test_coverage_report import CoverageAnalyzer
        
        analyzer = CoverageAnalyzer()
        analyzer.generate_report()
        
        # C2レベル（分岐網羅率100%）の確認
        total_branches = 0
        total_covered = 0
        
        for class_name, data in analyzer.coverage_data.items():
            total_branches += data['total_branches']
            total_covered += data['covered_branches']
        
        coverage_rate = (total_covered / total_branches * 100) if total_branches > 0 else 0
        
        print(f"\n🎯 C2レベル（分岐網羅率100%）達成状況:")
        print(f"   分岐網羅率: {coverage_rate:.1f}%")
        
        if coverage_rate == 100.0:
            print("   ✅ C2レベル（分岐網羅率100%）を達成しました！")
            return True
        else:
            print("   ⚠️  C2レベル（分岐網羅率100%）に達していません。")
            return False
            
    except ImportError as e:
        print(f"❌ カバレッジ分析モジュールのインポートに失敗しました: {e}")
        return False


def main():
    """メイン関数"""
    print("メルカリ風C2Cサービス テスト実行スクリプト")
    print("C2レベル（分岐網羅率100%）の単体テストを実行します")
    print()
    
    # 単体テストを実行
    test_success = run_unit_tests()
    
    if not test_success:
        print("\n❌ 単体テストに失敗しました。カバレッジ分析をスキップします。")
        return 1
    
    # カバレッジ分析を実行
    coverage_success = run_coverage_analysis()
    
    print("\n" + "=" * 80)
    print("最終結果")
    print("=" * 80)
    
    if test_success and coverage_success:
        print("🎉 すべてのテストが成功し、C2レベル（分岐網羅率100%）を達成しました！")
        print("✅ 単体テスト: 成功")
        print("✅ カバレッジ: 100%")
        return 0
    elif test_success:
        print("⚠️  単体テストは成功しましたが、C2レベル（分岐網羅率100%）に達していません。")
        print("✅ 単体テスト: 成功")
        print("❌ カバレッジ: 100%未達成")
        return 1
    else:
        print("❌ 単体テストに失敗しました。")
        print("❌ 単体テスト: 失敗")
        print("❌ カバレッジ: 未確認")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
