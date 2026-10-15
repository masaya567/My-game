from constants import JUDGE_LINE

def spawn_hit_effect(screen_obj, lane, judge_text):
    lane_x = screen_obj.lane_x[lane]
    lane_center_x = lane_x

    screen_obj.logic.last_judged_lane = lane
    jt = judge_text.lower()

    strength_map = {
        "perfect": 1.0,
        "great": 0.7,
        "good": 0.4,
        "miss": 0.2,
    }
    strength = strength_map.get(jt, 0.5)

    # BPM に応じた演出強度補正（追加）
    bpm_factor = getattr(screen_obj.song, "bpm", 120) / 120

    if jt == "miss":
        screen_obj.effect_manager.spawn_combo_break(lane_x)

    screen_obj.effect_manager.spawn_hit_effect(
        lane_x,
        judge_text,
        screen_obj.res.get_font(48, weight="bold"),
        strength=strength,
    )

    screen_obj.judge_text_anim.trigger(judge_text, lane_center_x, JUDGE_LINE)

    if jt == "perfect":
        screen_obj.line_wave_strength = 10 * bpm_factor
        screen_obj.line_flash_lane = lane
        screen_obj.line_flash = 120
    elif jt == "great":
        screen_obj.line_wave_strength = 6 * bpm_factor
        screen_obj.line_flash_lane = lane
        screen_obj.line_flash = 60
    else:
        screen_obj.line_wave_strength = 0

    if jt == "perfect":
        screen_obj.effect_manager.spawn_hit_flash(lane_x)

    combo = screen_obj.logic.combo
    if combo >= 300:
        screen_obj.bg_pulse_strength = 80
    elif combo >= 200:
        screen_obj.bg_pulse_strength = 60
    elif combo >= 100:
        screen_obj.bg_pulse_strength = 40
    elif combo >= 50:
        screen_obj.bg_pulse_strength = 25
    else:
        screen_obj.bg_pulse_strength = 0

    if combo == 500:
        screen_obj.combo_flash = 120
    elif combo == 1000:
        screen_obj.combo_flash = 200

    if combo == 2000:
        screen_obj.combo_flash = 255
        screen_obj.line_flash = 200
        screen_obj.effect_manager.spawn_combo_ring(lane_center_x, JUDGE_LINE)

    if jt == "perfect":
        screen_obj.perfect_chain += 1
        screen_obj.fever_strength = min(
            120,
            screen_obj.fever_strength + screen_obj.perfect_chain * 2
        )
    else:
        screen_obj.perfect_chain = 0
