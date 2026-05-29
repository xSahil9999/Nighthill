from animations.utils import list_existing_frames, load_frames


def load_jump_animations(sprite_size: tuple[int, int]) -> dict[str, list]:
    candidates = [f"JUMP{i}.png" for i in range(1, 9)]
    jump_files = list_existing_frames("jump", candidates)

    if jump_files:
        return {"jump": load_frames("jump", jump_files, sprite_size)}

    # Fallback if no dedicated jump sprites exist yet.
    return {"jump": load_frames("idle", ["IDLE2.png", "IDLE3.png"], sprite_size)}

