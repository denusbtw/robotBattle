import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "ext")))

import pygame

import map_generator_ext
import game_core_ext

from game_config import GameConfig
from game_over_screen import GameOverScreen
from game_renderer import GameRenderer
from models import Charge, Key
from models.player import Player
from models.robot import Robot
from sound_manager import SoundManager
from start_menu import StartMenu
from utils import load_sprite_sheet, load_sprite

class Game:
    def __init__(self):
        pygame.init()
        self.sound_manager = SoundManager()

        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Robot Battle')
        start_menu = StartMenu(self.screen)
        self.difficulty = start_menu.run()

        self.game_config = GameConfig(difficulty=self.difficulty)
        self._initialize_screen()

        self.load_assets()

        cfg_data = map_generator_ext.ConfigData()
        grid = self.game_config.get_grid_settings()
        gameplay = self.game_config.get_gameplay_settings()
        diff = self.game_config.get_difficulty_settings()
        textures = self.game_config.get_textures_settings()

        cfg_data.rows = grid["rows"]
        cfg_data.cols = grid["cols"]
        cfg_data.default_textures = textures["default"]
        cfg_data.player_pos = (gameplay["player_start_position"][0], gameplay["player_start_position"][1])
        cfg_data.exit_pos = (gameplay["exit_position"][0], gameplay["exit_position"][1])
        cfg_data.number_of_keys = gameplay["number_of_keys"]

        cfg_data.clefts_coeff = diff["clefts_coefficient"]
        cfg_data.initial_robots_coeff = diff["initial_robots_coefficient"]
        cfg_data.charges_coeff = diff["charges_coefficient"]
        cfg_data.key_coefficient = cfg_data.number_of_keys / (cfg_data.rows * cfg_data.cols)

        cfg_data.cleft_char = textures["cleft"]
        cfg_data.robot_char = textures["robot"]
        cfg_data.charge_char = textures["charge"]
        cfg_data.key_char = textures["key"]
        cfg_data.player_char = textures["player"]
        cfg_data.exit_char = textures["exit"]

        self.map = map_generator_ext.generate_map(cfg_data)

        self.robots = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()
        self.charges = pygame.sprite.Group()
        self.pinged_robots = []
        self.player_turn = True
        self.exit_pos = (gameplay["exit_position"][0], gameplay["exit_position"][1])

        self.convert_map()

        self.play_background_music()

    def _initialize_screen(self) -> None:
        rows = self.game_config.get_grid_settings()["rows"]
        cols = self.game_config.get_grid_settings()["cols"]
        cell_size = self.game_config.get_grid_settings()["cell_size"]
        width, height = cols * cell_size, rows * cell_size
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Robot Battle')

        self.clock = pygame.time.Clock()

    def load_assets(self) -> None:
        cell_size = self.game_config.get_grid_settings()["cell_size"]
        self.tiles = load_sprite_sheet('assets/tiles.png', cell_size, cell_size)
        self.player_image = load_sprite('assets/astronaut.png', cell_size)
        self.robot_image = load_sprite('assets/robot1.png', cell_size)
        self.key_image = load_sprite('assets/key.png', cell_size)
        self.charge_image = load_sprite('assets/charge.png', cell_size)

    def check_for_win(self) -> None:
        if (self.player.x, self.player.y) == self.exit_pos and self.player.keys >= self.game_config.get_gameplay_settings()['number_of_keys']:
            self._game_over(reason='win')

    def convert_map(self) -> None:
        robots, charges, keys, player_pos = game_core_ext.convert_map(self.map)

        for x, y in robots:
            self.robots.add(Robot(x, y, self.robot_image, self.game_config.get_grid_settings()["cell_size"]))

        for x, y in charges:
            self.charges.add(Charge(x, y, self.charge_image, self.game_config.get_grid_settings()["cell_size"]))

        for x, y in keys:
            self.keys.add(Key(x, y, self.key_image, self.game_config.get_grid_settings()["cell_size"]))

        if player_pos != (-1, -1):
            self.player = Player(player_pos[0], player_pos[1],
                                 self.game_config.get_difficulty_settings()['max_charges'])

    def get_cell_from_mouse(self, pos: tuple[int, int]) -> tuple[int, int]:
        cell_size = self.game_config.get_grid_settings()["cell_size"]
        x, y = pos
        row, col = game_core_ext.get_cell_from_mouse(x, y, cell_size)
        return row, col

    def kill_pinged_robots(self) -> None:
        for robot in self.pinged_robots:
            robot.kill()
        self.pinged_robots.clear()

    def handle_right_click(self, row: int, col: int) -> None:
        movable_cells = self.player.get_movable_cells(self.map)
        for robot in self.robots:
            if robot.position() == (row, col) and (row, col) in movable_cells:
                if robot.is_pinged:
                    robot.is_pinged = False
                    if robot in self.pinged_robots:
                        self.pinged_robots.remove(robot)
                    self.player.charges += 1
                else:
                    if self.player.charges > 0 and robot not in self.pinged_robots:
                        robot.is_pinged = True
                        self.pinged_robots.append(robot)
                        self.player.charges -= 1
                break

    def handle_left_click(self, row: int, col: int) -> None:
        movable_cells = self.player.get_movable_cells(self.map)
        if (row, col) in movable_cells:
            self.kill_pinged_robots()
            self.player.move(row, col, self.robots, self.charges, self.keys, self.map)
            self.sound_manager.play('move')
            self.player_turn = False

            self.check_for_win()

    def check_for_collision(self) -> None:
        x, y = self.player.x, self.player.y
        robot_positions = [(robot.x, robot.y) for robot in self.robots]
        if game_core_ext.check_for_collision(x, y, robot_positions):
            self._game_over(reason='robot')

    def check_for_cleft(self) -> None:
        x, y = self.player.x, self.player.y
        converted_map = [[str(cell) for cell in row] for row in self.map]
        if game_core_ext.check_for_cleft(converted_map, x, y):
            self._game_over(reason='cleft')

    def _game_over(self, reason: str) -> None:
        pygame.mixer.music.stop()
        game_over_screen = GameOverScreen(self.screen.get_size(), self.screen.copy())

        if reason == 'win':
            win_message = "Congratulations! You've won the game!"
            result = game_over_screen.show(reason='win', message=win_message)
        else:
            death_message = self.select_death_message(reason)
            result = game_over_screen.show(reason='lose', message=death_message)

        if result == 'restart':
            self.__init__()
        else:
            pygame.quit()
            sys.exit()

    def select_death_message(self, reason: str) -> str:
        return game_core_ext.select_death_message(reason)

    def play_background_music(self) -> None:
        try:
            music_path = "assets/sounds/background_music.mp3"
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            print(f"Error loading background music: {e}")

    def update_robots(self) -> None:
        self.robots.update(self.player, self.map)
        for robot in self.robots.copy():
            if robot.is_dead(self.map):
                self.robots.remove(robot)

    def main_loop(self) -> None:
        while True:
            self.handle_events()
            self.check_for_collision()
            self.check_for_cleft()

            if not self.player_turn:
                self.update_robots()
                self.check_for_collision()
                self.player_turn = True

            self.render()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.player_turn and event.type == pygame.MOUSEBUTTONDOWN:
                row, col = self.get_cell_from_mouse(event.pos)
                match event.button:
                    case 1: self.handle_left_click(row, col)
                    case 3: self.handle_right_click(row, col)

    def render(self):
        renderer = GameRenderer(
            self.screen,
            self.tiles,
            self.player_image,
            self.robot_image,
            self.key_image,
            self.charge_image,
            self.game_config
        )
        renderer.render(
            self.map,
            self.keys,
            self.charges,
            self.player,
            self.robots,
            self.player.get_movable_cells(self.map)
        )

    def run(self):
        self.main_loop()


if __name__ == '__main__':
    game = Game()
    game.run()
