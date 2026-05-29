import pygame

from core import settings


class GameMap:
    def __init__(self):
        self.background = None
        self.floor_y_value = settings.HEIGHT - settings.GROUND_HEIGHT
        self.draw_ground_overlay = True
        self.ground_rect = pygame.Rect(
            0,
            self.floor_y_value,
            settings.WIDTH,
            settings.GROUND_HEIGHT,
        )
        self.ground_color = (42, 72, 54)
        self.hill_color = (26, 42, 35)

    @property
    def floor_y(self) -> int:
        return self.floor_y_value

    def set_level_visuals(
        self,
        map_file: str | None,
        floor_y: int | None = None,
        draw_ground_overlay: bool = True,
    ):
        if floor_y is None:
            floor_y = settings.HEIGHT - settings.GROUND_HEIGHT

        self.floor_y_value = max(0, min(settings.HEIGHT, floor_y))
        self.ground_rect.top = self.floor_y_value
        self.ground_rect.height = max(0, settings.HEIGHT - self.floor_y_value)
        self.draw_ground_overlay = draw_ground_overlay
        self.background = self._load_background(map_file)

    def _load_background(self, map_file: str | None) -> pygame.Surface | None:
        if not map_file:
            return None

        map_path = settings.ASSETS_DIR / "Map" / map_file
        if not map_path.exists():
            return None

        image = pygame.image.load(str(map_path)).convert()
        return self._scale_to_cover(image, settings.WIDTH, settings.HEIGHT)

    @staticmethod
    def _scale_to_cover(image: pygame.Surface, target_w: int, target_h: int) -> pygame.Surface:
        src_w, src_h = image.get_size()
        scale = max(target_w / src_w, target_h / src_h)

        scaled_w = int(src_w * scale)
        scaled_h = int(src_h * scale)
        scaled = pygame.transform.smoothscale(image, (scaled_w, scaled_h))

        result = pygame.Surface((target_w, target_h))
        offset_x = (target_w - scaled_w) // 2
        offset_y = (target_h - scaled_h) // 2
        result.blit(scaled, (offset_x, offset_y))
        return result

    def draw(self, surface: pygame.Surface):
        if self.background is not None:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(settings.BG_COLOR)

        if self.draw_ground_overlay:
            hill_points = [
                (0, self.ground_rect.top),
                (170, self.ground_rect.top - 80),
                (360, self.ground_rect.top - 20),
                (560, self.ground_rect.top - 90),
                (760, self.ground_rect.top - 30),
                (settings.WIDTH, self.ground_rect.top),
            ]
            pygame.draw.polygon(surface, self.hill_color, hill_points)
            pygame.draw.rect(surface, self.ground_color, self.ground_rect)
