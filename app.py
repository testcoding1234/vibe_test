#!/usr/bin/env python3
"""
Flask Webサーバー - CSV統計ツール
"""

from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/csv_uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# アップロードフォルダを作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def analyze_csv_file(filepath):
    """CSVファイルを分析し、統計情報を辞書で返す"""
    try:
        df = pd.read_csv(filepath)
        
        # 基本情報
        result = {
            'success': True,
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
            },
            'columns': list(df.columns)
        }
        
        # 欠損値情報
        total_missing = df.isnull().sum().sum()
        missing_by_column = df.isnull().sum().to_dict()
        
        result['missing_info'] = {
            'total_missing': int(total_missing),
            'by_column': missing_by_column
        }
        
        # 数値列の統計量
        numeric_df = df.select_dtypes(include=['number'])
        if len(numeric_df.columns) > 0:
            # pandasのdescribeはString型のインデックスを持つDataFrameを返す
            stats = numeric_df.describe().to_dict()
            # Noneをnullに変換（JSON互換性のため）
            for col in stats:
                for stat_name in stats[col]:
                    val = stats[col][stat_name]
                    if pd.isna(val):
                        stats[col][stat_name] = None
                    else:
                        stats[col][stat_name] = float(val)
            result['statistics'] = stats
        else:
            result['statistics'] = {}
        
        # 列の型情報
        result['dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        return result
        
    except pd.errors.ParserError as e:
        return {
            'success': False,
            'error': f'CSVパースエラー: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'エラーが発生しました: {str(e)}'
        }


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """CSVファイルをアップロードして分析"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'ファイルが指定されていません'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'CSVファイルのみアップロード可能です'}), 400
    
    try:
        # ファイルを保存
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 分析実行
        result = analyze_csv_file(filepath)
        
        # ファイルを削除
        os.remove(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'サーバーエラー: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
