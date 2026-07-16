"""
商用品質：ノーツ速度制御モジュール（完全版・最終形態）

BPM変化・難易度補正・AUTO SPEED・リアルタイム補間を統合管理する。
"""

from game.constants import DIFFICULTY_MULTIPLIER


class SpeedController:
    """
    商用品質：ノーツ速度制御クラス
    """

    def __init__(self, bpm=120, difficulty="NORMAL", base_speed_level=1.0):
        self.base_bpm = bpm
        self.current_bpm = bpm
        self.target_bpm = bpm

        self.transition_time = 0.0
        self.elapsed = 0.0

        self.difficulty = difficulty
        self.multiplier = DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)

        # AUTO SPEED（曲特徴から決まる速度）
        self.base_speed_level = base_speed_level

        # 初期速度
        self.note_speed = self._calculate_speed(bpm)

    # ============================================================
    # BPM変更処理
    # ============================================================

    def set_bpm(self, bpm, transition_time=0.0):
        """BPMを変更（スムーズな補間対応）"""
        self.base_bpm = self.current_bpm  # ★補間の基準を更新
        self.target_bpm = bpm
        self.transition_time = transition_time
        self.elapsed = 0.0

        # 即時変更の場合は同期
        if transition_time == 0:
            self.current_bpm = bpm
            self.note_speed = self._calculate_speed(bpm)

    # ============================================================
    # 時間補間
    # ============================================================

    def update(self, dt):
        """時間経過に応じてBPMを補間"""
        if self.transition_time > 0:
            self.elapsed += dt
            t = min(self.elapsed / self.transition_time, 1.0)
            self.current_bpm = self._lerp(self.base_bpm, self.target_bpm, t)
        else:
            self.current_bpm = self.target_bpm

        self.note_speed = self._calculate_speed(self.current_bpm)

    # ============================================================
    # 速度計算（AUTO SPEED + BPM補正 + 難易度補正）
    # ============================================================

    def _calculate_speed(self, bpm):
        """
        BPMからノーツ落下速度を計算
        AUTO SPEED（曲特徴）と難易度倍率を統合
        """
        bpm_factor = bpm / 120.0
        return self.base_speed_level * bpm_factor * self.multiplier

    # ============================================================
    # 補間関数
    # ============================================================

    def _lerp(self, a, b, t):
        """線形補間"""
        return a + (b - a) * t

    # ============================================================
    # 情報取得
    # ============================================================

    def get_speed_info(self):
        """現在の速度情報を辞書形式で取得"""
        return {
            "current_bpm": round(self.current_bpm, 2),
            "note_speed": round(self.note_speed, 3),
            "difficulty": self.difficulty,
            "base_speed_level": self.base_speed_level,
        }

    def reset(self):
        """速度情報をリセット"""
        self.current_bpm = self.base_bpm
        self.target_bpm = self.base_bpm
        self.note_speed = self._calculate_speed(self.base_bpm)
        self.elapsed = 0.0
