import re
from pathlib import Path

import pygame

from core import settings


class Enemy:
    def __init__(self, x: int, y: int, width: int | None = None, height: int | None = None):
        enemy_width = width or settings.ENEMY_SIZE[0]
        enemy_height = height or settings.ENEMY_SIZE[1]

        self.rect = pygame.Rect(x, y, enemy_width, enemy_height)
        self.speed = settings.ENEMY_SPEED
        self.facing_right = False

        self.left_bound = max(0, x - settings.ENEMY_PATROL_RANGE)
        self.right_bound = min(settings.WIDTH - enemy_width, x + settings.ENEMY_PATROL_RANGE)
        self.patrol_direction = 1

        self.max_health = settings.ENEMY_MAX_HEALTH
        self.health = settings.ENEMY_MAX_HEALTH
        self.dead = False
        self.hit_cooldown_timer = 0

        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_damage_applied = False
        self.pending_damage = False

        self.animations = self._load_animations((enemy_width, enemy_height))
        self.animation_speeds = {
            "idle": settings.ENEMY_IDLE_SPEED,
            "walk": settings.ENEMY_WALK_SPEED,
            "attack": settings.ENEMY_ATTACK_SPEED,
            "dead": settings.ENEMY_DEATH_SPEED,
        }

        self.image = self.animations["idle"][0]

    def _find_enemy_assets_dir(self) -> Path:
        root_candidate = settings.ENEMY_ASSETS_DIR
        if root_candidate.exists():
            return root_candidate

        assets_candidate = settings.ASSETS_DIR / "Enemy"
        if assets_candidate.exists():
            return assets_candidate

        return root_candidate

    def _load_animations(self, size: tuple[int, int]) -> dict[str, list[pygame.Surface]]:
        base = self._find_enemy_assets_dir()
        idle = self._load_folder_frames(base / "idl", size)
        walk = self._load_folder_frames(base / "Walk", size)
        attack = self._load_folder_frames(base / "Attack", size)
        dead = self._load_folder_frames(base / "Dead", size)

        if not idle:
            idle = [self._fallback_surface(size, (165, 165, 175))]
        if not walk:
            walk = idle
        if not attack:
            attack = idle
        if not dead:
            dead = idle

        return {"idle": idle, "walk": walk, "attack": attack, "dead": dead}

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

    def take_damage(self, amount: int = 1) -> bool:
        if self.dead or self.hit_cooldown_timer > 0:
            return False

        self.health = max(0, self.health - amount)
        self.hit_cooldown_timer = settings.ENEMY_HIT_COOLDOWN

        if self.health <= 0:
            self.dead = True
            self.pending_damage = False
            self._set_animation("dead")
        else:
            self._set_animation("idle")

        return True

    def update(self, player_rect: pygame.Rect):
        self.pending_damage = False

        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= 1

        if self.dead:
            self._animate(player_rect)
            return

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        player_is_near = self._is_player_near(
            player_rect,
            settings.ENEMY_AGGRO_DISTANCE_X,
            settings.ENEMY_AGGRO_DISTANCE_Y,
        )
        player_in_attack_range = self._is_player_near(
            player_rect,
            settings.ENEMY_ATTACK_DISTANCE_X,
            settings.ENEMY_ATTACK_DISTANCE_Y,
        )

        if player_is_near:
            self.facing_right = player_rect.centerx >= self.rect.centerx

            if (
                player_in_attack_range
                and self.attack_cooldown_timer == 0
                and self.current_animation != "attack"
            ):
                self._set_animation("attack")
            elif self.current_animation != "attack":
                self._set_animation("walk")
                if not player_in_attack_range:
                    if player_rect.centerx > self.rect.centerx:
                        self.rect.x += self.speed
                    elif player_rect.centerx < self.rect.centerx:
                        self.rect.x -= self.speed
        elif self.current_animation != "attack":
            self._set_animation("walk")
            self.rect.x += self.speed * self.patrol_direction
            if self.rect.x <= self.left_bound or self.rect.x >= self.right_bound:
                self.patrol_direction *= -1

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.WIDTH, self.rect.right)

        self._animate(player_rect)

    def _animate(self, player_rect: pygame.Rect):
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
                self.frame_index >= settings.ENEMY_DAMAGE_FRAME
                and not self.attack_damage_applied
                and self._is_player_near(
                    player_rect,
                    settings.ENEMY_ATTACK_DISTANCE_X,
                    settings.ENEMY_ATTACK_DISTANCE_Y,
                )
            ):
                self.pending_damage = True
                self.attack_damage_applied = True

            if self.frame_index >= len(frames):
                self.frame_index = 0
                self.attack_cooldown_timer = settings.ENEMY_ATTACK_COOLDOWN
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

        return self._is_player_near(
            player_rect,
            settings.ENEMY_ATTACK_DISTANCE_X,
            settings.ENEMY_ATTACK_DISTANCE_Y,
        )

    def draw(self, surface: pygame.Surface):
        if self.facing_right:
            surface.blit(self.image, self.rect)
        else:
            flipped = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped, self.rect)
