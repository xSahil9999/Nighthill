from animations.utils import load_frames


def load_attack_animations(sprite_size: tuple[int, int]) -> dict[str, list]:
    return {
        "attack1": load_frames(
            "attack",
            ["ATTACK1.png", "ATTACK2.png", "ATTACK3.png", "ATTACK4.png", "ATTACK5.png"],
            sprite_size,
        ),
        "attack2": load_frames(
            "attack",
            ["ATTACK2_1.png", "ATTACK2_2.png", "ATTACK2_3.png", "ATTACK2_4.png"],
            sprite_size,
        ),
        "attack3": load_frames(
            "attack",
            ["ATTACK3_1.png", "ATTACK3_2.png", "ATTACK3_3.png", "ATTACK3_4.png", "ATTACK3_5.png"],
            sprite_size,
        ),
    }

