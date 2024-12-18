import os
import sys

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../ext")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import robot_core_ext

from models import Robot


def test_robot_update():
    mock_image = pygame.Surface((10, 10))
    robot = Robot(1, 1, mock_image, cell_size=32)

    player = type('Player', (object,), {"x": 3, "y": 3})()
    game_map = [
        "0000",
        "0C00",
        "0000",
        "0000"
    ]

    robot_core_ext.update_robot = lambda x, y, px, py, gmap: (x + 1, y + 1, False)

    robot.update(player, game_map)

    assert robot.position() == (2, 2), "Robot position did not update correctly."
    assert robot.is_pinged is False, "Robot 'is_pinged' should remain unchanged."


def test_robot_is_dead():
    mock_image = pygame.Surface((10, 10))
    robot = Robot(1, 1, mock_image, cell_size=32)

    game_map = [
        "0000",
        "0C00",
        "0000",
        "0000"
    ]

    robot_core_ext.is_dead = lambda x, y, gmap: True if gmap[x][y] == 'C' else False

    assert robot.is_dead(game_map) is True, "Robot should be marked as dead."

    robot.x, robot.y = 0, 0
    assert robot.is_dead(game_map) is False, "Robot should not be dead in a safe cell."


def test_robot_position():
    mock_image = pygame.Surface((10, 10))
    robot = Robot(2, 3, mock_image, cell_size=32)

    assert robot.position() == (2, 3), "Initial position is incorrect."

    robot.x, robot.y = 4, 5
    assert robot.position() == (4, 5), "Updated position is incorrect."


def test_update_rect_position():
    mock_image = pygame.Surface((10, 10))
    robot = Robot(2, 3, mock_image, cell_size=32)

    assert robot.rect.topleft == (3 * 32, 2 * 32), "Rect position is incorrect."

    robot.x, robot.y = 4, 6
    robot._update_rect_position()
    assert robot.rect.topleft == (6 * 32, 4 * 32), "Rect position did not update correctly."
