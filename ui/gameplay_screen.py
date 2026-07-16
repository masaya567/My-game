import pygame
from ui.base_screen import BaseScreen
from constants import WIDTH, HEIGHT, JUDGE_LINE
from game.update.effect_update import update_effects, draw_effects

# ★ ① 判定文字アニメーションを読み込む
from graphics.judge_text_anim import JudgeTextAnim


class GameplayScreen(BaseScreen):
    """
    商用品質：GameLogic + Note クラス完全統合版ゲームプレイ画面
    """

    def __init__(self, manager, song, logic, speed=1.0):
        super().__init__(manager)

        self.song = song
        self.logic = logic
        self.speed = speed

        # 曲再生
        pygame.mixer.music.load(self.song.file)
        pygame.mixer.music.play()

        self.start_time = pygame.time.get_ticks() / 1000.0

        # レーン位置
        self.lane_x = [200, 350, 500, 650]

        # ★ ② 判定文字アニメーションを初期化
        self.judge_text_anim = JudgeTextAnim(self.res)

    # ============================================================
    # 更新処理
    # ============================================================

    def update(self, dt):
        song_time = pygame.time.get_ticks() / 1000.0 - self.start_time

        # ノーツ更新（落下 + BPM補正）
        self.logic.update_notes(dt, song_time, self.speed)

        # 自動ミス判定
        self.logic.auto_miss_check()

        # エフェクト更新
        update_effects(dt)

        # ★ ③ 判定文字アニメーション更新
        self.judge_text_anim.update(dt)

        # 曲終了判定
        if self.logic.is_finished():
            pygame.mixer.music.stop()
            self.play_se("se_decide")
            self.request_transition(
                (
                    "result",
                    {
                        "score": self.logic.score,
                        "max_combo": self.logic.max_combo,
                        "perfect": self.logic.perfect,
                        "great": self.logic.great,
                        "good": self.logic.good,
                        "miss": self.logic.miss,
                        "song": self.song,
                    },
                )
            )

    # ============================================================
    # 描画処理
    # ============================================================

    def draw(self, screen):
        screen.fill((20, 20, 20))

        # 判定ライン
        pygame.draw.line(screen, (255, 255, 255), (0, JUDGE_LINE), (WIDTH, JUDGE_LINE), 4)

        # ノーツ描画（Note クラス対応）
        for note in self.logic.notes:
            x = self.lane_x[note.lane]

            # ショートノーツ
            if not note.is_long:
                pygame.draw.circle(screen, (120, 200, 255), (x, int(note.head_y)), 25)

            # ロングノーツ
            else:
                pygame.draw.rect(
                    screen,
                    (255, 180, 120),
                    pygame.Rect(x - 15, int(note.tail_y), 30, int(note.head_y - note.tail_y)),
                    border_radius=10,
                )
                pygame.draw.circle(screen, (255, 180, 120), (x, int(note.head_y)), 25)

        # エフェクト描画
        draw_effects(screen)

        # ★ ④ 判定文字アニメーション描画
        self.judge_text_anim.draw(screen)

        # スコア・コンボ
        font = self.res.get_font(32, weight="medium")
        score_surf = font.render(f"Score: {self.logic.score}", True, (255, 255, 255))
        combo_surf = font.render(f"Combo: {self.logic.combo}", True, (255, 200, 120))

        screen.blit(score_surf, (20, 20))
        screen.blit(combo_surf, (20, 70))

        # フェード描画
        self.draw_fade(screen)

    # ============================================================
    # 入力処理
    # ============================================================

    def handle_event(self, event):
        song_time = pygame.time.get_ticks() / 1000.0 - self.start_time

        if event.type == pygame.KEYDOWN:

            # レーン入力
            if event.key == pygame.K_d:
                result = self.logic.try_judge(0, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[0], JUDGE_LINE)

            elif event.key == pygame.K_f:
                result = self.logic.try_judge(1, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[1], JUDGE_LINE)

            elif event.key == pygame.K_j:
                result = self.logic.try_judge(2, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[2], JUDGE_LINE)

            elif event.key == pygame.K_k:
                result = self.logic.try_judge(3, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[3], JUDGE_LINE)

            # ESC → タイトルへ
            elif event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.play_se("se_back")
                self.request_transition("title")

        # ロングノーツのキー離し判定
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                result = self.logic.release_judge(0, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[0], JUDGE_LINE)

            elif event.key == pygame.K_f:
                result = self.logic.release_judge(1, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[1], JUDGE_LINE)

            elif event.key == pygame.K_j:
                result = self.logic.release_judge(2, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[2], JUDGE_LINE)

            elif event.key == pygame.K_k:
                result = self.logic.release_judge(3, song_time)
                if result != "none":
                    self.judge_text_anim.trigger(result, self.lane_x[3], JUDGE_LINE)
