"""
ゲーム用カスタム例外定義

このモジュールは、Piano Tiles ゲーム固有のエラー処理を提供します。
エラーハンドリングを統一し、デバッグを容易にします。
"""


class PianoTilesError(Exception):
    """Piano Tiles ゲームの基本例外クラス"""

    pass


class ChartLoadError(PianoTilesError):
    """譜面読み込みエラー"""

    pass


class AudioLoadError(PianoTilesError):
    """音声ファイル読み込みエラー"""

    pass


class ConfigError(PianoTilesError):
    """設定ファイルエラー"""

    pass


class FontError(PianoTilesError):
    """フォント読み込みエラー"""

    pass


class ResourceError(PianoTilesError):
    """リソース管理エラー"""

    pass
