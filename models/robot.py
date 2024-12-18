import pygame
import robot_core_ext

class Robot(pygame.sprite.Sprite):
    def __init__(self,
                 x: int,
                 y: int,
                 image: pygame.Surface,
                 cell_size: int
                 ):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.cell_size = cell_size
        self.x = x
        self.y = y
        self.is_pinged = False
        self._update_rect_position()

    def _update_rect_position(self) -> None:
        self.rect.topleft = (self.y * self.cell_size, self.x * self.cell_size)

    def update(self, player, game_map: list[list[str]]) -> None:
        player_x, player_y = player.x, player.y

        cpp_game_map = [list(row) for row in game_map]

        new_x, new_y, dead = robot_core_ext.update_robot(self.x, self.y, player_x, player_y, cpp_game_map)

        self.x, self.y = new_x, new_y
        self.is_pinged = False if dead else self.is_pinged
        self._update_rect_position()

    def is_dead(self, game_map: list[list[str]]) -> bool:
        cpp_game_map = [list(row) for row in game_map]
        return robot_core_ext.is_dead(self.x, self.y, cpp_game_map)

    def position(self) -> tuple[int, int]:
        return self.x, self.y
