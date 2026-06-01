#!/usr/bin/env python3
"""
ゲーム起動スクリプト
Piano Tiles ゲームをシンプルに起動します
"""

import sys
import os

# 現在のディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from main import main

        print("=" * 50)
        print("Piano Tiles - ゲーム起動")
        print("=" * 50)
        print("← → キーで曲を選択")
        print("SPACE キーでゲーム開始")
        print("ESC キーで終了")
        print("=" * 50)
        main()
    except KeyboardInterrupt:
        print("\nゲームを終了しました。")
        sys.exit(0)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
