import os
import sys
from typing import Optional, Any

import numpy as np
import pygame
from pygame import Surface, Rect

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "ext")))
import game_over_screen_ext

from sound_manager import SoundManager


class GameOverScreen:
    def __init__(self,
                 screen_size: tuple[int, int],
                 captured_screen: Optional[pygame.Surface] = None
                 ) -> None:
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(screen_size)
        self.sound_manager = SoundManager()
        pygame.display.set_caption('Game Over')

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (220, 20, 60)
        self.BLOOD_RED = (136, 8, 8)
        self.GREEN = (0, 255, 0)
        self.DARK_GREEN = (0, 127, 0)

        try:
            font_path = os.path.join('assets', 'fonts', 'PressStart2P-Regular.ttf')
            self.font_large = pygame.font.Font(font_path, 50)
            self.font_small = pygame.font.Font(font_path, 20)
        except Exception:
            self.font_large = pygame.font.SysFont('arial', 74)
            self.font_small = pygame.font.SysFont('arial', 36)

        self.screen_width, self.screen_height = screen_size

        self.blurred_background = self.create_blurred_background(captured_screen)

    def create_blurred_background(self, captured_screen: pygame.Surface) -> pygame.Surface:
        if captured_screen is None:
            raise ValueError("Captured screen is None. Ensure a valid screen surface is passed.")

        screen_array = pygame.surfarray.array3d(captured_screen)

        image_list = screen_array.tolist()

        blurred_list = game_over_screen_ext.apply_gaussian_blur(image_list, sigma=2)
        blurred_array = np.array(blurred_list, dtype=np.uint8)
        blurred_surface = pygame.surfarray.make_surface(blurred_array)

        return pygame.transform.scale(blurred_surface, (self.screen_width, self.screen_height))

    def render_text_with_stroke(self,
                                text: str,
                                font: pygame.font.Font,
                                color: tuple[int, int, int],
                                stroke_color: tuple[int, int, int],
                                center: tuple[int, int]
                                ) -> tuple[Surface, Rect]:
        text_surface = font.render(text, True, color)

        outline_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)]:
            offset_surface = font.render(text, True, stroke_color)
            outline_surface.blit(offset_surface, (dx + 2, dy + 2))

        outline_surface.blit(text_surface, (2, 2))

        rect = outline_surface.get_rect(center=center)
        return outline_surface, rect

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> Any:
        font_width = font.size(' ')[0]

        lines = game_over_screen_ext.wrap_text(text, max_width, font_width)
        return lines

    def show(self, reason: str, message: str) -> str | None:
        if self.sound_manager:
            self.sound_manager.play('game_over')

        font_size = 10
        max_font_size = 50
        font_growth_rate = 1

        running = True
        while running:
            if self.blurred_background:
                self.screen.blit(self.blurred_background, (0, 0))
            else:
                self.screen.fill(self.BLACK)

            if font_size < max_font_size:
                font_size += font_growth_rate

            if reason == 'win':
                title = "VICTORY!"
                title_color = self.GREEN
                stroke_color = self.DARK_GREEN
            else:
                title = "GAME OVER"
                title_color = self.RED
                stroke_color = self.BLOOD_RED

            temp_font = pygame.font.Font(os.path.join('assets', 'fonts', 'PressStart2P-Regular.ttf'), font_size)

            game_over_surface, game_over_rect = self.render_text_with_stroke(
                title, temp_font, title_color, stroke_color,
                (self.screen_width // 2, self.screen_height // 2 - 100)
            )
            self.screen.blit(game_over_surface, game_over_rect)

            if message and font_size >= max_font_size:
                message_lines = self.wrap_text(message, self.font_small, self.screen_width - 40)
                message_y = self.screen_height // 2 - 20
                for line in message_lines:
                    reason_surface, reason_rect = self.render_text_with_stroke(
                        line, self.font_small, self.WHITE, self.BLACK,
                        (self.screen_width // 2, message_y)
                    )
                    self.screen.blit(reason_surface, reason_rect)
                    message_y += 30

            if font_size >= max_font_size:
                restart_surface, restart_rect = self.render_text_with_stroke(
                    'Press R to Restart or ESC to Quit', self.font_small, self.WHITE, self.BLACK,
                    (self.screen_width // 2, self.screen_height // 2 + 100)
                )
                self.screen.blit(restart_surface, restart_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return 'restart'
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

            pygame.time.Clock().tick(24)
