import math
import pygame
import colorsys
from constants import WIDTH, HEIGHT, JUDGE_LINE, LANE_WIDTH, UI_SCALE


def _clamp_alpha(value):
    return max(0, min(255, int(value)))


def _get_lane_positions(screen_obj):
    lane_x = getattr(screen_obj, "lane_x", None)
    if lane_x is not None:
        return lane_x

    try:
        from constants import LANE_X
        return LANE_X
    except Exception:
        pass

    lane_count = 4
    lane_width = max(1, WIDTH // lane_count)
    return [int((i + 0.5) * lane_width) for i in range(lane_count)]


def draw_gameplay(screen_obj, screen):
    # ============================================================
    # 背景
    # ============================================================
    if hasattr(screen_obj, "lane_bg_surface"):
        screen.blit(screen_obj.lane_bg_surface, (0, 0))
    else:
        screen.fill((20, 20, 20))

    song = getattr(screen_obj, "song", None)
    bpm = getattr(getattr(song, "audio_analyzer", None), "bpm", 120)
    pulse_speed = bpm / 120.0

    bg_pulse_strength = getattr(screen_obj, "bg_pulse_strength", 0.0)
    bg_pulse = getattr(screen_obj, "bg_pulse", 0.0)
    fever_strength = getattr(screen_obj, "fever_strength", 0.0)
    fever_phase = getattr(screen_obj, "fever_phase", 0.0)
    combo_flash = getattr(screen_obj, "combo_flash", 0.0)
    combo_flash_phase = getattr(screen_obj, "combo_flash_phase", 0.0)
    line_wave = getattr(screen_obj, "line_wave", 0.0)
    line_wave_strength = getattr(screen_obj, "line_wave_strength", 0.0)
    line_flash = getattr(screen_obj, "line_flash", 0.0)
    line_flash_lane = getattr(screen_obj, "line_flash_lane", None)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # ============================================================
    # BPM 脈動 / フィーバー / コンボ虹色フラッシュ
    # ============================================================
    if bg_pulse_strength > 0.0:
        pulse = (math.sin(bg_pulse * pulse_speed) * 0.5 + 0.5) * bg_pulse_strength
        overlay.fill((80, 120, 255, _clamp_alpha(pulse)))
        screen.blit(overlay, (0, 0))

    if fever_strength > 0.0:
        fever_pulse = (math.sin(fever_phase) * 0.5 + 0.5) * fever_strength
        overlay.fill((255, 200, 80, _clamp_alpha(fever_pulse)))
        screen.blit(overlay, (0, 0))

    if combo_flash > 0.1:
        hue = math.sin(combo_flash_phase) * 0.5 + 0.5
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        overlay.fill((int(r * 255), int(g * 255), int(b * 255), _clamp_alpha(combo_flash)))
        screen.blit(overlay, (0, 0))

    # ============================================================
    # 判定ライン（UI_SCALE 対応）
    # ============================================================
    lane_colors = [
        (255, 120, 120),
        (120, 255, 120),
        (120, 120, 255),
        (255, 255, 120),
    ]

    logic = getattr(screen_obj, "logic", None)
    active_lane = getattr(logic, "last_judged_lane", None) if logic else None

    line_color = lane_colors[active_lane] if active_lane is not None else (255, 255, 255)
    if fever_strength > 0.5:
        line_color = (255, 220, 120)

    wobble = math.sin(getattr(screen_obj, "song_time", 0.0) * (bpm / 240.0)) * 1.2
    offset = int((math.sin(line_wave) * line_wave_strength + wobble) * UI_SCALE)

    if hasattr(screen_obj, "judge_line_surface"):
        surf = screen_obj.judge_line_surface
        surf.fill((*line_color, 220))
        screen.blit(surf, (0, int(JUDGE_LINE + offset)))
    else:
        pygame.draw.line(
            screen,
            line_color,
            (0, int(JUDGE_LINE + offset)),
            (WIDTH, int(JUDGE_LINE + offset)),
            int(4 * UI_SCALE),
        )

    # ============================================================
    # レーンフラッシュ（UI_SCALE 対応）
    # ============================================================
    if line_flash > 1.0:
        lane_x_positions = _get_lane_positions(screen_obj)
        if line_flash_lane is not None and 0 <= line_flash_lane < len(lane_x_positions):
            lane_x = lane_x_positions[line_flash_lane]
            surf = screen_obj.lane_flash_surface
            surf.set_alpha(_clamp_alpha(line_flash))
            screen.blit(
                surf,
                (
                    lane_x - int(LANE_WIDTH * UI_SCALE) // 2,
                    int(JUDGE_LINE + offset - 20 * UI_SCALE),
                ),
            )

    # ============================================================
    # ノーツ描画（UI_SCALE 対応）
    # ============================================================
    notes = getattr(logic, "notes", []) if logic else []

    long_notes = [n for n in notes if getattr(n, "is_long", False)]
    tap_notes = [n for n in notes if not getattr(n, "is_long", False)]

    # ロングノート
    for note in long_notes:
        try:
            x = getattr(note, "x", None)
            head_y = getattr(note, "head_y", None)
            tail_y = getattr(note, "tail_y", None)
            if x is None or head_y is None or tail_y is None:
                continue

            cx = x - screen_obj.long_head.get_width() // 2

            screen.blit(screen_obj.long_head, (cx, head_y))

            top_y = min(head_y, tail_y)
            body_h = abs(tail_y - head_y)

            if body_h <= 0:
                screen.blit(screen_obj.long_tail, (cx, tail_y))
                continue

            max_body_h = screen_obj.long_body.get_height()
            body_h = min(body_h, max_body_h)

            src_rect = pygame.Rect(0, 0, screen_obj.long_body.get_width(), body_h)
            body = screen_obj.long_body.subsurface(src_rect)

            screen.blit(body, (cx, top_y))
            screen.blit(screen_obj.long_tail, (cx, tail_y))

        except Exception:
            continue

    # タップノート
    for note in tap_notes:
        try:
            x = getattr(note, "x", None)
            y = getattr(note, "head_y", None)
            if x is None or y is None:
                continue

            cx = x - screen_obj.short_body.get_width() // 2
            cy = y - screen_obj.short_body.get_height() // 2

            screen_obj.short_glow.set_alpha(90)
            screen.blit(
                screen_obj.short_glow,
                (cx - int(10 * UI_SCALE), cy - int(10 * UI_SCALE)),
            )

            screen.blit(screen_obj.short_body, (cx, cy))

        except Exception:
            continue

    # ============================================================
    # 統合エフェクト
    # ============================================================
    effect_manager = getattr(screen_obj, "effect_manager", None)
    if effect_manager:
        try:
            effect_manager.draw(screen)
        except Exception:
            pass

    judge_text_anim = getattr(screen_obj, "judge_text_anim", None)
    if judge_text_anim:
        try:
            judge_text_anim.draw(screen)
        except Exception:
            pass

    # ============================================================
    # スコア・コンボ（UI_SCALE 対応）
    # ============================================================
    res = getattr(screen_obj, "res", None)
    font = None
    if res is not None:
        try:
            font = res.get_font(int(32 * UI_SCALE), weight="medium")
        except Exception:
            font = None
    if font is None:
        font = pygame.font.SysFont(None, int(32 * UI_SCALE))

    score = getattr(logic, "score", 0) if logic else 0
    combo = getattr(logic, "combo", 0) if logic else 0

    score_surf = font.render(f"スコア: {score}", True, (255, 255, 255))
    combo_surf = font.render(f"コンボ: {combo}", True, (255, 200, 120))

    combo_scale = 1.0 + min(0.3, combo * 0.002)
    cw, ch = combo_surf.get_width(), combo_surf.get_height()
    combo_surf = pygame.transform.scale(
        combo_surf,
        (int(cw * combo_scale), int(ch * combo_scale)),
    )

    screen.blit(score_surf, (int(20 * UI_SCALE), int(20 * UI_SCALE)))
    screen.blit(combo_surf, (int(20 * UI_SCALE), int(70 * UI_SCALE)))

    # フェード
    draw_fade = getattr(screen_obj, "draw_fade", None)
    if callable(draw_fade):
        try:
            draw_fade(screen)
        except Exception:
            pass
