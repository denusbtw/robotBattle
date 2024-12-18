import pygame
from unittest.mock import Mock

import pytest

from sound_manager import SoundManager


def test_load_sound_success(mocker):
    mock_sound = mocker.patch("pygame.mixer.Sound")
    mock_sound.return_value = Mock()

    manager = SoundManager()
    sound = manager.load_sound("assets/sounds/click3.wav")

    assert sound is not None
    mock_sound.assert_called_with("assets/sounds/click3.wav")


def test_load_sound_failure(mocker):
    mocker.patch("pygame.mixer.Sound", side_effect=pygame.error("Failed to load"))

    manager = SoundManager()
    sound = manager.load_sound("assets/sounds/invalid.wav")

    assert sound is None


def test_sounds_initialization(mocker):
    mock_sound = mocker.patch("pygame.mixer.Sound")
    mock_sound.return_value = Mock()

    manager = SoundManager()

    assert "click" in manager.sounds
    assert "move" in manager.sounds
    assert "collect_key" in manager.sounds
    assert "collect_charge" in manager.sounds
    assert "game_over" in manager.sounds

    assert mock_sound.call_count == len(manager.sounds)


def test_play_sound_success(mocker):
    mock_sound = Mock()
    mock_sound.set_volume = Mock()
    mock_sound.play = Mock()

    mocker.patch("pygame.mixer.Sound", return_value=mock_sound)
    manager = SoundManager()

    manager.play("click", volume=0.8)

    mock_sound.set_volume.assert_called_once_with(0.8)
    mock_sound.play.assert_called_once()


def test_play_sound_missing(mocker):
    mocker.patch("pygame.mixer.Sound", side_effect=pygame.error)
    manager = SoundManager()

    manager.play("nonexistent_sound")


def test_mixer_init_failure(mocker):
    mocker.patch("pygame.mixer.init", side_effect=pygame.error("Mixer failed to initialize"))

    with pytest.raises(pygame.error):
        SoundManager()
