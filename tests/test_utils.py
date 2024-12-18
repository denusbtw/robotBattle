import pytest
import pygame
from utils import load_sprite, load_sprite_sheet


@pytest.fixture(scope="function")
def init_pygame():
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


class TestLoadSprite:
    def test_load_sprite(self, init_pygame, tmp_path):
        image_path = tmp_path / "test_image.png"
        surface = pygame.Surface((50, 50))
        pygame.image.save(surface, image_path)

        size = 32
        sprite = load_sprite(str(image_path), size)

        assert sprite.get_size() == (size, size), "The sprite size is incorrect."

    def test_load_sprite_invalid_path(self, init_pygame):
        with pytest.raises(FileNotFoundError):
            load_sprite("invalid_path.png", 32)


class TestLoadSpritesheet:
    def test_load_sprite_sheet(self, init_pygame, tmp_path):
        sheet_width, sheet_height = 64, 64
        frame_width, frame_height = 32, 32
        sprite_sheet_path = tmp_path / "test_spritesheet.png"

        surface = pygame.Surface((sheet_width, sheet_height))
        pygame.image.save(surface, sprite_sheet_path)

        tiles = load_sprite_sheet(str(sprite_sheet_path), frame_width, frame_height)

        expected_tiles = (sheet_width // frame_width) * (sheet_height // frame_height)
        assert len(tiles) == expected_tiles, "Incorrect number of tiles extracted."

        for tile in tiles:
            assert tile.get_size() == (frame_width, frame_height), "Tile size is incorrect."


    def test_load_sprite_sheet_invalid_path(self, init_pygame):
        with pytest.raises(FileNotFoundError):
            load_sprite_sheet("invalid_path.png", 32, 32)