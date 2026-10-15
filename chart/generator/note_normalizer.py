def normalize_notes(notes):
    """
    商用品質：完全版 normalize_notes
    - ロング中ショート削除（同 lane）
    - head/tail 同時刻ショート削除（同 lane）
    - ロング前後ショート調整（全 lane）
    - ロング同士の衝突除去（全 lane）
    - multi-lane 同時刻ショート → 階段変換
    - melody 優先
    """

    PEAK_PRIORITY = {
        "melody": 3,
        "snare": 2,
        "hihat": 1,
        "kick": 0,
    }

    # lane ごとに分ける
    lanes = {0: [], 1: [], 2: [], 3: []}
    for n in notes:
        lanes[n["lane"]].append(n)

    cleaned = []

    # ============================================================
    # 1. lane 内のロング・ショート衝突除去
    # ============================================================
    for lane, lane_notes in lanes.items():
        lane_notes.sort(key=lambda n: n["time"])

        i = 0
        while i < len(lane_notes):
            note = lane_notes[i]

            if note["type"] == "long":
                head = note["time"]
                tail = note["end_time"]

                # ロング中ショート削除
                j = i + 1
                while j < len(lane_notes):
                    other = lane_notes[j]
                    if other["type"] == "tap" and head <= other["time"] <= tail:
                        lane_notes.pop(j)
                        continue
                    j += 1

                # head/tail 同時刻ショート削除
                j = i + 1
                while j < len(lane_notes):
                    other = lane_notes[j]
                    if other["type"] == "tap" and abs(other["time"] - head) < 0.001:
                        lane_notes.pop(j)
                        continue
                    if other["type"] == "tap" and abs(other["time"] - tail) < 0.001:
                        lane_notes.pop(j)
                        continue
                    j += 1

            i += 1

        cleaned.extend(lane_notes)

    # ============================================================
    # 2. ロング前後ショートの自然なズレ補正（全 lane）
    # ============================================================
    for n in cleaned:
        if n["type"] == "long":
            head = n["time"]
            tail = n["end_time"]

            for other in cleaned:
                if other["type"] != "tap":
                    continue

                dt = other["time"] - head
                if 0 < dt < 0.05:
                    other["time"] += 0.012

                dt2 = tail - other["time"]
                if 0 < dt2 < 0.05:
                    other["time"] -= 0.012

    # ============================================================
    # 3. ロング同士の衝突除去（全 lane）
    # ============================================================
    cleaned.sort(key=lambda n: (n["lane"], n["time"]))
    last_long_end = {0: -1e9, 1: -1e9, 2: -1e9, 3: -1e9}

    for n in cleaned:
        if n["type"] == "long":
            lane = n["lane"]
            if n["time"] < last_long_end[lane]:
                n["type"] = "tap"
                n["end_time"] = n["time"]
            else:
                last_long_end[lane] = n["end_time"]

    # ============================================================
    # 4. multi-lane 同時刻ショート → 階段変換
    # ============================================================
    cleaned.sort(key=lambda n: n["time"])

    final = []
    i = 0
    while i < len(cleaned):
        group = [cleaned[i]]
        t = cleaned[i]["time"]

        j = i + 1
        while j < len(cleaned) and abs(cleaned[j]["time"] - t) < 0.0005:
            group.append(cleaned[j])
            j += 1

        if len(group) == 1:
            final.append(group[0])
            i = j
            continue

        longs = [g for g in group if g["type"] == "long"]
        if longs:
            final.append(longs[0])
            i = j
            continue

        group.sort(key=lambda g: -PEAK_PRIORITY.get(g["peak_type"], 0))

        base_lane = group[0]["lane"]
        for k, g in enumerate(group):
            g["lane"] = (base_lane + k) % 4
            final.append(g)

        i = j

    # ============================================================
    # 5. 最終ソート
    # ============================================================
    final.sort(key=lambda n: n["time"])
    return final
