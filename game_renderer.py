import os
import pygame

from game_config import GameConfig
from models import Robot, Player, Key, Charge


class GameRenderer:
    def __init__(self,
                 screen: pygame.Surface,
                 tiles: list[pygame.Surface],
                 player_sprite: pygame.Surface,
                 robot_sprite: pygame.Surface,
                 key_sprite: pygame.Surface,
                 charge_sprite: pygame.Surface,
                 config: GameConfig,
                 ):
        self.screen = screen
        self.tiles = tiles
        self.player_sprite = player_sprite
        self.robot_sprite = robot_sprite
        self.key_sprite = key_sprite
        self.charge_sprite = charge_sprite
        self.config = config

        grid_settings = config.get_grid_settings()
        color_settings = config.get_color_settings()
        textures = config.get_textures_settings()
        gameplay_settings = config.get_gameplay_settings()

        self.rows = grid_settings["rows"]
        self.cols = grid_settings["cols"]
        self.cell_size = grid_settings["cell_size"]

        self.exit_pos = gameplay_settings["exit_position"]

        self.exit_color = tuple(color_settings["exit"])
        self.stroke_color = color_settings['stroke']
        self.white = (255, 255, 255)

        self.textures = textures

        self.difficulty = config.difficulty

        self.hud_charge_icon = pygame.transform.scale(charge_sprite, (30, 30))
        self.hud_key_icon = pygame.transform.scale(key_sprite, (30, 30))

        font_path = os.path.join('assets', 'fonts', 'PressStart2P-Regular.ttf')
        self.font = pygame.font.Font(font_path, 20)

    def draw_grid(self, game_map: list[list[str]]) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                cell_value = game_map[row][col]
                frame_index = self.get_frame_index(cell_value)
                rect = pygame.Rect(
                    col * self.cell_size,
                    row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                self.screen.blit(self.tiles[frame_index], rect)

    def get_frame_index(self, cell_value: str) -> pygame.Surface | int:
        if cell_value == 'C':
            return self.textures["default"][0]-1
        elif cell_value in 'RGKPE':
            return self.textures["default"][0]
        elif cell_value.isdigit():
            return int(cell_value)
        else:
            raise ValueError(f"Unknown cell value: {cell_value}")

    def draw_exit(self) -> None:
        rect = pygame.Rect(
            self.exit_pos[1] * self.cell_size,
            self.exit_pos[0] * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(self.screen, self.exit_color, rect)

    def draw_objects(self, objects: pygame.sprite.Group | list, sprite: pygame.Surface) -> None:
        for obj in objects:
            obj_rect = sprite.get_rect(
                center=(
                    obj.y * self.cell_size + self.cell_size // 2,
                    obj.x * self.cell_size + self.cell_size // 2,
                )
            )
            self.screen.blit(sprite, obj_rect)

    def draw_highlight_stroke(self, cells: list[list[str]]) -> None:
        for row, col in cells:
            rect = pygame.Rect(
                col * self.cell_size + 2,
                row * self.cell_size + 2,
                self.cell_size - 4,
                self.cell_size - 4
            )
            pygame.draw.rect(self.screen, self.stroke_color, rect, width=2)

    def draw_robot(self, robot: Robot) -> None:
        robot_rect = self.robot_sprite.get_rect(
            center=(
                robot.y * self.cell_size + self.cell_size // 2,
                robot.x * self.cell_size + self.cell_size // 2,
            )
        )
        self.screen.blit(self.robot_sprite, robot_rect)
        if robot.is_pinged:
            pygame.draw.ellipse(self.screen, (0, 255, 255), robot_rect.inflate(-10, -10), width=2)

    def draw_robots(self, robots: pygame.sprite.Group) -> None:
        for robot in robots:
            self.draw_robot(robot)

    def draw_player(self, player: Player) -> None:
        self.draw_objects([player], self.player_sprite)

    def render_hud(self, player: Player) -> None:
        hud_background_rect = pygame.Rect(10, 20, 230, 50)
        pygame.draw.rect(self.screen, (0, 0, 0), hud_background_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.white, hud_background_rect, width=2, border_radius=8)

        self.screen.blit(self.hud_charge_icon, (20, 28))
        charge_text = self.font.render(f"x{player.charges}", True, self.white)
        self.screen.blit(charge_text, (60, 33))

        self.screen.blit(self.hud_key_icon, (140, 28))
        key_text = self.font.render(f"x{player.keys}", True, self.white)
        self.screen.blit(key_text, (180, 33))

    def render(self,
               game_map: list[list[str]],
               keys: pygame.sprite.Group,
               charges: pygame.sprite.Group,
               player: Player,
               robots: pygame.sprite.Group,
               highlight_cells: list[list[str]]
               ) -> None:
        self.screen.fill((0, 0, 0))
        self.draw_grid(game_map)
        self.draw_exit()
        self.draw_objects(keys, self.key_sprite)
        self.draw_objects(charges, self.charge_sprite)
        self.draw_highlight_stroke(highlight_cells)
        self.draw_player(player)
        self.draw_robots(robots)
        self.render_hud(player)
        pygame.display.flip()
