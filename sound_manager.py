import pygame


class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self.sounds = {
            'click': self.load_sound('assets/sounds/click3.wav'),
            # 'ping': self.load_sound('assets/sounds/ping.wav'),
            'move': self.load_sound('assets/sounds/move.wav'),
            'collect_key': self.load_sound('assets/sounds/collect_item.wav'),
            'collect_charge': self.load_sound('assets/sounds/collect_item.wav'),
            # 'robot_death': self.load_sound('assets/sounds/robot_death.wav'),
            'game_over': self.load_sound('assets/sounds/game_over.wav')
        }

    def load_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            print(f"Warning: Could not load sound {path}")
            return None

    def play(self, sound_name, volume=0.5):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.set_volume(volume)
            sound.play()