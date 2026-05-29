from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

# - Fenster und Spielbasis.
WIDTH = 960
HEIGHT = 600
FPS = 60
TITLE = "Night Hill"

# - Basisfarben und Sprite-Groessen.
BG_COLOR = (20, 20, 30)
SPRITE_SIZE = (96, 96)
ENEMY_SIZE = (72, 96)
NPC_SPRITE_SIZE = (110, 138)

# - Spieler-Physik.
PLAYER_SPEED = 4
GRAVITY = 0.7
JUMP_STRENGTH = 13

# - Animationsgeschwindigkeit Spieler/NPC.
IDLE_SPEED = 18
RUN_SPEED = 6
ATTACK_SPEED = 4
JUMP_SPEED = 8
DEATH_SPEED = 7
NPC_IDLE_SPEED = 16
NPC_FLOAT_AMPLITUDE = 10
NPC_FLOAT_SPEED = 0.06

# - Standardgegner (Skeleton).
GROUND_HEIGHT = 110
ENEMY_SPEED = 2
ENEMY_IDLE_SPEED = 20
ENEMY_WALK_SPEED = 8
ENEMY_ATTACK_SPEED = 5
ENEMY_PATROL_RANGE = 120
ENEMY_AGGRO_DISTANCE_X = 220
ENEMY_AGGRO_DISTANCE_Y = 110
ENEMY_ATTACK_DISTANCE_X = 90
ENEMY_ATTACK_DISTANCE_Y = 95
ENEMY_ATTACK_COOLDOWN = 50
ENEMY_DAMAGE_FRAME = 3
ENEMY_DEATH_SPEED = 10
ENEMY_MAX_HEALTH = 3
ENEMY_HIT_COOLDOWN = 14
ENEMY_DISAPPEAR_ON_DEATH = True

# - Boss (Koenigin in Hintergrund4).
BOSS_SIZE = (170, 220)
BOSS_IDLE_SPEED = 20
BOSS_ATTACK_SPEED = 7
BOSS_DEATH_SPEED = 12
BOSS_FLOAT_AMPLITUDE = 18
BOSS_FLOAT_SPEED = 0.07
BOSS_DRIFT_SPEED = 2
BOSS_AGGRO_DISTANCE_X = 340
BOSS_AGGRO_DISTANCE_Y = 180
BOSS_ATTACK_DISTANCE_X = 132
BOSS_ATTACK_DISTANCE_Y = 140
BOSS_ATTACK_RADIUS = 185
BOSS_ATTACK_COOLDOWN = 66
BOSS_DAMAGE_FRAME = 3
BOSS_DAMAGE_WINDOW_FRAMES = 8
BOSS_MAX_HEALTH = 5
BOSS_HIT_COOLDOWN = 16

# - Spielerleben und Respawn.
PLAYER_MAX_HEALTH = 3
PLAYER_HIT_COOLDOWN = 40
AUTO_RESPAWN_ON_DEATH = True
RESPAWN_DELAY_FRAMES = 90

# - Menue-Buttons.
MENU_BUTTONS_VISIBLE = True
MENU_BUTTON_WIDTH = 320
MENU_BUTTON_HEIGHT = 70
MENU_PLAY_X = (WIDTH - MENU_BUTTON_WIDTH) // 2
MENU_PLAY_Y = 220
MENU_EXIT_X = (WIDTH - MENU_BUTTON_WIDTH) // 2
MENU_EXIT_Y = 305
MENU_PLAY_COLOR = (70, 200, 120)
MENU_EXIT_COLOR = (220, 90, 90)

NPC_INTERACT_DISTANCE_X = 120
NPC_INTERACT_DISTANCE_Y = 90

ENEMY_ASSETS_DIR = PROJECT_ROOT / "Enemy"
START_LEVEL = 1

# - Levelablauf:
#   1 -> NPC1 Dialog
#   2 -> Skeletons erledigen + rechts raus
#   3 -> NPC2 Dialog
#   4 -> Bosskampf
LEVELS = {
    1: {
        "map_file": "Hintergrund.png",
        "player_spawn_x": 200,
        "enemy_spawns_x": [],
        "npcs": [
            {
                "x": 420,
                "name": "Goddess",
                "size": [88, 124],
                # - NPC1 schwebt leicht.
                "floating": True,
                "float_amplitude": 12,
                "float_speed": 0.07,
                "dialogue": [
                    ("Du bist endlich erschienen...", "Ich habe lange auf dich gewartet."),
                    ("Die Welt NightHill wird von Schatten verschlungen.", ""),
                    ("Der Daemonenkoenig hat seine Armee geschickt.", "Unsere Doerfer sind gefallen..."),
                    ("Viele Helden haben versucht, ihn zu besiegen.", "Keiner ist zurueckgekehrt."),
                    ("Aber die alte Prophezeiung sprach von einem Fremden...", ""),
                    ("Ein Wanderer aus einer anderen Welt...", "der NightHill retten wird."),
                    ("Du bist dieser Wanderer.", ""),
                    ("Finde deine Waffe.", "Werde staerker."),
                    ("Und besiege den Daemonenkoenig...", "bevor alles verloren ist."),
                ],
            },
        ],
        "next_level_on_npc_finish": 2,
        # - Etwas tieferer Boden nur in Hintergrund1.
        "floor_y": HEIGHT - GROUND_HEIGHT + 24,
        "draw_ground_overlay": False,
    },
    2: {
        "map_file": "Hintergrund2.png",
        "player_spawn_x": 160,
        "enemy_spawns_x": [520, 760],
        "npcs": [],
        "next_level_on_right_exit": 3,
        "require_enemies_cleared_for_exit": True,
        "floor_y": HEIGHT - GROUND_HEIGHT,
        "draw_ground_overlay": False,
    },
    3: {
        "map_file": "hintergrund3.png",
        "player_spawn_x": 160,
        "enemy_spawns_x": [],
        "npcs": [
            {
                "x": 310,
                "name": "NPC2",
                "sprite_file": "NPC/NPC2.png",
                "size": [130, 138],
                "dialogue": [
                    ("Halt!", ""),
                    ("Du solltest hier nicht sein.", ""),
                    ("Der Daemonenkoenig ist kein Gegner fuer dich.", ""),
                    ("Viele Krieger sind gegangen...", "keiner kam zurueck."),
                    ("Wenn du leben willst...", "dann verschwinde aus NightHill."),
                    ("Dieser Krieg ist laengst verloren.", ""),
                ],
            },
        ],
        "next_level_on_npc_finish": 4,
        "floor_y": HEIGHT - GROUND_HEIGHT,
        "draw_ground_overlay": False,
    },
    4: {
        "map_file": "Hintergrund4.png",
        "player_spawn_x": 140,
        "enemy_spawns_x": [],
        "npcs": [],
        "refill_player_health": True,
        "boss_queen": {
            "x": 700,
            "hover_height": 70,
            "size": [170, 220],
        },
        "floor_y": HEIGHT - GROUND_HEIGHT,
        "draw_ground_overlay": False,
    },
}
