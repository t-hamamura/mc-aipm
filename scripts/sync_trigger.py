#!/usr/bin/env python3
"""
プロジェクト→ブランド情報同期のトリガースクリプト
使用例: python sync_trigger.py "プロジェクト情報をブランドに反映"
"""
import sys
import subprocess
from pathlib import Path

def sync_project_to_brand_trigger():
    """プロジェクト情報をブランド情報に同期するトリガー"""
    
    # アクティブなプロジェクトを検索
    projects_dir = Path("workspace/projects/active")
    if not projects_dir.exists():
        print("❌ アクティブなプロジェクトが見つかりません")
        return False
    
    # プロジェクト一覧を取得
    projects = [p for p in projects_dir.iterdir() if p.is_dir()]
    
    if not projects:
        print("❌ アクティブなプロジェクトがありません")
        return False
    
    print("📋 アクティブなプロジェクト一覧:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project.name}")
    
    # プロジェクト選択（複数ある場合）
    if len(projects) == 1:
        selected_project = projects[0]
        print(f"✅ 自動選択: {selected_project.name}")
    else:
        try:
            choice = int(input("同期するプロジェクト番号を選択してください: ")) - 1
            if 0 <= choice < len(projects):
                selected_project = projects[choice]
            else:
                print("❌ 無効な選択です")
                return False
        except ValueError:
            print("❌ 数値を入力してください")
            return False
    
    # ブランド名を推測（プロジェクト名から）
    project_name = selected_project.name
    if "buzzlabo" in project_name.lower():
        brand_name = "BUZZLABO"
    elif "anzbeaute" in project_name.lower():
        brand_name = "ANZBEAUTE"
    else:
        brand_name = input("ブランド名を入力してください: ").upper()
    
    print(f"🔄 {project_name} → {brand_name} への同期を開始...")
    
    # 同期スクリプト実行
    try:
        result = subprocess.run([
            "python3", "scripts/sync_project_to_brand.py",
            str(selected_project), brand_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 同期が完了しました")
            print(result.stdout)
            return True
        else:
            print("❌ 同期に失敗しました")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and "プロジェクト情報をブランドに反映" in sys.argv[1]:
        sync_project_to_brand_trigger()
    else:
        print("使用方法: python sync_trigger.py 'プロジェクト情報をブランドに反映'")
