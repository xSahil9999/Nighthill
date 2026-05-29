from animations.utils import load_frames


def load_move_animations(sprite_size: tuple[int, int]) -> dict[str, list]:
    return {
        "idle": load_frames(
            "idle",
            ["IDLE1.png", "IDLE2.png", "IDLE3.png"],
            sprite_size,
        ),
        "run": load_frames(
            "move",
            ["RUN1.png", "RUN2.png", "RUN3.png", "RUN4.png", "RUN5.png", "RUN6.png"],
            sprite_size,
        ),
    }

