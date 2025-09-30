#!/usr/bin/env python3
"""
HTML to Excel 変換プログラムの使用例

このスクリプトは、html_to_excel_converter.pyの使用方法を示すサンプルです。
"""

import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.html_to_excel_converter import HTMLToExcelConverter


def example_single_file_conversion():
    """単一ファイル変換の例"""
    print("=== 単一ファイル変換の例 ===")
    
    # コンバーターを初期化
    converter = HTMLToExcelConverter(log_level="INFO")
    
    # 既存のHTMLファイルを変換
    html_file = project_root / "index.html"
    if html_file.exists():
        try:
            output_file = converter.convert_html_to_excel(str(html_file))
            print(f"変換完了: {output_file}")
        except Exception as e:
            print(f"変換エラー: {e}")
    else:
        print(f"HTMLファイルが見つかりません: {html_file}")


def example_batch_conversion():
    """一括変換の例"""
    print("\n=== 一括変換の例 ===")
    
    # コンバーターを初期化
    converter = HTMLToExcelConverter(log_level="INFO")
    
    # プロジェクトディレクトリ内のHTMLファイルを一括変換
    input_dir = str(project_root)
    output_dir = str(project_root / "excel_output")
    
    try:
        converted_files = converter.batch_convert(input_dir, output_dir)
        print(f"一括変換完了: {len(converted_files)}個のファイルを変換")
        for file_path in converted_files:
            print(f"  - {file_path}")
    except Exception as e:
        print(f"一括変換エラー: {e}")


def example_custom_html():
    """カスタムHTMLファイルの作成と変換例"""
    print("\n=== カスタムHTMLファイルの変換例 ===")
    
    # サンプルHTMLファイルを作成
    sample_html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>サンプルデータ</title>
    </head>
    <body>
        <h1>会社概要</h1>
        <p>この会社は革新的な技術を提供しています。</p>
        
        <h2>従業員一覧</h2>
        <table>
            <thead>
                <tr>
                    <th>名前</th>
                    <th>部署</th>
                    <th>入社年</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>田中太郎</td>
                    <td>営業部</td>
                    <td>2020</td>
                </tr>
                <tr>
                    <td>佐藤花子</td>
                    <td>開発部</td>
                    <td>2019</td>
                </tr>
                <tr>
                    <td>鈴木一郎</td>
                    <td>マーケティング部</td>
                    <td>2021</td>
                </tr>
            </tbody>
        </table>
        
        <h2>事業内容</h2>
        <ul>
            <li>Webアプリケーション開発</li>
            <li>モバイルアプリ開発</li>
            <li>システムコンサルティング</li>
        </ul>
        
        <h2>売上実績</h2>
        <table>
            <thead>
                <tr>
                    <th>年度</th>
                    <th>売上（万円）</th>
                    <th>前年比</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>2021</td>
                    <td>1,000</td>
                    <td>+10%</td>
                </tr>
                <tr>
                    <td>2022</td>
                    <td>1,200</td>
                    <td>+20%</td>
                </tr>
                <tr>
                    <td>2023</td>
                    <td>1,500</td>
                    <td>+25%</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # サンプルHTMLファイルを保存
    sample_file = project_root / "sample_data.html"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_html)
    
    # コンバーターを初期化
    converter = HTMLToExcelConverter(log_level="INFO")
    
    try:
        # サンプルファイルを変換
        output_file = converter.convert_html_to_excel(str(sample_file))
        print(f"サンプルファイル変換完了: {output_file}")
        
        # サンプルファイルを削除
        sample_file.unlink()
        print("サンプルファイルを削除しました")
        
    except Exception as e:
        print(f"サンプルファイル変換エラー: {e}")


def main():
    """メイン関数"""
    print("HTML to Excel 変換プログラムの使用例")
    print("=" * 50)
    
    # 例1: 単一ファイル変換
    example_single_file_conversion()
    
    # 例2: 一括変換
    example_batch_conversion()
    
    # 例3: カスタムHTMLファイルの変換
    example_custom_html()
    
    print("\n使用例が完了しました。")


if __name__ == "__main__":
    main()


