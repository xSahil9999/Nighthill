import pygame

from core import settings


class MenuScreen:
    def __init__(self):
        self.background = self._load_background()
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 56)

        self.play_button = pygame.Rect(
            settings.MENU_PLAY_X,
            settings.MENU_PLAY_Y,
            settings.MENU_BUTTON_WIDTH,
            settings.MENU_BUTTON_HEIGHT,
        )
        self.exit_button = pygame.Rect(
            settings.MENU_EXIT_X,
            settings.MENU_EXIT_Y,
            settings.MENU_BUTTON_WIDTH,
            settings.MENU_BUTTON_HEIGHT,
        )

    def _load_background(self) -> pygame.Surface | None:
        menu_path = settings.ASSETS_DIR / "menu" / "menu.png"
        if not menu_path.exists():
            return None

        image = pygame.image.load(str(menu_path)).convert()
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

    def get_action(self, mouse_pos: tuple[int, int]) -> str | None:
        if self.play_button.collidepoint(mouse_pos):
            return "play"
        if self.exit_button.collidepoint(mouse_pos):
            return "exit"
        return None

    def draw(self, surface: pygame.Surface):
        if self.background is not None:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((10, 12, 16))
            title = self.title_font.render("Night Hill", True, (240, 240, 240))
            title_rect = title.get_rect(center=(settings.WIDTH // 2, 120))
            surface.blit(title, title_rect)

        self._draw_button(surface, self.play_button, "PLAY", settings.MENU_PLAY_COLOR)
        self._draw_button(surface, self.exit_button, "EXIT", settings.MENU_EXIT_COLOR)

    def _draw_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        color: tuple[int, int, int],
    ):
        if settings.MENU_BUTTONS_VISIBLE:
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, (25, 25, 25), rect, width=2, border_radius=8)

            text = self.font.render(label, True, (20, 20, 20))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
