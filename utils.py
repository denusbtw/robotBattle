import pygame
from pygame import Surface


def load_sprite(image_path: str, size: int) -> pygame.Surface:
    sprite = pygame.image.load(image_path).convert_alpha()
    return pygame.transform.scale(sprite, (size, size))


def load_sprite_sheet(image_path: str, frame_width: int, frame_height: int) -> list[Surface]:
    sprite_sheet = pygame.image.load(image_path).convert_alpha()
    sheet_width, sheet_height = sprite_sheet.get_size()
    tiles = []
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            tile = sprite_sheet.subsurface((x, y, frame_width, frame_height))
            tiles.append(tile)
    return tiles