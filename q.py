import pygame
import sys
import random

from PIL import Image, ImageDraw, ImageFont

# Constants
GRID_ROWS = 11
GRID_COLS = 18
CELL_SIZE = 50
SCREEN_WIDTH = CELL_SIZE * GRID_COLS
SCREEN_HEIGHT = CELL_SIZE * GRID_ROWS
PLAYER_COLOR = (0, 255, 0)
GRID_COLOR = (200, 200, 200)
STROKE_COLOR = (255, 255, 0)
HOLE_COLOR = (100, 100, 100)
ROBOT_COLOR = (255, 0, 0)
PING_COLOR = (0, 255, 255)
EXIT_COLOR = (0, 255, 0)
CHARGE_COLOR = (0, 0, 255)
KEY_COLOR = (255, 215, 0)
MAX_CHARGES = 3

# Map: 0 = walkable, 1 = hole
MAP = [
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

EXIT_POSITION = (GRID_ROWS // 2, 0)
PLAYER_POSITION = (GRID_ROWS // 2, GRID_COLS - 1)


# def add_frame_indices_to_sprite_sheet(input_path, output_path, frame_width, frame_height, font_path=None):
#     sprite_sheet = Image.open(input_path)
#     sheet_width, sheet_height = sprite_sheet.size
#
#     cols = sheet_width // frame_width
#     rows = sheet_height // frame_height
#
#     new_sheet = sprite_sheet.copy()
#     draw = ImageDraw.Draw(new_sheet)
#
#     if font_path:
#         font = ImageFont.truetype(font_path, frame_height // 4)
#     else:
#         font = ImageFont.load_default()
#
#     index = 0
#     for row in range(rows):
#         for col in range(cols):
#             x = col * frame_width
#             y = row * frame_height
#
#             text = str(index)
#             text_bbox = font.getbbox(text)
#             text_width = text_bbox[2] - text_bbox[0]
#             text_height = text_bbox[3] - text_bbox[1]
#             text_x = x + (frame_width - text_width) // 2
#             text_y = y + (frame_height - text_height) // 2
#
#             draw.text((text_x, text_y), text, fill="white", font=font)
#
#             index += 1
#
#     new_sheet.save(output_path)
#     print(f"Sprite sheet with indices saved to {output_path}")


# def generate_2d_map_from_sprite_sheet(sprite_sheet_path, frame_width, frame_height, map_data, output_path):
#     sprite_sheet = Image.open(sprite_sheet_path)
#     sheet_width, sheet_height = sprite_sheet.size
#
#     frames_per_row = sheet_width // frame_width
#
#     map_rows = len(map_data)
#     map_cols = len(map_data[0])
#     output_width = map_cols * frame_width
#     output_height = map_rows * frame_height
#
#     map_image = Image.new("RGBA", (output_width, output_height))
#
#     for row_index, row in enumerate(map_data):
#         for col_index, frame_index in enumerate(row):
#             frame_x = (frame_index % frames_per_row) * frame_width
#             frame_y = (frame_index // frames_per_row) * frame_height
#
#             frame = sprite_sheet.crop((frame_x, frame_y, frame_x + frame_width, frame_y + frame_height))
#
#             dest_x = col_index * frame_width
#             dest_y = row_index * frame_height
#             map_image.paste(frame, (dest_x, dest_y))
#
#     map_image.save(output_path)
#     print(f"2D map saved to {output_path}")


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.charges = MAX_CHARGES
        self.keys = 0

    def move_to(self, row, col, robots, charges, keys):
        self.x = row
        self.y = col
        # Check for collision with robots
        for robot in robots:
            if (self.x, self.y) == (robot.x, robot.y):
                return "robot"
        # Pick up charges
        if (self.x, self.y) in charges:
            if 0 <= self.charges < MAX_CHARGES:
                charges.remove((self.x, self.y))
                self.charges += 1
        # Pick up keys
        if (self.x, self.y) in keys:
            keys.remove((self.x, self.y))
            self.keys += 1
        return "safe"

    def is_dead(self):
        return MAP[self.x][self.y] == 1

    def get_movable_cells(self):
        cells = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                new_x = self.x + dx
                new_y = self.y + dy
                cells.append((new_x, new_y))
        return cells


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_pinged = False

    def move_towards(self, player):
        dx = player.x - self.x
        dy = player.y - self.y

        if abs(dx) > abs(dy):
            self.x += 1 if dx > 0 else -1
        else:
            self.y += 1 if dy > 0 else -1

    def is_dead(self):
        return MAP[self.x][self.y] == 1


def spawn_items(count, exclude_positions):
    items = []
    while len(items) < count:
        x = random.randint(0, GRID_ROWS - 1)
        y = random.randint(0, GRID_COLS - 1)
        if MAP[x][y] == 0 and (x, y) not in exclude_positions:
            items.append((x, y))
    return items


def draw_grid(screen):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if MAP[row][col] == 1:
                pygame.draw.rect(screen, HOLE_COLOR, rect)
            else:
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)


def draw_exit(screen):
    rect = pygame.Rect(
        EXIT_POSITION[1] * CELL_SIZE,
        EXIT_POSITION[0] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )
    pygame.draw.rect(screen, EXIT_COLOR, rect)


def draw_charges(screen, charges, charge_sprite):
    for x, y in charges:
        charge_rect = charge_sprite.get_rect(
            center=(
                y * CELL_SIZE + CELL_SIZE // 2,
                x * CELL_SIZE + CELL_SIZE // 2,
            )
        )
        screen.blit(charge_sprite, charge_rect)


def draw_keys(screen, keys, key_sprite):
    """Draw key sprites."""
    for x, y in keys:
        key_rect = key_sprite.get_rect(
            center=(
                y * CELL_SIZE + CELL_SIZE // 2,
                x * CELL_SIZE + CELL_SIZE // 2,
            )
        )
        screen.blit(key_sprite, key_rect)


def draw_highlight_stroke(screen, cells):
    for row, col in cells:
        rect = pygame.Rect(
            col * CELL_SIZE + 2, row * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4
        )
        pygame.draw.rect(screen, STROKE_COLOR, rect, width=2)


def draw_robots(screen, robots, robot_sprite):
    """Draw robot sprites."""
    for robot in robots:
        robot_rect = robot_sprite.get_rect(
            center=(
                robot.y * CELL_SIZE + CELL_SIZE // 2,
                robot.x * CELL_SIZE + CELL_SIZE // 2,
            )
        )
        color = PING_COLOR if robot.is_pinged else None  # Highlight if pinged
        screen.blit(robot_sprite, robot_rect)

        if color:  # Optional: Add a ping effect (stroke) if robot is pinged
            pygame.draw.ellipse(screen, color, robot_rect.inflate(-10, -10), width=2)


def draw_indicator(screen, player):
    font = pygame.font.SysFont(None, 36)
    text = font.render(
        f"Charges: {player.charges}/{MAX_CHARGES} Keys: {player.keys}/3",
        True,
        (255, 255, 255),
    )
    screen.blit(text, (10, 10))


def get_cell_from_mouse(pos):
    x, y = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    return row, col


def load_sprite(image_path, size):
    """Load and scale a sprite."""
    sprite = pygame.image.load(image_path).convert_alpha()
    return pygame.transform.scale(sprite, (size, size))

def draw_player(screen, player, player_sprite):
    """Draw the player sprite."""
    player_rect = player_sprite.get_rect(
        center=(
            player.y * CELL_SIZE + CELL_SIZE // 2,
            player.x * CELL_SIZE + CELL_SIZE // 2,
        )
    )
    screen.blit(player_sprite, player_rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Turn-Based Grid Movement with Exit")
    clock = pygame.time.Clock()

    player_sprite = load_sprite("assets/astronaut.png", CELL_SIZE)
    robot_sprite = load_sprite("assets/robot1.png", CELL_SIZE)
    key_sprite = load_sprite("assets/key.png", CELL_SIZE)
    charge_sprite = load_sprite('assets/charge.png', CELL_SIZE)
    player = Player(*PLAYER_POSITION)
    robots = [Robot(0, 0), Robot(10, 17), Robot(5, 5)]

    charges = spawn_items(5, [EXIT_POSITION, PLAYER_POSITION])
    keys = spawn_items(3, [EXIT_POSITION, PLAYER_POSITION] + charges)

    pinged_robots = []

    running = True
    player_turn = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                if event.button == 3:
                    if player.charges > 0:
                        row, col = get_cell_from_mouse(event.pos)
                        for robot in robots:
                            if (robot.x, robot.y) == (row, col):
                                robot.is_pinged = not robot.is_pinged
                                if robot.is_pinged:
                                    pinged_robots.append(robot)
                                    player.charges -= 1
                                else:
                                    pinged_robots.remove(robot)
                                    player.charges += 1
                elif event.button == 1:
                    row, col = get_cell_from_mouse(event.pos)
                    if pinged_robots:
                        if (row, col) in player.get_movable_cells():
                            move_result = player.move_to(row, col, robots, charges, keys)
                            if move_result == "robot":
                                print("Game Over! You moved into a robot.")
                                running = False
                            else:
                                robots = [robot for robot in robots if robot not in pinged_robots]
                                pinged_robots.clear()
                                player_turn = False
                    else:
                        if (row, col) in player.get_movable_cells():
                            move_result = player.move_to(row, col, robots, charges, keys)
                            if move_result == "robot":
                                print("Game Over! You moved into a robot.")
                                running = False
                            elif player.is_dead():
                                print("Game Over! You fell into a hole.")
                                running = False
                            else:
                                player_turn = False

        if player.x == EXIT_POSITION[0] and player.y == EXIT_POSITION[1]:
            if player.keys == 3:
                print("Victory! You collected all keys and reached the exit.")
                running = False
            else:
                print("You need all 3 keys to exit!")

        if not player_turn:
            for robot in robots:
                robot.move_towards(player)
            if any((robot.x, robot.y) == (player.x, player.y) for robot in robots):
                print("Game Over! A robot moved into your cell.")
                running = False
            robots = [robot for robot in robots if not robot.is_dead()]
            player_turn = True

        screen.fill((0, 0, 0))

        draw_grid(screen)
        draw_exit(screen)
        draw_charges(screen, charges, charge_sprite)
        draw_keys(screen, keys, key_sprite)

        draw_highlight_stroke(screen, player.get_movable_cells())

        draw_player(screen, player, player_sprite)  # Pass player sprite here
        draw_robots(screen, robots, robot_sprite)  # Pass robot sprite here

        draw_indicator(screen, player)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    # add_frame_indices_to_sprite_sheet(
    #     input_path="assets/cosmic_legacy.png",
    #     output_path="assets/cosmic_legacy_with_indices.png",
    #     frame_width=16,
    #     frame_height=16,
    #     font_path=None
    # )
    main()
