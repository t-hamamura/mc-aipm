#!/usr/bin/env python3
"""
プロジェクト情報をブランド情報に自動同期するスクリプト
"""
import os
import yaml
import json
from pathlib import Path
from datetime import datetime
import re

def extract_markdown_content(file_path):
    """Markdownファイルから構造化された情報を抽出"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 基本的な情報抽出（より高度な抽出は後で実装）
    info = {}
    
    # ターゲットオーディエンス抽出
    if 'ターゲット' in content or 'target' in content.lower():
        # 簡易的な抽出ロジック
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'ターゲット' in line or 'target' in line.lower():
                # 次の数行をターゲット情報として抽出
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        if 'target_audience' not in info:
                            info['target_audience'] = []
                        info['target_audience'].append(lines[j].strip())
    
    return info

def sync_project_to_brand(project_path, brand_name):
    """プロジェクト情報をブランド情報に同期"""
    
    # パス設定
    project_info_path = project_path / "project_info.yaml"
    brand_info_path = Path("brands") / brand_name / "info.yaml"
    
    if not project_info_path.exists():
        print(f"❌ プロジェクト情報ファイルが見つかりません: {project_info_path}")
        return False
    
    if not brand_info_path.exists():
        print(f"❌ ブランド情報ファイルが見つかりません: {brand_info_path}")
        return False
    
    # プロジェクト情報読み込み
    with open(project_info_path, 'r', encoding='utf-8') as f:
        project_data = yaml.safe_load(f)
    
    # ブランド情報読み込み
    with open(brand_info_path, 'r', encoding='utf-8') as f:
        brand_data = yaml.safe_load(f)
    
    # 同期処理
    updated = False
    
    # 1. ターゲットオーディエンスの同期
    if 'target_audience' in project_data:
        if 'target_market' not in brand_data['brand']:
            brand_data['brand']['target_market'] = []
        
        # 新しいターゲット情報を追加（重複チェック）
        for target in project_data['target_audience']:
            if target not in brand_data['brand']['target_market']:
                brand_data['brand']['target_market'].append(target)
                updated = True
    
    # 2. キーメッセージの同期
    if 'key_messages' in project_data:
        if 'key_messages' not in brand_data['brand']:
            brand_data['brand']['key_messages'] = []
        
        for message in project_data['key_messages']:
            if message not in brand_data['brand']['key_messages']:
                brand_data['brand']['key_messages'].append(message)
                updated = True
    
    # 3. プロジェクト情報の更新
    if 'projects' not in brand_data:
        brand_data['projects'] = {'active': [], 'completed': []}
    
    project_name = project_data.get('project', {}).get('name', 'Unknown Project')
    if project_name not in brand_data['projects']['active']:
        brand_data['projects']['active'].append(project_name)
        updated = True
    
    # 4. 調査ファイルからの情報抽出
    research_files = [
        "research/persona-analysis.md",
        "research/user-needs-analysis.md",
        "analysis/competitor-analysis.md",
        "analysis/market-analysis.md",
        "strategy/brand-positioning.md"
    ]
    
    for research_file in research_files:
        file_path = project_path / research_file
        if file_path.exists():
            extracted_info = extract_markdown_content(file_path)
            
            # 抽出した情報をブランド情報に統合
            for key, value in extracted_info.items():
                if key not in brand_data['brand']:
                    brand_data['brand'][key] = value
                    updated = True
                elif isinstance(value, list) and isinstance(brand_data['brand'][key], list):
                    # リストの場合は重複チェックして追加
                    for item in value:
                        if item not in brand_data['brand'][key]:
                            brand_data['brand'][key].append(item)
                            updated = True
    
    # 5. 最終更新日時の記録
    if updated:
        brand_data['brand']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ブランド情報を保存
        with open(brand_info_path, 'w', encoding='utf-8') as f:
            yaml.dump(brand_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        print(f"✅ {brand_name}ブランド情報を更新しました")
        return True
    else:
        print(f"ℹ️ {brand_name}ブランド情報に更新はありませんでした")
        return False

def main():
    """メイン処理"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python sync_project_to_brand.py <project_path> <brand_name>")
        print("Example: python sync_project_to_brand.py workspace/projects/active/buzzlabo-brand-site BUZZLABO")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    brand_name = sys.argv[2]
    
    if not project_path.exists():
        print(f"❌ プロジェクトパスが存在しません: {project_path}")
        sys.exit(1)
    
    success = sync_project_to_brand(project_path, brand_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
