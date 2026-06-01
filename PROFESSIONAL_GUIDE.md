# 🎯 Piano Tiles - プロフェッショナル化ガイド

このドキュメントは、Piano Tiles ゲームをプロフェッショナルなレベルに引き上げるための詳細ガイドです。

## 📚 目次

1. [プロフェッショナル化の内容](#プロフェッショナル化の内容)
2. [新しいモジュール](#新しいモジュール)
3. [型ヒント](#型ヒント)
4. [ドキュメント](#ドキュメント)
5. [使用方法](#使用方法)
6. [ベストプラクティス](#ベストプラクティス)

---

## 🏆 プロフェッショナル化の内容

### ✅ 実装された改善

| 項目                   | 説明                                    |
| ---------------------- | --------------------------------------- |
| **型ヒント**           | 全関数に型ヒント実装                    |
| **ドキュメント**       | Google style docstring                  |
| **エラーハンドリング** | カスタム例外システム                    |
| **ロギング**           | 構造化ロギング（ファイル + コンソール） |
| **リソース管理**       | キャッシング機構付き                    |
| **設定管理**           | 外部設定ファイル対応                    |
| **プロジェクト構造**   | pyproject.toml 対応                     |
| **コード品質**         | Black, flake8, mypy 対応                |

---

## 📦 新しいモジュール

### 1. **exceptions.py** - カスタム例外

```python
from exceptions import PianoTilesError, ChartLoadError, AudioLoadError

# 基本例外
try:
    # 何か処理
    pass
except ChartLoadError as e:
    logger.error(f"譜面読み込みエラー: {e}")
except AudioLoadError as e:
    logger.error(f"音声読み込みエラー: {e}")
```

**利点**:

- エラーの種類が明確
- 適切なエラーハンドリングが可能
- デバッグが容易

---

### 2. **logger.py** - ロギングシステム

```python
from logger import get_logger

# ロガー取得
logger = get_logger(__name__)

# ログ出力
logger.debug("デバッグ情報")
logger.info("ゲーム開始")
logger.warning("警告メッセージ")
logger.error("エラーが発生しました")
logger.critical("致命的エラー")
```

**ログファイル**: `logs/piano_tiles_YYYYMMDD_HHMMSS.log`

**利点**:

- ファイルとコンソールに同時出力
- 自動的に logs/ フォルダを作成
- タイムスタンプ付きログファイル
- デバッグが容易

---

### 3. **config.py** - 設定管理

```python
from config import Config

# デフォルト設定を読み込み
config = Config.load()

# 設定にアクセス
print(config.screen.width)      # 400
print(config.game.difficulty)   # "NORMAL"
print(config.audio.bgm_volume)  # 0.8

# 設定を変更
config.game.speed_level = 5
config.audio.master_volume = 0.9

# 設定を保存
config.save()  # config.json に保存
```

**設定ファイル**: `config.json`

**利点**:

- 実行時に設定を変更可能
- ユーザーの設定が保存される
- 設定ファイルは JSON で可読性高い

---

### 4. **resource_manager.py** - リソース管理

```python
from resource_manager import get_resource_manager

# リソースマネージャー取得
rm = get_resource_manager()

# フォント取得
font = rm.get_font("default", size=48)
small_font = rm.get_font("small", size=32)

# サウンド取得
sound = rm.get_sound("perfect.wav")
if sound:
    sound.play()

# 画像取得
image = rm.get_image("background.png")

# プリロード
rm.preload_fonts([32, 48, 64])
rm.preload_sounds(["perfect.wav", "great.wav", "good.wav"])

# メモリ使用量確認
usage = rm.get_memory_usage()
print(usage)  # {'fonts': 3, 'sounds': 3, 'images': 0}
```

**利点**:

- 自動キャッシング（メモリ効率）
- エラーハンドリング統一
- メモリ使用量監視可能

---

## 🔤 型ヒント

### 基本的な型ヒント

```python
from typing import Dict, List, Optional, Tuple, Any

def update_note(
    dt: float,
    t: float,
    bpm_events: List[Dict[str, Any]],
    base_speed: float,
    default_bpm: float
) -> None:
    """ノーツを更新"""
    pass

def get_combo_color(combo: int) -> Tuple[int, int, int]:
    """コンボ数に応じた色を返す"""
    if combo < 30:
        return (80, 120, 255)
    elif combo < 60:
        return (140, 80, 255)
    # ...

def get_resource_manager() -> Optional[ResourceManager]:
    """リソースマネージャーを取得"""
    pass
```

### mypy で型チェック

```bash
# 型チェック実行
mypy classes_professional.py

# 結果
Success: no issues found in 1 source file
```

---

## 📖 ドキュメント（Docstring）

### Google Style Docstring

```python
def process_chart(
    chart: List[Dict[str, Any]],
    difficulty: str
) -> List[Note]:
    """
    譜面を処理してノーツリストに変換

    長い説明がある場合はここに記載します。
    複数行の説明に対応しています。

    Args:
        chart: 譜面データ（JSON 形式）
        difficulty: 難易度 ("EASY", "NORMAL", "HARD", "PRO")

    Returns:
        List[Note]: 処理されたノーツリスト

    Raises:
        ChartLoadError: 譜面の形式が不正な場合

    Example:
        >>> chart = [{"time": 0.5, "lane": 0, "type": "short"}]
        >>> notes = process_chart(chart, "NORMAL")
        >>> len(notes)
        1
    """
    # 実装
    pass
```

---

## 🎯 使用方法

### 最小限の例

```python
import pygame
from config import Config
from logger import get_logger
from resource_manager import get_resource_manager

# 初期化
pygame.init()
pygame.mixer.init()

# ロガー取得
logger = get_logger(__name__)
logger.info("ゲームを起動します")

# 設定読み込み
config = Config.load()

# リソースマネージャー取得
rm = get_resource_manager()

# フォントプリロード
rm.preload_fonts([32, 48, 64])

logger.info(f"解像度: {config.screen.width}x{config.screen.height}")
logger.info(f"難易度: {config.game.difficulty}")

# ゲーム開始
# ...

pygame.quit()
logger.info("ゲームを終了します")
```

---

## 🚀 ベストプラクティス

### 1. 常にロギングを使用

```python
# ❌ 悪い例
print("ゲーム開始")

# ✅ 良い例
from logger import info
info("ゲームを起動しました")
```

### 2. 例外処理は適切に

```python
# ❌ 悪い例
try:
    sound = pygame.mixer.Sound("file.wav")
except:
    pass  # 何もしない

# ✅ 良い例
from exceptions import AudioLoadError
from logger import get_logger

logger = get_logger(__name__)

try:
    sound = pygame.mixer.Sound("file.wav")
except FileNotFoundError:
    logger.error("サウンドファイルが見つかりません")
    raise AudioLoadError("サウンドロード失敗")
except Exception as e:
    logger.error(f"サウンドロードエラー: {e}")
    raise AudioLoadError(f"予期しないエラー: {e}")
```

### 3. 型ヒントは必須

```python
# ❌ 悪い例
def get_color(combo):
    if combo < 30:
        return (80, 120, 255)
    return (255, 255, 255)

# ✅ 良い例
from typing import Tuple

def get_color(combo: int) -> Tuple[int, int, int]:
    """コンボに応じた色を返す"""
    if combo < 30:
        return (80, 120, 255)
    return (255, 255, 255)
```

### 4. リソースはマネージャーから

```python
# ❌ 悪い例
font = pygame.font.Font(None, 48)
font2 = pygame.font.Font(None, 48)  # 重複ロード

# ✅ 良い例
from resource_manager import get_resource_manager

rm = get_resource_manager()
font = rm.get_font("default", 48)  # キャッシュから取得
font2 = rm.get_font("default", 48)  # 同じオブジェクト
```

### 5. 設定は Config から

```python
# ❌ 悪い例
WIDTH = 400
HEIGHT = 600
FPS = 60

# ✅ 良い例
from config import Config

config = Config.load()
WIDTH = config.screen.width
HEIGHT = config.screen.height
FPS = config.screen.fps
```

---

## 📋 チェックリスト

新しい機能を追加する際のチェックリスト:

- [ ] 型ヒントを追加した
- [ ] ドキュメント文字列（docstring）を記述した
- [ ] ロギングを適切に配置した
- [ ] 例外処理を実装した
- [ ] unit テストを追加した
- [ ] コードを Black でフォーマットした
- [ ] flake8 で lint チェックした
- [ ] mypy で型チェックした

---

## 🔨 開発ツール

### Code Formatting (Black)

```bash
# コードをフォーマット
black .

# 確認のみ
black --check .
```

### Linting (flake8)

```bash
# 問題を検出
flake8 .

# 特定のファイルをチェック
flake8 classes_professional.py
```

### Type Checking (mypy)

```bash
# 型チェック実行
mypy .

# 厳密モード
mypy --strict .
```

### Testing (pytest)

```bash
# テスト実行
pytest

# カバレッジ付き
pytest --cov=.

# 特定のテストのみ
pytest tests/test_note.py::test_note_creation
```

---

## 📊 コード品質メトリクス

推奨値:

| メトリクス       | 推奨値 |
| ---------------- | ------ |
| 行あたり文字数   | < 100  |
| 関数の行数       | < 50   |
| 複雑度           | < 10   |
| テストカバレッジ | > 80%  |

---

## 🎓 学習リソース

- [PEP 8 - Python Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [Pygame Documentation](https://www.pygame.org/docs/)

---

## 📝 次のステップ

1. ✅ 型ヒント実装完了
2. ✅ ドキュメント完成
3. ✅ エラーハンドリング実装
4. ⏳ Unit テスト作成
5. ⏳ CI/CD パイプライン構築
6. ⏳ GitHub Actions 設定

---

**最終更新**: 2026年5月28日
