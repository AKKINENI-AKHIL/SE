import math
import random
import struct
import pygame

from .fruit import Fruit


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_OVERLAY = (10, 12, 25)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [
    (220, 60, 60),
    (230, 140, 40),
    (230, 200, 40),
    (90, 180, 90),
    (80, 160, 220),
]

DIFFICULTIES = {
    "easy": {
        "label": "Easy",
        "spawn_interval": 70,
        "bomb_chance": 0.08,
        "speed_scale": 0.90,
    },
    "medium": {
        "label": "Medium",
        "spawn_interval": 55,
        "bomb_chance": 0.15,
        "speed_scale": 1.00,
    },
    "hard": {
        "label": "Hard",
        "spawn_interval": 42,
        "bomb_chance": 0.24,
        "speed_scale": 1.10,
    },
}


def _make_tone(frequency, duration, volume=0.25, sample_rate=22050):
    """Create a short PCM sound without requiring external audio assets."""
    count = max(1, int(sample_rate * duration))
    amplitude = int(32767 * volume)
    fade_samples = max(1, int(count * 0.08))
    data = bytearray()

    for i in range(count):
        t = i / sample_rate
        envelope = 1.0
        if i < fade_samples:
            envelope = i / fade_samples
        elif i >= count - fade_samples:
            envelope = (count - i) / fade_samples

        sample = int(
            amplitude
            * envelope
            * math.sin(2 * math.pi * frequency * t)
        )
        data.extend(struct.pack("<h", sample))

    return pygame.mixer.Sound(buffer=bytes(data))


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fruits = []
        self.trail = []
        self.previous_mouse_pos = None

        self.spawn_interval = DIFFICULTIES["medium"]["spawn_interval"]
        self._spawn_timer = 0
        self.bomb_chance = DIFFICULTIES["medium"]["bomb_chance"]
        self.speed_scale = DIFFICULTIES["medium"]["speed_scale"]

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.large_font = pygame.font.SysFont("Arial", 54, bold=True)
        self.medium_font = pygame.font.SysFont("Arial", 34, bold=True)
        self.game_over = False
        self.exit_requested = False
        self.difficulty = "medium"

        self.sound_enabled = False
        self.slice_sound = None
        self.bomb_sound = None
        self.game_over_sound = None
        self._setup_sounds()

    def _setup_sounds(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.slice_sound = _make_tone(880, 0.07, 0.20)
            self.bomb_sound = _make_tone(110, 0.22, 0.30)
            self.game_over_sound = _make_tone(220, 0.45, 0.28)
            self.sound_enabled = True
        except pygame.error:
            # The game remains playable on systems without an audio device.
            self.sound_enabled = False

    def _play(self, sound):
        if self.sound_enabled and sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass

    def set_difficulty(self, difficulty):
        config = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.spawn_interval = config["spawn_interval"]
        self.bomb_chance = config["bomb_chance"]
        self.speed_scale = config["speed_scale"]

    def reset(self, difficulty=None):
        if difficulty is not None:
            self.set_difficulty(difficulty)

        self.fruits.clear()
        self.trail.clear()
        self.previous_mouse_pos = None
        self._spawn_timer = 0
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.exit_requested = False

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(
            x,
            self.height + 30,
            vx,
            vy,
            gravity,
            radius=28,
            kind=kind,
        )
        fruit.color = (
            BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        )
        self.fruits.append(fruit)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)

        elif event.type == pygame.KEYDOWN and self.game_over:
            if event.key == pygame.K_1:
                self.reset("easy")
            elif event.key == pygame.K_2:
                self.reset("medium")
            elif event.key == pygame.K_3:
                self.reset("hard")
            elif event.key in (pygame.K_e, pygame.K_ESCAPE, pygame.K_q):
                self.exit_requested = True

    def _handle_motion(self, pos):
        # Do not process blade collisions after game over.
        if self.game_over:
            self.previous_mouse_pos = pos
            return

        start = self.previous_mouse_pos
        end = pos

        for fruit in self.fruits:
            if (
                not fruit.sliced
                and fruit.segment_intersects(start, end, padding=4)
            ):
                self._slice(fruit)

        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

        self.previous_mouse_pos = pos

    def _slice(self, fruit):
        fruit.sliced = True

        if fruit.kind == "bomb":
            self.game_over = True
            self._play(self.bomb_sound)
            self._play(self.game_over_sound)
        else:
            self.score += 1
            self._play(self.slice_sound)

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []

        for fruit in self.fruits:
            fruit.update()

            if fruit.sliced:
                continue

            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue

            still_alive.append(fruit)

        self.fruits = still_alive

        if self.lives <= 0:
            self.game_over = True
            self._play(self.game_over_sound)

    def _draw_centered(self, screen, text, font, y, color=WHITE):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.width // 2, y))
        screen.blit(surface, rect)

    def render(self, screen):
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)
            pygame.draw.circle(
                screen,
                color,
                (int(fruit.x), int(fruit.y)),
                fruit.radius,
            )

            # Simple bomb marker.
            if fruit.kind == "bomb":
                pygame.draw.circle(
                    screen,
                    (190, 190, 190),
                    (int(fruit.x), int(fruit.y)),
                    fruit.radius - 8,
                    2,
                )

        if len(self.trail) >= 2 and not self.game_over:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        lives_rect = lives_text.get_rect(topright=(self.width - 10, 10))
        screen.blit(lives_text, lives_rect)

        difficulty_text = self.font.render(
            f"Difficulty: {DIFFICULTIES[self.difficulty]['label']}",
            True,
            WHITE,
        )
        screen.blit(difficulty_text, (10, 45))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((DARK_OVERLAY[0], DARK_OVERLAY[1], DARK_OVERLAY[2], 225))
        screen.blit(overlay, (0, 0))

        self._draw_centered(
            screen,
            "GAME OVER",
            self.large_font,
            self.height // 2 - 115,
        )
        self._draw_centered(
            screen,
            f"Final Score: {self.score}",
            self.medium_font,
            self.height // 2 - 55,
        )
        self._draw_centered(
            screen,
            "Play Again",
            self.font,
            self.height // 2 + 5,
        )
        self._draw_centered(
            screen,
            "1 - Easy     2 - Medium     3 - Hard",
            self.font,
            self.height // 2 + 45,
        )
        self._draw_centered(
            screen,
            "Press E to Exit",
            self.font,
            self.height // 2 + 90,
        )
