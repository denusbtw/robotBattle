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
        """Extract a single frame from the sprite sheet."""
        # Create a surface to hold the single frame
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)

        # Blit only the requested frame from the sprite sheet onto the new surface
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

        self.image = self.sprite_sheet.get_frame(0, 0, frame_width, frame_height)
        self.rect = self.image.get_rect(topleft=(start_x, start_y))
        self.pos = pygame.math.Vector2(start_x, start_y)

        self.speed = speed

        self.current_frame = 0
        self.animation_speed = 0.2
        self.current_frames = self.walk_left_frames
        self.direction = 'right'
        self.is_dead = False

    def update(self, player, other_robots):
        if self.is_dead:
            self.animate_death()
            return

        # Calculate direction towards player
        direction_vector = pygame.math.Vector2(player.pos - self.pos).normalize()
        dx, dy = direction_vector.x, direction_vector.y

        # Determine the new position
        new_pos = self.pos + direction_vector * self.speed

        # Check for interception
        if not self.is_overlapping(player, new_pos, other_robots):
            self.pos = new_pos
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        # Set walking frames based on direction
        self.set_walking_frames(dx, dy)

        # Animate the robot
        self.animate()

    def set_walking_frames(self, dx, dy):
        """Set walking frames based on the movement direction."""
        if abs(dx) > abs(dy):  # Horizontal movement
            if dx > 0:
                self.current_frames = self.walk_right_frames
                self.direction = 'right'
            else:
                self.current_frames = self.walk_left_frames
                self.direction = 'left'
        # else:  # Vertical movement
            # if dy > 0:
            #     self.current_frames = self.walk_down_frames
            #     self.direction = 'down'
            # else:
            #     self.current_frames = self.walk_up_frames
            #     self.direction = 'up'

    def animate(self):
        """Handle animation frame updates."""
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.current_frames):
            self.current_frame = 0
        self.image = self.current_frames[int(self.current_frame)]

    def take_damage(self):
        """Trigger death animation."""
        self.is_dead = True
        self.current_frame = 0
        self.current_frames = self.death_frames

    def animate_death(self):
        """Animate the robot's death."""
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.current_frames):
            self.current_frame = len(self.current_frames) - 1  # Stop at the last frame
        self.image = self.current_frames[int(self.current_frame)]

    def is_overlapping(self, player, new_pos, other_robots):
        robot_rect = self.rect.copy()
        robot_rect.topleft = (int(new_pos.x), int(new_pos.y))

        print(f"Robot Rect: {robot_rect}, Player Rect: {player.rect}")

        # Check collision with player
        if robot_rect.colliderect(player.rect):
            print(f"Collision detected with player at Robot: {robot_rect}, Player: {player.rect}")
            return True

        # Check collision with other robots
        for robot in other_robots:
            if robot is not self and robot.rect.colliderect(robot_rect):
                print(f"Collision detected with robot {id(robot)} at Robot: {robot_rect}, Other Robot: {robot.rect}")
                return True

        return False


class Robot1(Robot):
    def __init__(self, sprite_sheet_path, start_x, start_y):
        super().__init__(sprite_sheet_path, start_x, start_y, FRAME_WIDTH, FRAME_HEIGHT, speed=2)

    @cached_property
    def walk_left_frames(self):
        return self.sprite_sheet.get_row(0, 4, FRAME_WIDTH, FRAME_HEIGHT)

    @cached_property
    def walk_right_frames(self):
        return self.sprite_sheet.get_row(1, 4, FRAME_WIDTH, FRAME_HEIGHT)


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Battle")
    clock = pygame.time.Clock()

    player = Player('assets/player.png', 640, 360, FRAME_WIDTH, FRAME_HEIGHT)

    robots = pygame.sprite.Group()
    robot1 = Robot1('assets/Robot1.png', 100, 100)
    robots.add(robot1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)

        for robot in robots:
            robot.update(player, robots)

        screen.fill((0, 0, 0))
        screen.blit(player.image, player.pos)
        robots.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)