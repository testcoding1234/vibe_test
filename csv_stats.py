#!/usr/bin/env python3
"""
CSVファイルの統計情報を出力するCLIツール
行数・列数・欠損値数・数値列の統計量を表示
"""

import argparse
import sys
import pandas as pd
from pathlib import Path


def analyze_csv(filepath):
    """CSVファイルを分析し、統計情報を表示する"""
    try:
        df = pd.read_csv(filepath)
        
        # 基本情報
        print("=" * 60)
        print(f"ファイル: {filepath}")
        print("=" * 60)
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        
        # 欠損値情報
        print("\n--- 欠損値情報 ---")
        total_missing = df.isnull().sum().sum()
        print(f"欠損値の総数: {total_missing}")
        
        missing_by_column = df.isnull().sum()
        if missing_by_column.any():
            print("\n列ごとの欠損値:")
            for col, count in missing_by_column[missing_by_column > 0].items():
                percentage = (count / len(df)) * 100
                print(f"  {col}: {count} ({percentage:.2f}%)")
        else:
            print("欠損値がありません")
        
        # 数値列の統計量
        print("\n--- 数値列の統計量 ---")
        numeric_df = df.select_dtypes(include=['number'])
        
        if len(numeric_df.columns) > 0:
            print(numeric_df.describe().to_string())
        else:
            print("数値列がありません")
        
        # 列情報
        print("\n--- 列情報 ---")
        print("列名と型:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
        
        print("\n" + "=" * 60)
        
    except FileNotFoundError:
        print(f"エラー: ファイル '{filepath}' が見つかりません", file=sys.stderr)
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"エラー: ファイル '{filepath}' はCSV形式ではありません", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='CSVファイルの統計情報を表示するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python csv_stats.py data.csv
  python csv_stats.py /path/to/file.csv
        '''
    )
    parser.add_argument('filepath', help='分析するCSVファイルのパス')
    
    args = parser.parse_args()
    analyze_csv(args.filepath)


if __name__ == '__main__':
    main()
