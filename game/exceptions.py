"""
商用品質：例外処理モジュール（完全版）

ゲーム全体で発生する例外を統一的に管理し、
ログ出力・追加情報・階層構造を備えた商用品質の例外システム。
"""

import datetime

# ============================================================
# 基本例外クラス（商用品質）
# ============================================================


class GameError(Exception):
    """ゲーム全体の基本例外クラス（商用品質）"""

    def __init__(self, message="ゲーム内で予期しないエラーが発生しました。", detail=None):
        super().__init__(message)
        self.message = message
        self.detail = detail
        self.timestamp = datetime.datetime.now()

    def log(self):
        """商用品質ログ出力"""
        print(f"[ERROR] {self.timestamp} | {self.__class__.__name__} | {self.message}")
        if self.detail:
            print(f"        Detail: {self.detail}")


# ============================================================
# リソース関連
# ============================================================


class ResourceLoadError(GameError):
    """リソース読み込み失敗"""

    def __init__(self, resource_name, detail=None):
        super().__init__(f"リソース '{resource_name}' の読み込みに失敗しました。", detail)


class ResourceNotFoundError(GameError):
    """リソースが存在しない"""

    def __init__(self, resource_name):
        super().__init__(f"リソース '{resource_name}' が見つかりません。")


# ============================================================
# 音声関連
# ============================================================


class AudioPlaybackError(GameError):
    """音声再生エラー"""

    def __init__(self, file_path, detail=None):
        super().__init__(f"音声ファイル '{file_path}' の再生中にエラーが発生しました。", detail)


class AudioLoadError(GameError):
    """音声ファイル読み込みエラー"""

    def __init__(self, file_path):
        super().__init__(f"音声ファイル '{file_path}' を読み込めませんでした。")


# ============================================================
# 譜面関連
# ============================================================


class ChartParseError(GameError):
    """譜面解析エラー"""

    def __init__(self, chart_file, detail=None):
        super().__init__(f"譜面ファイル '{chart_file}' の解析に失敗しました。", detail)


class ChartFormatError(GameError):
    """譜面フォーマット不正"""

    def __init__(self, chart_file):
        super().__init__(f"譜面ファイル '{chart_file}' の形式が不正です。")


# ============================================================
# 描画関連
# ============================================================


class RenderError(GameError):
    """描画関連エラー"""

    def __init__(self, detail="描画処理中にエラーが発生しました。"):
        super().__init__(detail)


# ============================================================
# 設定関連
# ============================================================


class ConfigError(GameError):
    """設定ファイルエラー"""

    def __init__(self, key, detail=None):
        super().__init__(f"設定キー '{key}' が無効または存在しません。", detail)


# ============================================================
# ゲームプレイ関連
# ============================================================


class GameplayError(GameError):
    """プレイ中のロジックエラー"""

    def __init__(self, detail="プレイロジック中に異常が発生しました。"):
        super().__init__(detail)


class TimingError(GameError):
    """判定タイミング異常"""

    def __init__(self, detail="判定タイミングに異常が発生しました。"):
        super().__init__(detail)
