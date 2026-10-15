"""互換用のゲーム起動エントリポイント。"""


def run_game():
    """現行のルート起動処理へ委譲する。"""
    from main import main

    main()
