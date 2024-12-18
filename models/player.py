import player_core_ext
import pygame

from sound_manager import SoundManager


class Player:
    def __init__(self,
                 x: int,
                 y: int,
                 max_charges: int
                 ):
        self.x = x
        self.y = y
        self.charges = max_charges
        self.max_charges = max_charges
        self.keys = 0

        self.sound_manager = SoundManager()

    def move(self,
             target_x: int,
             target_y: int,
             robots: pygame.sprite.Group,
             charges: pygame.sprite.Group,
             keys: pygame.sprite.Group,
             game_map: list[list[str]]
             ):
        robot_positions = [robot.position() for robot in robots]
        charge_positions = [(charge.x, charge.y) for charge in charges]
        key_positions = [(key.x, key.y) for key in keys]

        result = player_core_ext.move_player(
            self.x, self.y, target_x, target_y,
            robot_positions, charge_positions, key_positions,
            game_map, self.charges, self.max_charges, self.keys
        )

        self.x, self.y = target_x, target_y

        for charge in charges.copy():
            if charge.position() == (self.x, self.y) and self.charges < self.max_charges:
                charge.interact(self)
                self.sound_manager.play('collect_charge')
                charges.remove(charge)

        for key in keys.copy():
            if key.position() == (self.x, self.y):
                key.interact(self)
                self.sound_manager.play('collect_key')
                keys.remove(key)

        return result

    def get_movable_cells(self, game_map: list[list[str]]):
        return player_core_ext.get_movable_cells(self.x, self.y, game_map)

