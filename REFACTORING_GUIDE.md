# 🎮 Piano Tiles - コード分割ガイド

## 📂 新しいファイル構成

```
mygame/
├── main.py                 # ★ メインプログラム（簡潔化予定）
├── constants.py            # 定数・設定値（画面サイズ、色、判定範囲など）
├── classes.py              # ゲームクラス（Note、Effect、UI要素など）
├── chart_generator.py      # 譜面自動生成ロジック
├── utils.py                # ユーティリティ関数（テキスト処理、フォント取得など）
├── ui_screens.py           # UI画面（タイトル、オプション、選曲など）
├── game_loop.py            # ★ ゲームループ（未作成）
│
├── ✅ assets/              # 既存のアセット
│   ├── music/
│   └── sounds/
│
└── ✅ JSON ファイル        # 既存の譜面データ
    ├── erize_chart.json
    ├── moonlight_chart.json
    └── ...
```

---

## 📖 各ファイルの役割

### 1️⃣ **constants.py** ✅ 完成

- **画面サイズ**: WIDTH, HEIGHT, LANES
- **判定範囲**: PERFECT_RANGE, GREAT_RANGE, GOOD_RANGE
- **色定義**: 全ての色を一元管理
- **UI パラメータ**: ボタン色、テキスト色など
- **譜面生成パラメータ**: 難易度別設定

📌 **使用方法**:

```python
from constants import WIDTH, HEIGHT, WHITE, BLACK
```

---

### 2️⃣ **classes.py** ✅ 完成

以下のクラスを実装:

- **Note**: ノーツの描画・判定・動作管理
- **NoteTrail**: ノーツタイル
- **BackgroundNote**: 背景ノーツ
- **BGTile**: 背景タイル
- **JudgeEffect**: 判定エフェクト（Perfect/Great/Good/Miss）
- **RippleEffect**: 波紋エフェクト
- **LongEndEffect**: ロング終了エフェクト
- **ShortHitEffect**: 短音符ヒットエフェクト
- **BGGlow**: 背景発光
- **JudgeBeam**: 判定ラインの光

📌 **使用方法**:

```python
from classes import Note, JudgeEffect, BGTile
```

---

### 3️⃣ **chart_generator.py** ✅ 完成

譜面自動生成機能:

- `auto_generate_chart(song, difficulty)`: 難易度別生成
- `generate_easy(bpm, length)`: EASY（4分のみ）
- `generate_normal(bpm, length)`: NORMAL（4分 + 8分）
- `generate_hard(bpm, length)`: HARD（4分 + 8分 + 16分）
- `generate_pro(song, limit_time)`: PRO（音声解析版）

📌 **使用方法**:

```python
from chart_generator import auto_generate_chart
chart = auto_generate_chart(song, "NORMAL")
```

---

### 4️⃣ **utils.py** ✅ 完成

ユーティリティ関数:

- `render_fit_text()`: テキスト自動縮小
- `wrap_text()`: 日本語対応折り返し
- `load_chart()`: JSON 譜面読み込み
- `get_combo_bg_color()`: コンボ色判定
- `make_jacket()`: ジャケット生成
- `get_system_font()`: 日本語フォント取得

📌 **使用方法**:

```python
from utils import wrap_text, render_fit_text, get_system_font
```

---

### 5️⃣ **ui_screens.py** ✅ 完成

UI 画面関数:

- `title_screen()`: タイトル画面
- `option_screen()`: オプション画面
- `change_difficulty_screen()`: 難易度変更
- `change_speed_screen()`: 速度変更
- `key_config_screen()`: キー設定
- `how_to_play_screen()`: あそびかた画面

📌 **使用方法**:

```python
from ui_screens import title_screen, option_screen
```

---

### 6️⃣ **game_loop.py** ⏳ 未作成

以下を予定:

- `game_loop(selected_song, key_config)`: メインゲームループ
- `song_select_screen()`: 選曲画面
- `result_screen()`: リザルト画面
- `build_notes_from_chart()`: 譜面から Note に変換
- `spawn_notes_from_chart()`: BPM 対応 Note 生成

---

## 🔄 main.py の改善予定

現在の `main.py` は以下のように改善します:

```python
import pygame
from constants import *
from classes import *
from chart_generator import auto_generate_chart
from utils import get_system_font, load_chart
from ui_screens import *
from game_loop import game_loop, song_select_screen, result_screen

# 初期化
pygame.init()
pygame.mixer.init()

# ゲーム設定
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Tiles")
clock = pygame.time.Clock()

# フォント取得
font, font_small, font_large, font_medium = get_system_font()

# 曲データロード
songs = [...]  # song_list.py に移動予定

def main():
    while True:
        result = title_screen(...)
        if result:
            difficulty, speed_level, key_config, selected_song, mode = result
            # ゲームループ実行
            ...

if __name__ == "__main__":
    main()
```

---

## 🎯 使用方法

### インポート例

```python
# 定数を使う
from constants import WIDTH, HEIGHT, JUDGE_LINE

# ゲームクラスを使う
from classes import Note, JudgeEffect

# 譜面生成
from chart_generator import generate_normal

# ユーティリティ
from utils import wrap_text, load_chart

# UI 画面
from ui_screens import title_screen, option_screen
```

---

## 📌 注意点

1. **全てのモジュール間で constants.py をインポート** して定数を共有
2. **pygame の初期化** は `main.py` で一度だけ実行
3. **グローバル変数** は最小限に（各画面の内部変数を使う）
4. **song リスト** は後で `song_list.py` に分離予定

---

## 🚀 次のステップ

1. ✅ `constants.py` - 完成
2. ✅ `classes.py` - 完成
3. ✅ `chart_generator.py` - 完成
4. ✅ `utils.py` - 完成
5. ✅ `ui_screens.py` - 完成
6. ⏳ `game_loop.py` - 作成予定
7. ⏳ `main.py` - 簡潔化
8. ⏳ `song_list.py` - 作成予定（曲データ管理）

---

## 📝 利点

✅ **コードの再利用性向上** - 各モジュールが独立している
✅ **保守性向上** - 機能ごとにファイルを分けているので修正が簡単
✅ **テストしやすい** - 各モジュールを個別にテスト可能
✅ **スケーラビリティ** - 新機能追加が容易
✅ **チーム開発対応** - 複数人で同時に開発可能
