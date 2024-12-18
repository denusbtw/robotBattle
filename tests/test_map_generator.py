import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../ext")))

import map_generator_ext


def test_generate_map():
    config = map_generator_ext.ConfigData()
    config.rows = 10
    config.cols = 10
    config.default_textures = [0, 1]
    config.player_pos = (0, 0)
    config.exit_pos = (9, 9)
    config.clefts_coeff = 0.1
    config.initial_robots_coeff = 0.05
    config.charges_coeff = 0.03
    config.key_coefficient = 0.02
    config.cleft_char = 'C'
    config.robot_char = 'R'
    config.charge_char = 'G'
    config.key_char = 'K'
    config.player_char = 'P'
    config.exit_char = 'E'

    game_map = map_generator_ext.generate_map(config)

    assert len(game_map) == config.rows, "Invalid rows count"
    assert len(game_map[0]) == config.cols, "Invalid columns count"

    for row in game_map:
        print(" ".join(row))

    assert any('P' in row for row in game_map), "No player on map"
    assert any('E' in row for row in game_map), "No exit on map"


def count_objects(game_map, obj_char):
    return sum(row.count(obj_char) for row in game_map)


def test_object_quantities():
    config = map_generator_ext.ConfigData()
    config.rows = 20
    config.cols = 20
    config.default_textures = [0, 1]
    config.player_pos = (0, 0)
    config.exit_pos = (19, 19)
    config.clefts_coeff = 0.1
    config.initial_robots_coeff = 0.05
    config.charges_coeff = 0.03
    config.key_coefficient = 3 / config.rows / config.cols
    config.cleft_char = 'C'
    config.robot_char = 'R'
    config.charge_char = 'G'
    config.key_char = 'K'
    config.player_char = 'P'
    config.exit_char = 'E'

    game_map = map_generator_ext.generate_map(config)

    total_cells = config.rows * config.cols

    expected_clefts = round(total_cells * config.clefts_coeff)
    expected_robots = round(total_cells * config.initial_robots_coeff)
    expected_charges = round(total_cells * config.charges_coeff)
    expected_keys = round(total_cells * config.key_coefficient)

    cleft_count = count_objects(game_map, config.cleft_char)
    robot_count = count_objects(game_map, config.robot_char)
    charge_count = count_objects(game_map, config.charge_char)
    key_count = count_objects(game_map, config.key_char)

    print(f"Expected clefts: {expected_clefts}, Actual: {cleft_count}")
    print(f"Expected robots: {expected_robots}, Actual: {robot_count}")
    print(f"Expected charges: {expected_charges}, Actual: {charge_count}")
    print(f"Expected keys: {expected_keys}, Actual: {key_count}")

    assert abs(cleft_count - expected_clefts) <= 1, f"Expected ~{expected_clefts} clefts, got {cleft_count}"
    assert abs(robot_count - expected_robots) <= 1, f"Expected ~{expected_robots} robots, got {robot_count}"
    assert abs(charge_count - expected_charges) <= 1, f"Expected ~{expected_charges} charges, got {charge_count}"
    assert abs(key_count - expected_keys) <= 1, f"Expected ~{expected_keys} keys, got {key_count}"


if __name__ == "__main__":
    test_generate_map()
