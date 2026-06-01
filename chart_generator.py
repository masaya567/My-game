import random
import json
import os


# ---------------------------------------------------------
# ★ 難易度別 自動譜面生成（完全版）
# ---------------------------------------------------------
def auto_generate_chart(song, difficulty="NORMAL"):
    """難易度別の自動譜面生成"""
    bpm = song["bpm"]
    length = song["length"]

    if difficulty == "EASY":
        return generate_easy(bpm, length)
    elif difficulty == "NORMAL":
        return generate_normal(bpm, length)
    elif difficulty == "HARD":
        return generate_hard(bpm, length)
    elif difficulty == "PRO":
        return generate_pro(song, length)
    else:
        print("未知の難易度:", difficulty)
        return []


# ---------------------------------------------------------
# EASY
# ---------------------------------------------------------
def generate_easy(bpm, length):
    """EASY（4分）"""
    beat = 60 / bpm
    chart = []
    t = 0
    last_long_end = -1

    while t < length:
        if t < last_long_end:
            t += beat * 0.5
            continue

        lane = random.randint(0, 3)

        if random.random() < 0.02:
            duration = beat * random.randint(2, 3)
            end = t + duration
            chart.append(
                {
                    "time": round(t, 3),
                    "lane": lane,
                    "type": "long",
                    "end": round(end, 3),
                }
            )
            last_long_end = end
            t += duration
            continue

        chart.append({"time": round(t, 3), "lane": lane, "type": "short"})
        t += beat * 1.5

    return chart


# ---------------------------------------------------------
# NORMAL
# ---------------------------------------------------------
def generate_normal(bpm, length):
    """NORMAL（4分＋8分）"""
    beat = 60 / bpm
    chart = []
    t = 0
    last_long_end = -1

    while t < length:
        if t < last_long_end:
            t += beat * 0.25
            continue

        step = beat
        lane = random.randint(0, 3)

        if random.random() < 0.08:
            duration = random.choice([beat * 2, beat * 3])
            end = t + duration
            chart.append(
                {
                    "time": round(t, 3),
                    "lane": lane,
                    "type": "long",
                    "end": round(end, 3),
                }
            )
            last_long_end = end
            t += duration
            continue

        chart.append({"time": round(t, 3), "lane": lane, "type": "short"})
        t += beat

    return chart


# ---------------------------------------------------------
# HARD
# ---------------------------------------------------------
def generate_hard(bpm, length):
    """HARD（4分＋8分＋16分＋ロング）"""
    beat = 60 / bpm
    chart = []
    t = 0
    last_long_end = -1

    while t < length:
        if t < last_long_end:
            t += beat * 0.125
            continue

        step = random.choice([beat, beat / 2])
        lane = random.randint(0, 3)

        if random.random() < 0.08:
            duration = random.choice([beat * 2, beat * 3, beat * 4])
            end = t + duration
            chart.append(
                {
                    "time": round(t, 3),
                    "lane": lane,
                    "type": "long",
                    "end": round(end, 3),
                }
            )
            last_long_end = end
            t += duration
            continue

        chart.append({"time": round(t, 3), "lane": lane, "type": "short"})
        t += step

    return chart


# ---------------------------------------------------------
# PRO（音声解析版）
# ---------------------------------------------------------
def generate_pro(song, limit_time):
    """PRO（音声解析版）"""
    onset_times = song["pro_onset_times"]
    rms = song["pro_rms"]
    centroid_norm = song["pro_centroid_norm"]

    chart = []
    last_long_end = -1

    for i, t in enumerate(onset_times):
        if t > limit_time:
            break

        if t < last_long_end:
            continue

        vol = rms[min(i, len(rms) - 1)]
        if random.random() > min(1.0, vol * 3):
            continue

        c = centroid_norm[min(i, len(centroid_norm) - 1)]
        lane = int(c * 3.99)

        if vol > 0.1 and t - last_long_end > 0.5 and random.random() < 0.15:
            end = t + random.uniform(0.3, 1.2)
            chart.append(
                {
                    "time": round(t, 3),
                    "lane": lane,
                    "type": "long",
                    "end": round(end, 3),
                }
            )
            last_long_end = end
            continue

        chart.append({"time": round(t, 3), "lane": lane, "type": "short"})

    return chart


# ---------------------------------------------------------
# ★ 全曲一括生成（完全版）
# ---------------------------------------------------------
def generate_all_charts(songs, difficulty="NORMAL"):
    """全曲の譜面を一括生成して JSON に保存"""
    for song in songs:
        chart = auto_generate_chart(song, difficulty)
        filename = song["title"].replace(" ", "_") + "_chart.json"
        path = os.path.join(os.getcwd(), filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(chart, f, ensure_ascii=False, indent=2)

        print(f"✔ {filename} を生成しました（{len(chart)} ノーツ）")


# ---------------------------------------------------------
# ★ 直接実行されたときだけ動く
# ---------------------------------------------------------
if __name__ == "__main__":
    from songs import songs  # ← あなたの songs.py のリストを読み込む

    generate_all_charts(songs, difficulty="NORMAL")
