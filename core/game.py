import sys

import pygame

from core import settings
from core.window import create_window
from entities.boss_queen import BossQueen
from entities.enemy import Enemy
from entities.npc import NPC
from entities.player import Player
from ui.menu_screen import MenuScreen
from world.game_map import GameMap


class Game:
    def __init__(self):
        # - Fenster, Map und Menue laden.
        self.screen, self.clock = create_window()
        self.game_map = GameMap()
        self.menu = MenuScreen()

        self.state = "menu"
        self.running = True

        self.current_level = settings.START_LEVEL
        self.player: Player | None = None
        # - Enemies kann normale Gegner oder Boss enthalten.
        self.enemies: list[Enemy | BossQueen] = []
        self.npcs: list[NPC] = []
        self.game_won = False
        self.death_timer = 0
        self.respawn_font = pygame.font.SysFont(None, 34)
        self.win_font = pygame.font.SysFont(None, 52)
        self.level_font = pygame.font.SysFont(None, 24)

        self.load_level(self.current_level)

    def _get_level_config(self) -> dict:
        if self.current_level in settings.LEVELS:
            return settings.LEVELS[self.current_level]
        return settings.LEVELS[1]

    def load_level(self, level_number: int, preserve_player_health: bool = False):
        # - Optional alte Lebenspunkte merken.
        previous_health: int | None = None
        if preserve_player_health and self.player is not None:
            previous_health = self.player.health

        self.current_level = level_number if level_number in settings.LEVELS else 1
        self.game_won = False
        self.death_timer = 0
        level_config = self._get_level_config()
        self.game_map.set_level_visuals(
            map_file=level_config.get("map_file"),
            floor_y=level_config.get("floor_y"),
            draw_ground_overlay=level_config.get("draw_ground_overlay", True),
        )

        floor_y = self.game_map.floor_y
        player_y = floor_y - settings.SPRITE_SIZE[1]
        self.player = Player(level_config["player_spawn_x"], player_y, floor_y)

        # - Level kann erzwungen volle HP setzen (z.B. Hintergrund4).
        if bool(level_config.get("refill_player_health", False)):
            self.player.health = self.player.max_health
        elif previous_health is not None:
            self.player.health = max(1, min(self.player.max_health, previous_health))

        # - Standardgegner laden.
        enemy_y = floor_y - settings.ENEMY_SIZE[1]
        self.enemies = [Enemy(x, enemy_y) for x in level_config["enemy_spawns_x"]]

        # - Optional Boss laden.
        level_boss = self._build_level_boss(level_config, floor_y)
        if level_boss is not None:
            self.enemies.append(level_boss)

        self.npcs = self._build_npcs(level_config, floor_y)

    def _build_level_boss(self, level_config: dict, floor_y: int) -> BossQueen | None:
        # - Kein Boss in diesem Level.
        boss_config = level_config.get("boss_queen")
        if not isinstance(boss_config, dict):
            return None

        size = boss_config.get("size")
        boss_width, boss_height = settings.BOSS_SIZE
        if (
            isinstance(size, (list, tuple))
            and len(size) == 2
            and isinstance(size[0], int)
            and isinstance(size[1], int)
            and size[0] > 0
            and size[1] > 0
        ):
            boss_width, boss_height = size[0], size[1]

        spawn_x = boss_config.get("x")
        if not isinstance(spawn_x, int):
            spawn_x = settings.WIDTH - boss_width - 120

        hover_height = boss_config.get("hover_height")
        if not isinstance(hover_height, int):
            hover_height = 70

        spawn_x = max(0, min(settings.WIDTH - boss_width, spawn_x))
        spawn_y = floor_y - boss_height - hover_height
        spawn_y = max(0, min(settings.HEIGHT - boss_height, spawn_y))

        # - Boss mit berechneter Position/Groesse erstellen.
        return BossQueen(spawn_x, spawn_y, width=boss_width, height=boss_height)

    def _build_npcs(self, level_config: dict, floor_y: int) -> list[NPC]:
        # - Neue NPC-Konfiguration (Liste von Dicts).
        npc_configs = level_config.get("npcs")
        if isinstance(npc_configs, list):
            built_npcs: list[NPC] = []
            for npc_cfg in npc_configs:
                if not isinstance(npc_cfg, dict):
                    continue

                x = npc_cfg.get("x")
                if not isinstance(x, int):
                    continue

                name = npc_cfg.get("name") if isinstance(npc_cfg.get("name"), str) else "Goddess"
                sprite_file = npc_cfg.get("sprite_file") if isinstance(npc_cfg.get("sprite_file"), str) else None
                # - Optionales Schweben pro NPC.
                floating = bool(npc_cfg.get("floating", False))

                size_value = npc_cfg.get("size")
                sprite_size: tuple[int, int] = settings.NPC_SPRITE_SIZE
                if (
                    isinstance(size_value, (list, tuple))
                    and len(size_value) == 2
                    and isinstance(size_value[0], int)
                    and isinstance(size_value[1], int)
                    and size_value[0] > 0
                    and size_value[1] > 0
                ):
                    sprite_size = (size_value[0], size_value[1])

                dialogue_raw = npc_cfg.get("dialogue")
                dialogue: list[tuple[str, str]] | None = None
                if isinstance(dialogue_raw, list):
                    parsed: list[tuple[str, str]] = []
                    for row in dialogue_raw:
                        if (
                            isinstance(row, (list, tuple))
                            and len(row) == 2
                            and isinstance(row[0], str)
                            and isinstance(row[1], str)
                        ):
                            parsed.append((row[0], row[1]))
                    if parsed:
                        dialogue = parsed

                float_amplitude = npc_cfg.get("float_amplitude")
                if not isinstance(float_amplitude, int):
                    float_amplitude = None

                float_speed = npc_cfg.get("float_speed")
                if not isinstance(float_speed, (float, int)):
                    float_speed = None

                built_npcs.append(
                    NPC(
                        x=x,
                        y=floor_y - sprite_size[1],
                        name=name,
                        dialogue=dialogue,
                        sprite_file=sprite_file,
                        sprite_size=sprite_size,
                        floating=floating,
                        float_amplitude=float_amplitude,
                        float_speed=float_speed,
                    )
                )

            return built_npcs

        legacy_spawns = level_config.get("npc_spawns_x", [])
        default_y = floor_y - settings.NPC_SPRITE_SIZE[1]
        return [NPC(x, default_y) for x in legacy_spawns if isinstance(x, int)]

    def _handle_right_exit_progression(self):
        if self.player is None or self.state != "playing" or self.player.dead:
            return

        level_config = self._get_level_config()
        next_level = level_config.get("next_level_on_right_exit")
        if not isinstance(next_level, int):
            return

        require_clear = bool(level_config.get("require_enemies_cleared_for_exit", False))
        if require_clear and self.enemies:
            return

        if self.player.rect.right >= settings.WIDTH:
            self.load_level(next_level, preserve_player_health=True)

    def respawn_player(self):
        self.load_level(self.current_level)

    def handle_events(self):
        if self.player is None:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "menu":
                    action = self.menu.get_action(event.pos)
                    if action == "play":
                        self.state = "playing"
                    elif action == "exit":
                        self.running = False
                elif self.state == "playing":
                    self.player.start_attack()

            elif event.type == pygame.KEYDOWN:
                if self.state == "playing" and event.key == pygame.K_j:
                    self.player.start_attack()
                elif self.state == "playing" and event.key == pygame.K_e:
                    self.try_npc_interaction()
                elif self.state == "playing" and event.key == pygame.K_r and self.player.dead:
                    self.respawn_player()
                elif self.state == "menu" and event.key == pygame.K_RETURN:
                    self.state = "playing"
                elif self.state == "menu" and event.key == pygame.K_ESCAPE:
                    self.running = False

    def try_npc_interaction(self):
        if self.player is None:
            return

        interacted = False
        target_level: int | None = None
        level_config = self._get_level_config()

        for npc in self.npcs:
            if npc.is_player_near(self.player.rect):
                result = npc.interact()
                if result == "finished":
                    next_level = level_config.get("next_level_on_npc_finish")
                    if isinstance(next_level, int):
                        target_level = next_level
                interacted = True
            else:
                npc.stop_talking()

        if target_level is not None:
            self.load_level(target_level, preserve_player_health=True)
            return

        if not interacted:
            for npc in self.npcs:
                npc.stop_talking()

    def update(self):
        if self.state != "playing" or self.player is None:
            return

        # - Nach Boss-Tod keine Spiel-Updates mehr.
        if self.game_won:
            return

        self.player.update()
        self._handle_player_attack_hits()

        # - Auto-Respawn wenn Spieler tot ist.
        if self.player.dead:
            self._handle_auto_respawn()
            return

        for npc in self.npcs:
            npc.update()
            if npc.talking and not npc.is_player_near(self.player.rect):
                npc.stop_talking()

        for enemy in self.enemies:
            enemy.update(self.player.rect)

        if not self.player.dead:
            for enemy in self.enemies:
                if enemy.can_damage_player(self.player.rect):
                    self.player.take_damage(1)
                    if self.player.dead:
                        self._handle_auto_respawn()
                        break

        if self._is_level_boss_defeated():
            self.game_won = True
            return

        # - Tote Standardgegner werden entfernt, Boss bleibt fuer Win-Anzeige.
        if settings.ENEMY_DISAPPEAR_ON_DEATH:
            self.enemies = [
                enemy
                for enemy in self.enemies
                if not (enemy.dead and getattr(enemy, "remove_on_death", True))
            ]

        self._handle_right_exit_progression()

    def _handle_player_attack_hits(self):
        if self.player is None or not self.player.can_deal_damage():
            return

        hitbox = self.player.get_attack_hitbox()
        if hitbox is None:
            return

        for enemy in self.enemies:
            if enemy.dead:
                continue

            if hitbox.colliderect(enemy.rect):
                was_hit = enemy.take_damage(1)
                if was_hit:
                    self.player.mark_attack_damage_done()
                    break

    def _is_level_boss_defeated(self) -> bool:
        boss_found = False
        for enemy in self.enemies:
            if getattr(enemy, "is_boss", False):
                boss_found = True
                if not enemy.dead:
                    return False
        return boss_found

    def _handle_auto_respawn(self):
        if self.player is None or not self.player.dead:
            self.death_timer = 0
            return

        # - Falls deaktiviert, bleibt nur manuelles Respawn.
        if not settings.AUTO_RESPAWN_ON_DEATH:
            return

        # - Nach Delay Level neu laden.
        self.death_timer += 1
        if self.death_timer >= settings.RESPAWN_DELAY_FRAMES:
            self.respawn_player()

    def draw(self):
        if self.player is None:
            return

        if self.state == "menu":
            self.menu.draw(self.screen)
            pygame.display.flip()
            return

        self.game_map.draw(self.screen)

        for npc in self.npcs:
            npc.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        self.player.draw_health(self.screen)
        for npc in self.npcs:
            npc.draw_overlay(self.screen, self.player.rect)

        if self.game_won:
            self._draw_win_hint()
        elif self.player.dead:
            self._draw_respawn_hint()

        self._draw_level_hint()
        pygame.display.flip()

    def _draw_respawn_hint(self):
        title = self.respawn_font.render("Du bist gestorben", True, (255, 210, 210))
        hint = self.respawn_font.render("Druecke R zum Respawn", True, (255, 240, 220))
        title_rect = title.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 20))
        hint_rect = hint.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20))
        self.screen.blit(title, title_rect)
        self.screen.blit(hint, hint_rect)

    def _draw_win_hint(self):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        title = self.win_font.render("WIN GAME", True, (255, 244, 160))
        subtitle = self.respawn_font.render("ist zu Ende", True, (245, 245, 245))
        title_rect = title.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 10))
        subtitle_rect = subtitle.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 34))
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)

    def _draw_level_hint(self):
        label = self.level_font.render(f"Level {self.current_level}", True, (240, 240, 240))
        self.screen.blit(label, (12, 12))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)

        pygame.quit()
        sys.exit()
