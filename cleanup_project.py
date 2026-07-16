"""
商用品質：自動整理スクリプト（ログ付き完全版）

不要ファイル削除・フォルダ生成・ファイル移動・重複チェックを自動化。
結果を cleanup_log.txt に記録する。
"""

import os
import shutil
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(ROOT, "cleanup_log.txt")

# 削除対象（あなたのプロジェクト構成に合わせて最適化）
REMOVE_FILES = [
    "audio_analyzer.py",
    "chart_generator.py",
    "classes_professional.py",
    "config.py",
    "exceptions.py",
    "graphics.py",
    "logger.py",
    "songs.py",
    "ui_screens.py",
    "utils.py",
    "resource_manager.py",
]

# 移動タスク（必要なら追加可能）
MOVE_TASKS = [
    ("ui/manager.py", "manager/screen_manager.py"),
    ("utils.py", "utils/common/utils.py"),
]

# 必要フォルダ
NEEDED_DIRS = [
    "manager",
    "utils/common",
]

# 重複チェック（あなたのプロジェクト構成に合わせて最適化）
DUPLICATES = [
    ("game/render/effects/judge_beam.py", "graphics/effects/judge_beam.py"),
    ("game/render/effects/glow_effect.py", "graphics/effects/glow_effect.py"),
]


def log(message: str):
    """ログ出力（ファイル＋コンソール）"""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def ensure_dirs():
    log("\n[1] 必要フォルダの作成")
    for d in NEEDED_DIRS:
        path = os.path.join(ROOT, d)
        if not os.path.exists(path):
            os.makedirs(path)
            log(f"  ✔ Created: {d}")
        else:
            log(f"  ✔ Exists: {d}")


def remove_old_files():
    log("\n[2] 旧ファイルの削除")
    for f in REMOVE_FILES:
        path = os.path.join(ROOT, f)
        if os.path.exists(path):
            os.remove(path)
            log(f"  ✔ Removed: {f}")
        else:
            log(f"  ✔ Already removed: {f}")


def move_files():
    log("\n[3] ファイルの移動")
    for src, dst in MOVE_TASKS:
        src_path = os.path.join(ROOT, src)
        dst_path = os.path.join(ROOT, dst)

        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.move(src_path, dst_path)
            log(f"  ✔ Moved: {src} → {dst}")
        else:
            log(f"  ✔ Skip (not found): {src}")


def check_duplicates():
    log("\n[4] 重複ファイルのチェック")
    for a, b in DUPLICATES:
        a_path = os.path.join(ROOT, a)
        b_path = os.path.join(ROOT, b)
        if os.path.exists(a_path) and os.path.exists(b_path):
            log(f"  ⚠ Duplicate found: {a} AND {b}")
        else:
            log(f"  ✔ OK: {a} / {b}")


def main():
    # ログ初期化
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== Cleanup Log ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

    log("======================================")
    log("   商用品質：プロジェクト自動整理ツール")
    log("======================================")

    ensure_dirs()
    remove_old_files()
    move_files()
    check_duplicates()

    log("\n✔ 完了しました！")
    log("プロジェクトが商用品質の構造に整理されました。")


if __name__ == "__main__":
    main()
