from pathlib import Path

import pygame

from core import settings


ANIMATION_ROOT = settings.ASSETS_DIR / "Animation"


def load_and_scale(path: Path, size: tuple[int, int]) -> pygame.Surface:
    image = pygame.image.load(str(path)).convert_alpha()
    return pygame.transform.scale(image, size)


def load_frames(folder: str, filenames: list[str], size: tuple[int, int]) -> list[pygame.Surface]:
    frames: list[pygame.Surface] = []
    for filename in filenames:
        file_path = ANIMATION_ROOT / folder / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Animation frame not found: {file_path}")
        frames.append(load_and_scale(file_path, size))
    return frames


def list_existing_frames(folder: str, filenames: list[str]) -> list[str]:
    base_path = ANIMATION_ROOT / folder
    return [filename for filename in filenames if (base_path / filename).exists()]
