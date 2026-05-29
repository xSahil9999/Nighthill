import math
import re
from pathlib import Path

import pygame

from core import settings


class BossQueen:
    def __init__(self, x: int, y: int, width: int | None = None, height: int | None = None):
        # - Boss-Groesse aus Parameter oder Settings.
        boss_width = width or settings.BOSS_SIZE[0]
        boss_height = height or settings.BOSS_SIZE[1]

        self.rect = pygame.Rect(x, y, boss_width, boss_height)
        self.facing_right = False

        # - Boss-Lebenssystem.
        self.max_health = settings.BOSS_MAX_HEALTH
        self.health = settings.BOSS_MAX_HEALTH
        self.dead = False
        self.remove_on_death = False
        self.is_boss = True

        # - Kampfstatus.
        self.hit_cooldown_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_damage_applied = False
        self.pending_damage = False
        self.damage_window_timer = 0

        # - Animationsstatus.
        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0

        # - Schwebe-Basis.
        self.base_center_y = self.rect.centery
        self.float_phase = 0.0

        self.animations = self._load_animations((boss_width, boss_height))
        self.animation_speeds = {
            "idle": settings.BOSS_IDLE_SPEED,
            "attack": settings.BOSS_ATTACK_SPEED,
            "dead": settings.BOSS_DEATH_SPEED,
        }
        self.image = self.animations["idle"][0]

    def _find_boss_assets_dir(self) -> Path:
        # - Sucht einen Unterordner mit Idl + Attack (robust gegen Namen).
        roots = [settings.ENEMY_ASSETS_DIR, settings.ASSETS_DIR / "Enemy"]
        for root in roots:
            if not root.exists():
                continue
            for child in root.iterdir():
                if not child.is_dir():
                    continue

                has_idle = (child / "Idl").exists() or (child / "idl").exists()
                has_attack = (child / "Attack").exists()
                if not (has_idle and has_attack):
                    continue

                if child.name.lower() in {"attack", "dead", "walk", "idl", "idle"}:
                    continue

                return child

        return settings.ENEMY_ASSETS_DIR

    def _load_animations(self, size: tuple[int, int]) -> dict[str, list[pygame.Surface]]:
        # - Boss nutzt Idl/Attack; Dead bleibt auf letztem Attack-Frame.
        base = self._find_boss_assets_dir()
        idle = self._load_folder_frames(base / "Idl", size)
        attack = self._load_folder_frames(base / "Attack", size)

        if not idle:
            idle = [self._fallback_surface(size, (168, 132, 196))]
        if not attack:
            attack = idle

        dead = [attack[-1]]
        return {"idle": idle, "attack": attack, "dead": dead}

    def _load_folder_frames(self, folder: Path, size: tuple[int, int]) -> list[pygame.Surface]:
        if not folder.exists():
            return []

        paths = sorted(folder.glob("*.png"), key=self._frame_sort_key)
        frames: list[pygame.Surface] = []
        for path in paths:
            frame = pygame.image.load(str(path)).convert_alpha()
            frame = pygame.transform.scale(frame, size)
            frames.append(frame)
        return frames

    @staticmethod
    def _frame_sort_key(path: Path) -> int:
        numbers = re.findall(r"\d+", path.stem)
        if numbers:
            return int(numbers[0])
        return 9999

    @staticmethod
    def _fallback_surface(size: tuple[int, int], color: tuple[int, int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        return surface

    def _set_animation(self, name: str):
        if self.current_animation != name:
            self.current_animation = name
            self.frame_index = 0
            self.animation_timer = 0
            if name == "attack":
                self.attack_damage_applied = False

    def _is_player_near(self, player_rect: pygame.Rect, dist_x: int, dist_y: int) -> bool:
        dx = abs(player_rect.centerx - self.rect.centerx)
        dy = abs(player_rect.centery - self.rect.centery)
        return dx <= dist_x and dy <= dist_y

    def _is_player_in_attack_radius(self, player_rect: pygame.Rect) -> bool:
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        return math.hypot(dx, dy) <= settings.BOSS_ATTACK_RADIUS

    def _float_motion(self):
        # - Sinus-Schweben.
        self.float_phase += settings.BOSS_FLOAT_SPEED
        vertical_offset = math.sin(self.float_phase) * settings.BOSS_FLOAT_AMPLITUDE
        self.rect.centery = int(self.base_center_y + vertical_offset)

    def _hover_towards_player(self, player_rect: pygame.Rect):
        # - Leichte horizontale Bewegung zum Spieler.
        if player_rect.centerx > self.rect.centerx + 24:
            self.rect.x += settings.BOSS_DRIFT_SPEED
        elif player_rect.centerx < self.rect.centerx - 24:
            self.rect.x -= settings.BOSS_DRIFT_SPEED

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.WIDTH, self.rect.right)

    def take_damage(self, amount: int = 1) -> bool:
        # - Nimmt Schaden nur wenn nicht tot und nicht im Hit-Cooldown.
        if self.dead or self.hit_cooldown_timer > 0:
            return False

        self.health = max(0, self.health - amount)
        self.hit_cooldown_timer = settings.BOSS_HIT_COOLDOWN

        if self.health <= 0:
            self.dead = True
            self.pending_damage = False
            self.damage_window_timer = 0
            self._set_animation("dead")
        else:
            self._set_animation("idle")

        return True

    def update(self, player_rect: pygame.Rect):
        # - Damage-Fenster fuer Radius-Angriff.
        if self.damage_window_timer > 0:
            self.damage_window_timer -= 1
        self.pending_damage = self.damage_window_timer > 0

        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= 1
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        self.facing_right = player_rect.centerx >= self.rect.centerx

        if self.dead:
            self._float_motion()
            self._animate(player_rect)
            return

        # - Aggro/Attack nur wenn Spieler nah genug ist.
        player_is_near = self._is_player_near(
            player_rect,
            settings.BOSS_AGGRO_DISTANCE_X,
            settings.BOSS_AGGRO_DISTANCE_Y,
        )
        player_in_attack_range = self._is_player_near(
            player_rect,
            settings.BOSS_ATTACK_DISTANCE_X,
            settings.BOSS_ATTACK_DISTANCE_Y,
        )

        if (
            player_is_near
            and player_in_attack_range
            and self.attack_cooldown_timer == 0
            and self.current_animation != "attack"
        ):
            self._set_animation("attack")
        elif self.current_animation != "attack":
            self._set_animation("idle")
            if player_is_near:
                self._hover_towards_player(player_rect)

        self._float_motion()
        self._animate(player_rect)

    def _animate(self, player_rect: pygame.Rect):
        # - Framewechsel nach eingestellter Geschwindigkeit.
        frames = self.animations[self.current_animation]
        speed = self.animation_speeds[self.current_animation]

        self.animation_timer += 1
        if self.animation_timer < speed:
            self.image = frames[self.frame_index]
            return

        self.animation_timer = 0
        self.frame_index += 1

        if self.current_animation == "dead":
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1

        elif self.current_animation == "attack":
            if (
                self.frame_index >= settings.BOSS_DAMAGE_FRAME
                and not self.attack_damage_applied
            ):
                # - Radius-Schaden wird fuer ein kurzes Fenster aktiv.
                self.damage_window_timer = settings.BOSS_DAMAGE_WINDOW_FRAMES
                self.pending_damage = True
                self.attack_damage_applied = True

            if self.frame_index >= len(frames):
                self.frame_index = 0
                self.attack_cooldown_timer = settings.BOSS_ATTACK_COOLDOWN
                self._set_animation("idle")

        elif self.frame_index >= len(frames):
            self.frame_index = 0

        frames = self.animations[self.current_animation]
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[self.frame_index]

    def can_damage_player(self, player_rect: pygame.Rect) -> bool:
        if self.dead or not self.pending_damage:
            return False

        return self._is_player_in_attack_radius(player_rect)

    def draw(self, surface: pygame.Surface):
        if self.facing_right:
            surface.blit(self.image, self.rect)
        else:
            flipped = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped, self.rect)
