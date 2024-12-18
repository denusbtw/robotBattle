import pygame

class Charge(pygame.sprite.Sprite):
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
        self.rect.topleft = (y * self.cell_size, x * self.cell_size)

    def interact(self, player) -> None:
        player.charges += 1

    def position(self) -> tuple[int, int]:
        return self.x, self.y
