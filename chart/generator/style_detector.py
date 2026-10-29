import numpy as np

class StyleDetector:
    @staticmethod
    def detect(bands):
        """
        市販譜面生成エンジン用スタイル判定
        - melody（high）主体 → メロディ曲
        - rhythm（low/mid）主体 → 伴奏・リズム曲
        - balanced → 均等
        """

        low_energy  = np.mean(list(bands.get("low", {}).values()) or [0])
        mid_energy  = np.mean(list(bands.get("mid", {}).values()) or [0])
        high_energy = np.mean(list(bands.get("melody", {}).values()) or [0])

        melody_energy = high_energy
        rhythm_energy = (low_energy + mid_energy) * 0.7  # 伴奏は少し弱めに補正

        if melody_energy > rhythm_energy * 1.25:
            return "melody"

        elif rhythm_energy > melody_energy * 1.25:
            return "rhythm"

        else:
            return "balanced"
