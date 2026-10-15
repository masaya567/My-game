class MusicAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def analyze_bands(self):
        return self.analyzer.analyze_bands()

    def detect_sustain(self):
        return self.analyzer.detect_sustain("melody")

    def analyze_sections(self):
        return self.analyzer.analyze_sections()
