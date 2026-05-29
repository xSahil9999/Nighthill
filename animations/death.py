import re
from pathlib import Path

from animations.utils import ANIMATION_ROOT, load_and_scale


def _death_sort_key(path: Path) -> int:
    stem = path.stem.upper()
    if stem == "DEATH":
        return -1

    match = re.fullmatch(r"DEATH(\d+)", stem)
    if match:
        return int(match.group(1))

    return 9999


def load_death_animations(sprite_size: tuple[int, int]) -> dict[str, list]:
    death_dir = ANIMATION_ROOT / "death"
    frame_paths = sorted(death_dir.glob("DEATH*.png"), key=_death_sort_key)

    if not frame_paths:
        return {}

    frames = [load_and_scale(frame_path, sprite_size) for frame_path in frame_paths]
    return {"death": frames}

