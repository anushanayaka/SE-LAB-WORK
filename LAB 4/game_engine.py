import pygame
import random
import json
import os

from game.player import Player, LANE_W
from game.traffic import Car, make_car


LANES = 8
WIDTH = LANES * LANE_W
HEIGHT = 600
FPS = 60

# Normal background
BG = (60, 60, 60)

# Task 2: moving log lane
LOG_LANE_Y = 280
LOG_HEIGHT = 50
LOG_WIDTH = 150
LOG_SPEED = 2

# Task 3: high score file
HIGH_SCORE_FILE = "highscores.json"

# Task 4: day/night cycle
DAY_BG = (60, 60, 60)
NIGHT_BG = (15, 20, 35)
DAY_NIGHT_INTERVAL = 30 * FPS


class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Traffic Escape")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("monospace", 24, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 18, bold=True)

        # Task 3
        self.high_scores = self.load_high_scores()

        self.reset()

    # ==========================================
    # TASK 3: LOAD HIGH SCORES
    # ==========================================
    def load_high_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as file:
                    scores = json.load(file)

                if isinstance(scores, list):
                    return sorted(scores, reverse=True)[:5]

            except (json.JSONDecodeError, OSError):
                pass

        return []

    # ==========================================
    # TASK 3: SAVE HIGH SCORES
    # ==========================================
    def save_high_scores(self):
        try:
            with open(HIGH_SCORE_FILE, "w") as file:
                json.dump(self.high_scores, file, indent=4)
        except OSError:
            pass

    # ==========================================
    # TASK 3: ADD SCORE
    # ==========================================
    def add_high_score(self):
        final_score = self.score // 10

        self.high_scores.append(final_score)

        # Sort highest to lowest
        self.high_scores.sort(reverse=True)

        # Keep only top 5
        self.high_scores = self.high_scores[:5]

        # Save to JSON
        self.save_high_scores()

    def reset(self):
        self.player = Player(WIDTH // 2, HEIGHT - 80)
        self.cars = []

        # Task 2: create moving logs
        self.logs = [
            pygame.Rect(
                20,
                LOG_LANE_Y,
                LOG_WIDTH,
                LOG_HEIGHT
            ),
            pygame.Rect(
                300,
                LOG_LANE_Y,
                LOG_WIDTH,
                LOG_HEIGHT
            ),
            pygame.Rect(
                580,
                LOG_LANE_Y,
                LOG_WIDTH,
                LOG_HEIGHT
            )
        ]

        self.timer = 0
        self.spawn_interval = 50
        self.speed = 3
        self.score = 0

        # Task 1: 3 lives
        self.lives = 3

        self.game_over = False
        self.won = False

        # Prevent duplicate score saving
        self.score_saved = False

        # Task 4: day/night state
        self.day_night_timer = 0
        self.is_night = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

        return True

    # ==========================================
    # TASK 2: MOVE LOGS
    # ==========================================
    def update_logs(self):
        for log in self.logs:
            log.x += LOG_SPEED

            if log.left > WIDTH:
                log.right = 0

    # ==========================================
    # TASK 2: CHECK LOG
    # ==========================================
    def get_player_log(self):
        for log in self.logs:
            if self.player.rect.colliderect(log):
                return log

        return None

    # ==========================================
    # TASK 4: DAY/NIGHT CYCLE
    # ==========================================
    def update_day_night(self):
        self.day_night_timer += 1

        if self.day_night_timer >= DAY_NIGHT_INTERVAL:
            self.day_night_timer = 0
            self.is_night = not self.is_night

    # ==========================================
    # TASK 4: SAVE SCORE AFTER GAME END
    # ==========================================
    def finish_game(self):
        if not self.score_saved:
            self.add_high_score()
            self.score_saved = True

    def update(self):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()

        # Normal player movement
        self.player.move(keys, 0, WIDTH)

        # Task 4
        self.update_day_night()

        # Move logs
        self.update_logs()

        # Check if player is on a log
        player_log = self.get_player_log()

        # Carry player with log
        if player_log is not None:
            self.player.rect.x += LOG_SPEED

            if self.player.rect.left < 0:
                self.player.rect.left = 0

            if self.player.rect.right > WIDTH:
                self.player.rect.right = WIDTH

        # ==========================================
        # TASK 2: FALL INTO WATER
        # ==========================================
        player_center_y = self.player.rect.centery

        if (
            LOG_LANE_Y <= player_center_y <= LOG_LANE_Y + LOG_HEIGHT
            and player_log is None
        ):
            self.lives -= 1

            self.player = Player(
                WIDTH // 2,
                HEIGHT - 80
            )

            if self.lives <= 0:
                self.game_over = True
                self.finish_game()

            return

        # ==========================================
        # TRAFFIC SYSTEM
        # ==========================================
        self.timer += 1

        if self.timer >= self.spawn_interval:
            lane = random.randint(0, LANES - 1)

            self.cars.append(
                make_car(
                    lane,
                    HEIGHT,
                    self.speed
                )
            )

            self.timer = 0

            self.spawn_interval = max(
                22,
                self.spawn_interval - 0.2
            )

        # Update cars
        for c in self.cars:
            c.update()

            # Car collision
            if c.rect.colliderect(self.player.rect):
                self.lives -= 1

                self.player = Player(
                    WIDTH // 2,
                    HEIGHT - 80
                )

                if c in self.cars:
                    self.cars.remove(c)

                if self.lives <= 0:
                    self.game_over = True
                    self.finish_game()

                break

        self.cars = [
            c for c in self.cars
            if not c.off_screen(HEIGHT)
        ]

        # Increase score
        self.score += 1

        if self.score % 300 == 0:
            self.speed = min(
                10,
                self.speed + 0.5
            )

        # Player reached top
        if self.player.rect.top <= 10:
            self.won = True
            self.finish_game()

    def draw(self):
        # ==========================================
        # TASK 4: DAY/NIGHT BACKGROUND
        # ==========================================
        background = NIGHT_BG if self.is_night else DAY_BG
        self.screen.fill(background)

        # ==========================================
        # ROAD MARKINGS
        # ==========================================
        for i in range(LANES + 1):
            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                (i * LANE_W, 0),
                (i * LANE_W, HEIGHT),
                2
            )

        for y in range(0, HEIGHT, 60):
            for i in range(LANES):
                pygame.draw.rect(
                    self.screen,
                    (200, 200, 100),
                    pygame.Rect(
                        i * LANE_W + LANE_W // 2 - 3,
                        y,
                        6,
                        30
                    )
                )

        # ==========================================
        # SIDEWALKS
        # ==========================================
        pygame.draw.rect(
            self.screen,
            (150, 130, 110),
            pygame.Rect(
                0,
                HEIGHT - 50,
                WIDTH,
                50
            )
        )

        pygame.draw.rect(
            self.screen,
            (150, 130, 110),
            pygame.Rect(
                0,
                0,
                WIDTH,
                30
            )
        )

        # ==========================================
        # TASK 2: WATER
        # ==========================================
        pygame.draw.rect(
            self.screen,
            (40, 120, 180),
            pygame.Rect(
                0,
                LOG_LANE_Y,
                WIDTH,
                LOG_HEIGHT
            )
        )

        # Draw logs
        for log in self.logs:
            pygame.draw.rect(
                self.screen,
                (130, 75, 30),
                log,
                border_radius=8
            )

            pygame.draw.line(
                self.screen,
                (80, 45, 20),
                (log.x + 20, log.y + 5),
                (log.x + 20, log.bottom - 5),
                3
            )

            pygame.draw.line(
                self.screen,
                (80, 45, 20),
                (log.right - 20, log.y + 5),
                (log.right - 20, log.bottom - 5),
                3
            )

        # ==========================================
        # CARS + TASK 4 HEADLIGHTS
        # ==========================================
        for c in self.cars:
            c.draw(self.screen)

            if self.is_night:
                # Headlight glow extending ahead of the car
                beam_y = c.rect.centery

                pygame.draw.polygon(
                    self.screen,
                    (180, 180, 110),
                    [
                        (c.rect.left, beam_y - 7),
                        (max(0, c.rect.left - 120), beam_y - 35),
                        (max(0, c.rect.left - 120), beam_y + 35)
                    ]
                )

                # Headlights
                pygame.draw.circle(
                    self.screen,
                    (255, 245, 180),
                    (c.rect.left + 5, c.rect.top + 12),
                    5
                )

                pygame.draw.circle(
                    self.screen,
                    (255, 245, 180),
                    (c.rect.left + 5, c.rect.bottom - 12),
                    5
                )

        # ==========================================
        # PLAYER
        # ==========================================
        self.player.draw(self.screen)

        # ==========================================
        # HUD
        # ==========================================
        hud = pygame.Rect(
            0,
            0,
            WIDTH,
            30
        )

        pygame.draw.rect(
            self.screen,
            (20, 20, 20),
            hud
        )

        mode = "NIGHT" if self.is_night else "DAY"

        s = self.font.render(
            f"Score: {self.score // 10}  "
            f"Lives: {self.lives}  "
            f"{mode}  "
            f"GOAL: reach the top!  R=Restart",
            True,
            (220, 220, 220)
        )

        self.screen.blit(
            s,
            (6, 4)
        )

        # Task 2 message
        log_text = self.font.render(
            "HOP ON THE LOG!",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            log_text,
            (
                WIDTH // 2 - log_text.get_width() // 2,
                LOG_LANE_Y + LOG_HEIGHT + 5
            )
        )

        # ==========================================
        # GAME OVER
        # ==========================================
        if self.game_over:
            self._msg(
                "GAME OVER",
                (220, 60, 60)
            )

        # ==========================================
        # WIN
        # ==========================================
        if self.won:
            self._msg(
                "YOU MADE IT!",
                (80, 220, 80)
            )

        pygame.display.flip()

    # ==========================================
    # TASK 3: HIGH SCORE DISPLAY
    # ==========================================
    def draw_high_scores(self):
        title = self.big_font.render(
            "HIGH SCORES",
            True,
            (255, 215, 0)
        )

        self.screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                120
            )
        )

        if not self.high_scores:
            text = self.small_font.render(
                "No scores yet",
                True,
                (220, 220, 220)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    190
                )
            )

        else:
            for i, score in enumerate(self.high_scores):
                text = self.small_font.render(
                    f"{i + 1}. {score}",
                    True,
                    (255, 255, 255)
                )

                self.screen.blit(
                    text,
                    (
                        WIDTH // 2 - 50,
                        180 + i * 30
                    )
                )

    def _msg(self, text, color):
        ov = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        ov.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            ov,
            (0, 0)
        )

        m = self.big_font.render(
            text,
            True,
            color
        )

        sub = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            m,
            (
                WIDTH // 2 - m.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            sub,
            (
                WIDTH // 2 - sub.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

        # Task 3: show high scores
        self.draw_high_scores()

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
