import math
import re

import pygame

from core import settings


class NPC:
    def __init__(
        self,
        x: int,
        y: int,
        name: str = "Goddess",
        dialogue: list[tuple[str, str]] | None = None,
        sprite_file: str | None = None,
        sprite_size: tuple[int, int] | None = None,
        floating: bool = False,
        float_amplitude: int | None = None,
        float_speed: float | None = None,
    ):
        # - Grunddaten und Sprite-Laden.
        self.name = name
        self.sprite_file = sprite_file
        self.sprite_size = sprite_size or settings.NPC_SPRITE_SIZE
        self.frames = self._load_idle_frames()
        self.frame_index = 0
        self.animation_timer = 0

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # - Optionales Schweben (sinusfoermig).
        self.base_y = y
        self.floating = floating
        self.float_amplitude = (
            float_amplitude
            if isinstance(float_amplitude, int) and float_amplitude >= 0
            else settings.NPC_FLOAT_AMPLITUDE
        )
        self.float_speed = (
            float_speed
            if isinstance(float_speed, (float, int)) and float_speed > 0
            else settings.NPC_FLOAT_SPEED
        )
        self.float_phase = x * 0.01

        # - Dialog-Status.
        self.dialogue = dialogue or [
            ("Ich habe einen Auftrag fuer dich.", "Gehe weiter nach Night Hill."),
        ]
        self.dialogue_index = 0
        self.talking = False
        self.quest_started = False
        self.dialogue_finished = False

        self.prompt_font = pygame.font.SysFont(None, 28)
        self.name_font = pygame.font.SysFont(None, 30)
        self.dialog_font = pygame.font.SysFont(None, 26)

    def _load_idle_frames(self) -> list[pygame.Surface]:
        # - Wenn direktes NPC-Bild gesetzt ist, nur dieses laden.
        if self.sprite_file:
            custom_path = settings.ASSETS_DIR / self.sprite_file
            if custom_path.exists():
                frame = pygame.image.load(str(custom_path)).convert_alpha()
                frame = pygame.transform.scale(frame, self.sprite_size)
                return [frame]

        # - Sonst alle Idle-Frames aus assets/NPC/idl.
        idle_dir = settings.ASSETS_DIR / "NPC" / "idl"
        frame_paths = sorted(idle_dir.glob("*.png"), key=self._frame_sort_key)

        if not frame_paths:
            fallback = pygame.Surface(self.sprite_size, pygame.SRCALPHA)
            fallback.fill((220, 200, 120))
            return [fallback]

        frames: list[pygame.Surface] = []
        for path in frame_paths:
            frame = pygame.image.load(str(path)).convert_alpha()
            frame = pygame.transform.scale(frame, self.sprite_size)
            frames.append(frame)
        return frames

    @staticmethod
    def _frame_sort_key(path) -> int:
        match = re.search(r"(\d+)$", path.stem)
        if match:
            return int(match.group(1))
        return 9999

    def update(self):
        # - Y-Position fuer Schweben aktualisieren.
        if self.floating:
            self.float_phase += self.float_speed
            self.rect.y = self.base_y + int(math.sin(self.float_phase) * self.float_amplitude)
        else:
            self.rect.y = self.base_y

        # - Idle-Animation weiterschalten.
        self.animation_timer += 1
        if self.animation_timer < settings.NPC_IDLE_SPEED:
            return

        self.animation_timer = 0
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[self.frame_index]

    def is_player_near(self, player_rect: pygame.Rect) -> bool:
        dx = abs(player_rect.centerx - self.rect.centerx)
        dy = abs(player_rect.centery - self.rect.centery)
        return dx <= settings.NPC_INTERACT_DISTANCE_X and dy <= settings.NPC_INTERACT_DISTANCE_Y

    def interact(self) -> str:
        if self.dialogue_finished:
            return "finished"

        self.quest_started = True

        if not self.talking:
            self.talking = True
            self.dialogue_index = 0
            return "opened"

        if self.dialogue_index < len(self.dialogue) - 1:
            self.dialogue_index += 1
            return "advanced"

        self.talking = False
        self.dialogue_finished = True
        return "finished"

    def stop_talking(self):
        self.talking = False

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def draw_overlay(self, surface: pygame.Surface, player_rect: pygame.Rect):
        player_near = self.is_player_near(player_rect)
        if player_near and not self.dialogue_finished:
            prompt = self.prompt_font.render("E druecken um zu reden", True, (255, 248, 216))
            prompt_rect = prompt.get_rect(midbottom=(self.rect.centerx, self.rect.top - 8))
            surface.blit(prompt, prompt_rect)

        if self.talking:
            self._draw_dialog(surface)

    def _draw_dialog(self, surface: pygame.Surface):
        box_rect = pygame.Rect(30, settings.HEIGHT - 180, settings.WIDTH - 60, 140)
        pygame.draw.rect(surface, (14, 16, 24), box_rect, border_radius=10)
        pygame.draw.rect(surface, (228, 210, 150), box_rect, width=2, border_radius=10)

        name_surface = self.name_font.render(self.name, True, (238, 224, 177))
        surface.blit(name_surface, (box_rect.x + 14, box_rect.y + 10))

        line1, line2 = self.dialogue[self.dialogue_index]
        text1 = self.dialog_font.render(line1, True, (240, 240, 240))
        text2 = self.dialog_font.render(line2, True, (240, 240, 240))
        surface.blit(text1, (box_rect.x + 14, box_rect.y + 56))
        surface.blit(text2, (box_rect.x + 14, box_rect.y + 86))

        continue_hint = self.dialog_font.render("E: weiter", True, (220, 220, 220))
        hint_rect = continue_hint.get_rect(bottomright=(box_rect.right - 14, box_rect.bottom - 12))
        surface.blit(continue_hint, hint_rect)
