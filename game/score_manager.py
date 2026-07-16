"""
商用品質：スコア管理モジュール（完全版・最終形態）

判定結果・コンボ・ランクを統合的に管理する。
GameLogic から判定結果を受け取り、内部状態を更新する。
"""

from game.constants import (
    SCORE_PERFECT,
    SCORE_GREAT,
    SCORE_GOOD,
    SCORE_MISS,
    COMBO_MULTIPLIER,
    RANK_THRESHOLDS,
)


class ScoreManager:
    """
    商用品質：スコア管理クラス
    """

    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.judgments = {"perfect": 0, "great": 0, "good": 0, "miss": 0}
        self.rank = "C"

    # ============================================================
    # 判定処理
    # ============================================================

    def register_judgment(self, judgment: str):
        """
        判定結果を登録してスコアを更新
        judgment は "perfect" / "great" / "good" / "miss"
        """

        judgment = judgment.lower()

        base_score = self._get_base_score(judgment)

        if judgment != "miss":
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)

            # コンボボーナス（10コンボごとに倍率上昇）
            combo_bonus = COMBO_MULTIPLIER ** (self.combo // 10)
            self.score += int(base_score * combo_bonus)

        else:
            self.combo = 0  # コンボ切れ

        # 判定カウント
        if judgment in self.judgments:
            self.judgments[judgment] += 1

        # ランク更新
        self._update_rank()

    # ============================================================
    # スコア基準
    # ============================================================

    def _get_base_score(self, judgment):
        """判定ごとの基本スコアを取得"""
        return {
            "perfect": SCORE_PERFECT,
            "great": SCORE_GREAT,
            "good": SCORE_GOOD,
            "miss": SCORE_MISS,
        }.get(judgment, 0)

    # ============================================================
    # ランク更新
    # ============================================================

    def _update_rank(self):
        """現在のスコア比率からランクを更新"""
        total_notes = sum(self.judgments.values())
        if total_notes == 0:
            return

        score_ratio = min(1.0, self.score / (total_notes * SCORE_PERFECT))

        for rank, threshold in RANK_THRESHOLDS.items():
            if score_ratio >= threshold:
                self.rank = rank
                break

    # ============================================================
    # 情報取得
    # ============================================================

    def get_summary(self):
        """スコア情報を辞書形式で取得"""
        return {
            "score": self.score,
            "combo": self.combo,
            "max_combo": self.max_combo,
            "judgments": self.judgments,
            "rank": self.rank,
        }

    def reset(self):
        """スコア情報をリセット"""
        self.__init__()
