import os
import sys

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from game import Game
from unittest.mock import patch, Mock


@patch('pygame.event.get')
@patch('game.Game.handle_left_click')
@patch('game.Game.handle_right_click')
def test_handle_events(mock_right_click, mock_left_click, mock_event_get):
    game = Game()
    mock_event_get.return_value = [
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (50, 50), "button": 1}),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (50, 50), "button": 3}),
    ]

    with patch('game.Game.get_cell_from_mouse', return_value=(2, 2)):
        game.handle_events()

    mock_left_click.assert_called_with(2, 2)
    mock_right_click.assert_called_with(2, 2)



@patch('pygame.mixer.music.load')
@patch('pygame.mixer.music.play')
def test_play_background_music(mock_play, mock_load):
    game = Game()
    game.play_background_music()
    mock_load.assert_called_with("assets/sounds/background_music.mp3")
    mock_play.assert_called_with(loops=-1)
