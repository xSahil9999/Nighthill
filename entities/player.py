import pygame

from animations.attack import load_attack_animations
from animations.death import load_death_animations
from animations.jump import load_jump_animations
from animations.move import load_move_animations
from core import settings


class Player:
    def __init__(self, x: int, y: int, floor_y: int):
        self.speed = settings.PLAYER_SPEED
        self.facing_right = True
        self.floor_y = floor_y

        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0

        self.attacking = False
        self.combo_step = 0
        self.combo_queued = False
        self.attack_damage_done = False
        self.dead = False
        self.death_finished = False
        self.max_health = settings.PLAYER_MAX_HEALTH
        self.health = settings.PLAYER_MAX_HEALTH
        self.hit_cooldown_timer = 0

        self.velocity_y = 0.0
        self.on_ground = False

        self.animations: dict[str, list[pygame.Surface]] = {}
        self.animations.update(load_move_animations(settings.SPRITE_SIZE))
        self.animations.update(load_attack_animations(settings.SPRITE_SIZE))
        self.animations.update(load_jump_animations(settings.SPRITE_SIZE))
        self.animations.update(load_death_animations(settings.SPRITE_SIZE))

        self.animation_speeds = {
            "idle": settings.IDLE_SPEED,
            "run": settings.RUN_SPEED,
            "jump": settings.JUMP_SPEED,
            "attack1": settings.ATTACK_SPEED,
            "attack2": settings.ATTACK_SPEED,
            "attack3": settings.ATTACK_SPEED,
            "death": settings.DEATH_SPEED,
        }

        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        if self.rect.bottom > self.floor_y:
            self.rect.bottom = self.floor_y
        self.on_ground = self.rect.bottom >= self.floor_y

    def _set_animation(self, name: str):
        if self.current_animation != name:
            self.current_animation = name
            self.frame_index = 0
            self.animation_timer = 0

            if name.startswith("attack"):
                self.attack_damage_done = False

    def _end_attack(self):
        self.attacking = False
        self.combo_step = 0
        self.combo_queued = False
        self.attack_damage_done = False

        if self.on_ground:
            self._set_animation("idle")
        else:
            self._set_animation("jump")

    def start_attack(self):
        if self.dead:
            return

        if not self.attacking:
            self.attacking = True
            self.combo_step = 1
            self.combo_queued = False
            self._set_animation("attack1")
            return

        if self.combo_step in (1, 2):
            self.combo_queued = True

    def start_jump(self):
        if self.dead or not self.on_ground:
            return

        self.velocity_y = -settings.JUMP_STRENGTH
        self.on_ground = False

        if not self.attacking:
            self._set_animation("jump")

    def handle_input(self):
        if self.dead:
            return

        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            moving = True

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            moving = True

        if keys[pygame.K_SPACE] or keys[pygame.K_w]:
            self.start_jump()

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = max(0.0, self.velocity_y)

        if not self.attacking:
            if not self.on_ground:
                self._set_animation("jump")
            elif moving:
                self._set_animation("run")
            else:
                self._set_animation("idle")

    def die(self):
        if self.dead or "death" not in self.animations:
            return

        self.dead = True
        self.death_finished = False
        self.attacking = False
        self.combo_step = 0
        self.combo_queued = False
        self.attack_damage_done = False
        self.velocity_y = 0.0
        self._set_animation("death")

    def take_damage(self, amount: int = 1):
        if self.dead or self.hit_cooldown_timer > 0:
            return

        self.health = max(0, self.health - amount)
        self.hit_cooldown_timer = settings.PLAYER_HIT_COOLDOWN

        if self.health <= 0:
            self.die()

    def apply_gravity(self):
        self.velocity_y += settings.GRAVITY
        self.rect.y += int(self.velocity_y)

        if self.rect.bottom >= self.floor_y:
            self.rect.bottom = self.floor_y
            self.velocity_y = 0.0
            self.on_ground = True
        else:
            self.on_ground = False

    def get_current_frames(self) -> list[pygame.Surface]:
        return self.animations.get(self.current_animation, self.animations["idle"])

    def animate(self):
        frames = self.get_current_frames()
        speed = self.animation_speeds.get(self.current_animation, settings.IDLE_SPEED)

        self.animation_timer += 1
        if self.animation_timer < speed:
            self.image = frames[self.frame_index]
            return

        self.animation_timer = 0
        self.frame_index += 1

        if self.current_animation == "death":
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
                self.death_finished = True
        elif self.current_animation == "attack1":
            if self.frame_index >= len(frames):
                if self.combo_queued:
                    self.combo_step = 2
                    self.combo_queued = False
                    self._set_animation("attack2")
                else:
                    self._end_attack()
        elif self.current_animation == "attack2":
            if self.frame_index >= len(frames):
                if self.combo_queued:
                    self.combo_step = 3
                    self.combo_queued = False
                    self._set_animation("attack3")
                else:
                    self._end_attack()
        elif self.current_animation == "attack3":
            if self.frame_index >= len(frames):
                self._end_attack()
        elif self.frame_index >= len(frames):
            self.frame_index = 0

        frames = self.get_current_frames()
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[self.frame_index]

    def update(self):
        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= 1

        self.handle_input()
        self.apply_gravity()

        if not self.dead and not self.attacking and self.on_ground and self.current_animation == "jump":
            self._set_animation("idle")

        self.animate()

    def draw(self, surface: pygame.Surface):
        if self.facing_right:
            surface.blit(self.image, self.rect)
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_image, self.rect)

    def can_deal_damage(self) -> bool:
        if self.dead or not self.attacking:
            return False
        if not self.current_animation.startswith("attack"):
            return False
        if self.attack_damage_done:
            return False
        return self.frame_index >= 1

    def mark_attack_damage_done(self):
        self.attack_damage_done = True

    def get_attack_hitbox(self) -> pygame.Rect | None:
        if not self.current_animation.startswith("attack"):
            return None

        hitbox_width = 42
        hitbox_height = self.rect.height - 16
        hitbox_y = self.rect.y + 8

        if self.facing_right:
            hitbox_x = self.rect.right - 8
        else:
            hitbox_x = self.rect.left - hitbox_width + 8

        return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def draw_health(self, surface: pygame.Surface):
        bar_width = 42
        bar_height = 8
        gap = 10
        start_x = 18
        start_y = 44

        for idx in range(self.max_health):
            x = start_x + idx * (bar_width + gap)
            rect = pygame.Rect(x, start_y, bar_width, bar_height)
            if idx < self.health:
                color = (220, 62, 62)
            else:
                color = (75, 35, 35)
            pygame.draw.rect(surface, color, rect, border_radius=3)
            pygame.draw.rect(surface, (15, 15, 15), rect, width=1, border_radius=3)
