import math

import pygame
import sys
from functools import cached_property

from settings import *


class SpriteSheet:
    def __init__(self, filepath):
        self.sprite_sheet = pygame.image.load(filepath).convert_alpha()

    def get_row(self, row, cols, frame_width, frame_height):
        frames = []
        y = row * frame_height
        for col in range(cols):
            x = col * frame_width
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.sprite_sheet, (0, 0), pygame.Rect(x, y, frame_width, frame_height))
            frames.append(frame)
        return frames

    def get_frame(self, x, y, frame_width, frame_height):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), pygame.Rect(x, y, frame_width, frame_height))
        return frame

    def get_frames(self, rows ,cols, frame_width, frame_height):
        frames = []
        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frames.append(self.get_frame(x, y, frame_width, frame_height))
        return frames


class Player(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet_path, start_x, start_y, frame_width, frame_height):
        super().__init__()
        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.image = self.default_idle_frame
        self.rect = self.image.get_rect(topleft=(start_x, start_y))
        self.pos = pygame.math.Vector2(start_x, start_y)

        self.speed = PLAYER_DEFAULT_SPEED
        self.current_frame = 0
        self.animation_speed = 0.2
        self.current_frames = self.walk_down_frames
        self.direction = 'down'

    def move(self, dx, dy):
        if dx != 0 and dy != 0: # moving diagonally
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        new_pos = self.pos + pygame.math.Vector2(dx, dy)

        if (0 <= new_pos.x < (WIDTH-self.frame_width)) and (0 <= new_pos.y <= (HEIGHT-self.frame_height)):
            self.pos = new_pos

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = 'up'
            self.current_frames = self.walk_up_frames
        if keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = 'down'
            self.current_frames = self.walk_down_frames
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = 'left'
            self.current_frames = self.walk_left_frames
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = 'right'
            self.current_frames = self.walk_right_frames

        if dx != 0 or dy != 0:
            self.animate()
        else:
            match self.direction:
                case 'up': self.image = self.walk_up_frames[0]
                case 'down': self.image = self.walk_down_frames[0]
                case 'left': self.image = self.walk_left_frames[0]
                case 'right': self.image = self.walk_right_frames[0]
                case _: self.image = self.default_idle_frame

        self.move(dx, dy)

    def animate(self):
        animation_speed = max(0.1, 1 / self.speed)
        self.current_frame += animation_speed
        if self.current_frame >= len(self.current_frames):
            self.current_frame = 0
        self.image = self.current_frames[int(self.current_frame)]

    @property
    def default_idle_frame(self):
        return self.sprite_sheet.get_frame(0, 2 * self.frame_height, self.frame_width, self.frame_height)

    @cached_property
    def walk_up_frames(self):
        return self.sprite_sheet.get_row(0, 3, self.frame_width, self.frame_height)

    @cached_property
    def walk_left_frames(self):
        return self.sprite_sheet.get_row(1, 4, self.frame_width, self.frame_height)

    @cached_property
    def walk_down_frames(self):
        return self.sprite_sheet.get_row(2, 3, self.frame_width, self.frame_height)

    @cached_property
    def walk_right_frames(self):
        return self.sprite_sheet.get_row(3, 4, self.frame_width, self.frame_height)


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Battle")
    clock = pygame.time.Clock()

    player = Player('assets/player.png', 640, 360, FRAME_WIDTH, FRAME_HEIGHT)

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0,0,0))

        screen.blit(player.image, player.pos)
        player.update(keys)

        pygame.display.update()
        pygame.display.flip()
        clock.tick(FPS)