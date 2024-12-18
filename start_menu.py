import os
import sys

import pygame

from sound_manager import SoundManager


class StartMenu:
    def __init__(self, screen: pygame.Surface):
        pygame.init()
        pygame.font.init()

        self.screen = screen

        try:
            self.background_image = pygame.image.load('assets/background.png').convert()
            self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())
        except Exception:
            self.background_image = pygame.Surface(self.screen.get_size())
            self.background_image.fill((0, 0, 0))

        self.sound_manager = SoundManager()

        self.WHITE = (255, 255, 255)
        self.HIGHLIGHT = (255, 223, 0)

        try:
            font_path = os.path.join('assets', 'fonts', 'PressStart2P-Regular.ttf')
            self.title_font = pygame.font.Font(font_path, 40)
            self.option_font = pygame.font.Font(font_path, 30)
        except Exception:
            self.title_font = pygame.font.SysFont('arial', 40)
            self.option_font = pygame.font.SysFont('arial', 30)

        self.options = ["Easy", "Normal", "Hard"]
        self.selected_index = 0

    def render_menu(self) -> None:
        self.screen.blit(self.background_image, (0, 0))

        title_text = self.title_font.render("Select Difficulty", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_text, title_rect)

        for index, option in enumerate(self.options):
            color = self.HIGHLIGHT if index == self.selected_index else self.WHITE
            option_text = self.option_font.render(f"• {option}", True, color)
            option_rect = option_text.get_rect(center=(self.screen.get_width() // 2, 250 + index * 50))
            self.screen.blit(option_text, option_rect)

        pygame.display.flip()

    def run(self) -> str:
        running = True

        while running:
            self.render_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    self.sound_manager.play('click', 0.1)
                    match event.key:
                        case pygame.K_UP: self.selected_index = (self.selected_index - 1) % len(self.options)
                        case pygame.K_DOWN: self.selected_index = (self.selected_index + 1) % len(self.options)
                        case pygame.K_RETURN: return self.options[self.selected_index].lower()

            pygame.time.Clock().tick(30)