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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=5):
        super().__init__()
        self.image = pygame.Surface((10, 5))  # Example size
        self.image.fill((255, 0, 0))  # Red bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed

    def update(self):
        """Move the bullet."""
        if self.direction == 'right':
            self.rect.x += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed

        # Remove the bullet if it goes off-screen
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


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

        self.is_firing = False
        self.fire_animation_completed = False

        self.lives = 6
        self.is_dead = False

    def move(self, dx, dy):
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        new_pos = self.pos + pygame.math.Vector2(dx, dy)

        if (0 <= new_pos.x < (WIDTH-self.frame_width)) and (0 <= new_pos.y <= (HEIGHT-self.frame_height)):
            self.pos = new_pos
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def update(self, keys):
        if self.is_dead:
            self.animate_death()
            return

        dx, dy = 0, 0

        if not self.is_firing:
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
            else:
                match self.direction:
                    case 'up': self.image = self.walk_up_frames[0]
                    case 'down': self.image = self.walk_down_frames[0]
                    case 'left': self.image = self.walk_left_frames[0]
                    case 'right': self.image = self.walk_right_frames[0]
                    case _: self.image = self.default_idle_frame

            if dx != 0 or dy != 0:
                self.move(dx, dy)
                self.animate()
        else:
            self.animate()

        if keys[pygame.K_SPACE] and not self.is_firing:
            bullet = Bullet(player.rect.centerx, player.rect.centery, player.direction)
            bullets.add(bullet)
            self.start_firing_animation()

    def take_damage(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.start_death_animation()

    def start_death_animation(self):
        self.is_dead = True
        self.current_frame = 0
        match self.direction:
            case 'right': self.current_frames = self.die_right_frames
            case _: self.current_frames = self.die_left_frames

    def animate_death(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.current_frames):
            self.current_frame = len(self.current_frames) - 1

        self.image = self.current_frames[int(self.current_frame)]

    def start_firing_animation(self):
        self.is_firing = True
        self.current_frame = 0
        match self.direction:
            case 'up': self.current_frames = self.fire_up_frames
            case 'down': self.current_frames = self.fire_down_frames
            case 'left': self.current_frames = self.fire_left_frames
            case 'right': self.current_frames = self.fire_right_frames

    def animate(self):
        self.current_frame += max(0.1, 1 / self.speed)
        if self.current_frame >= len(self.current_frames):
            self.current_frame = 0
            if self.is_firing:
                self.is_firing = False

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

    @cached_property
    def fire_up_frames(self):
        return self.sprite_sheet.get_row(4, 2, self.frame_width, self.frame_height)

    @cached_property
    def fire_right_frames(self):
        return self.sprite_sheet.get_row(5, 2, self.frame_width, self.frame_height)

    @cached_property
    def fire_down_frames(self):
        return self.sprite_sheet.get_row(6, 2, self.frame_width, self.frame_height)

    @cached_property
    def fire_left_frames(self):
        return self.sprite_sheet.get_row(7, 2, self.frame_width, self.frame_height)

    @cached_property
    def die_right_frames(self):
        return self.sprite_sheet.get_row(8, 6, self.frame_width, self.frame_height)

    @cached_property
    def die_left_frames(self):
        return self.sprite_sheet.get_row(9, 6, self.frame_width, self.frame_height)


class Robot(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet_path, start_x, start_y, frame_width, frame_height, speed):
        super().__init__()
        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Initialize the robot's image and position
        self.image = self.sprite_sheet.get_frame(0, 0, frame_width, frame_height)
        self.rect = self.image.get_rect(topleft=(start_x, start_y))
        self.pos = pygame.math.Vector2(start_x, start_y)

        # Movement and animation settings
        self.speed = speed
        self.current_frame = 0
        self.animation_speed = 0.2
        self.current_frames = self.walk_right_frames  # Default walking animation
        self.direction = 'right'  # Default direction

        # State flags
        self.is_dead = False

    def update(self, player, bullets, other_robots):
        """Update the robot's state each frame."""
        if self.is_dead:
            self.animate_death()
            return

        # Move the robot towards the player
        direction_vector = pygame.math.Vector2(player.pos - self.pos).normalize()
        dx, _ = direction_vector.x, direction_vector.y  # Only horizontal movement matters
        new_pos = self.pos + direction_vector * self.speed

        if not self.is_overlapping(player, new_pos, other_robots):
            self.pos = new_pos
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        self.update_walking_frames(dx)
        self.animate()

    def update_walking_frames(self, dx):
        """Update walking frames based on movement direction."""
        if dx > 0:
            self.direction = 'right'
            self.current_frames = self.walk_right_frames
        elif dx < 0:
            self.direction = 'left'
            self.current_frames = self.walk_left_frames

    def animate(self):
        """Handle animation frame updates."""
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.current_frames):
            self.current_frame = 0
        self.image = self.current_frames[int(self.current_frame)]

    def animate_death(self):
        """Animate the robot's death."""
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.current_frames):
            self.current_frame = len(self.current_frames) - 1  # Stop at the last frame
        self.image = self.current_frames[int(self.current_frame)]

    def is_overlapping(self, player, new_pos, other_robots):
        """Check for collisions with the player and other robots."""
        robot_rect = self.rect.copy()
        robot_rect.topleft = (int(new_pos.x), int(new_pos.y))

        # Check collision with player
        if robot_rect.colliderect(player.rect):
            return True

        # Check collision with other robots
        for robot in other_robots:
            if robot is not self and robot.rect.colliderect(robot_rect):
                return True

        return False

    @cached_property
    def walk_left_frames(self):
        """Retrieve walking frames for moving left."""
        return self.sprite_sheet.get_row(0, 4, self.frame_width, self.frame_height)

    @cached_property
    def walk_right_frames(self):
        """Retrieve walking frames for moving right."""
        return [pygame.transform.flip(frame, True, False) for frame in self.walk_left_frames]

    @cached_property
    def death_frames(self):
        """Retrieve death animation frames."""
        return self.sprite_sheet.get_row(3, 3, self.frame_width, self.frame_height)


class Robot1(Robot):
    def __init__(self, sprite_sheet_path, start_x, start_y):
        super().__init__(sprite_sheet_path, start_x, start_y, FRAME_WIDTH, FRAME_HEIGHT, speed=2)


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Battle")
    clock = pygame.time.Clock()

    bullets = pygame.sprite.Group()
    player = Player('assets/player.png', 640, 360, FRAME_WIDTH, FRAME_HEIGHT)

    robots = pygame.sprite.Group()
    robot1 = Robot1('assets/robot1.png', 100, 100)
    robots.add(robot1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)

        for robot in robots:
            robot.update(player, bullets, robots)

        screen.fill((0, 0, 0))
        screen.blit(player.image, player.pos)
        robots.draw(screen)

        bullets.update()
        bullets.draw(screen)

        pygame.display.flip()

        clock.tick(FPS)