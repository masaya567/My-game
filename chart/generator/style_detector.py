import numpy as np

class StyleDetector:
    @staticmethod
    def detect(bands):
        melody_energy = np.mean(list(bands.get("melody", {}).values()))
        drum_energy = (
            np.mean(list(bands.get("kick", {}).values())) +
            np.mean(list(bands.get("snare", {}).values())) +
            np.mean(list(bands.get("hihat", {}).values()))
        )

        if melody_energy > drum_energy * 1.3:
            return "melody"
        elif drum_energy > melody_energy * 1.3:
            return "rhythm"
        else:
            return "balanced"
