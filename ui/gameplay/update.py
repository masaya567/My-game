import pygame


def update_gameplay(screen_obj, dt):

    logic = screen_obj.logic
    song = screen_obj.song

    # ============================================================
    # ノーツ更新（動的判定・動的速度）
    # ============================================================
    song_time = screen_obj.song_time
    base_speed = screen_obj.speed
    bpm_events = getattr(song, "bpm_events", [])
    song_bpm = getattr(song, "bpm", 120)

    logic.update(
        dt,
        song_time,
        base_speed,
        bpm_events,
        song_bpm,
        on_miss=screen_obj.spawn_hit_effect,
    )

    # ============================================================
    # エフェクト更新
    # ============================================================
    screen_obj.effect_manager.update(dt)
    screen_obj.judge_text_anim.update(dt)

    # ============================================================
    # 曲同期パラメータ取得
    # ============================================================
    bpm_factor = song_bpm / 120.0
    energy = getattr(logic, "section_energy", 0.5)  # Aメロ/サビの盛り上がり
    volume = getattr(logic, "current_volume", 0.5)  # 現在の音量

    energy_factor = 0.6 + energy * 0.8
    volume_factor = 0.5 + volume * 1.2

    # ============================================================
    # UI演出更新（曲同期版）
    # ============================================================

    # 判定ライン波紋
    screen_obj.line_wave += dt * 20 * bpm_factor
    screen_obj.line_wave_strength *= 0.90

    # 背景脈動
    screen_obj.bg_pulse += dt * 15 * bpm_factor
    screen_obj.bg_pulse_strength *= 0.90 * energy_factor

    # フィーバー
    screen_obj.fever_phase += dt * 8 * bpm_factor
    screen_obj.fever_strength *= 0.90

    # コンボフラッシュ
    screen_obj.combo_flash_phase += dt * 6 * bpm_factor
    screen_obj.combo_flash *= 0.88

    # レーン発光（音量同期）
    screen_obj.line_flash *= 0.85
    if screen_obj.line_flash < 1.0:
        screen_obj.line_flash = 0.0


    # ============================================================
    # 楽曲終了
    # ============================================================
    if logic.is_finished():
        pygame.mixer.music.stop()
        screen_obj.play_se("se_decide")
        screen_obj.request_transition(
            (
                "result",
                {
                    "score": logic.score,
                    "max_combo": logic.max_combo,
                    "perfect": logic.perfect,
                    "great": logic.great,
                    "good": logic.good,
                    "miss": logic.miss,
                    "song": screen_obj.song,
                },
            )
        )
