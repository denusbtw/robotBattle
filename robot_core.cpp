#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <utility>
#include <tuple>

namespace py = pybind11;

bool is_valid_move(int x, int y, const std::vector<std::vector<std::string>>& game_map) {
    int rows = game_map.size();
    int cols = game_map[0].size();
    return x >= 0 && x < rows && y >= 0 && y < cols;
}

std::pair<int, int> move_towards(
    int robot_x, int robot_y,
    int player_x, int player_y,
    const std::vector<std::vector<std::string>>& game_map
) {
    int dx = player_x - robot_x;
    int dy = player_y - robot_y;

    int new_x = robot_x, new_y = robot_y;

    if (abs(dx) > abs(dy)) {
        new_x = robot_x + (dx > 0 ? 1 : -1);
        if (!is_valid_move(new_x, robot_y, game_map)) {
            new_x = robot_x;
        }
    } else {
        new_y = robot_y + (dy > 0 ? 1 : -1);
        if (!is_valid_move(robot_x, new_y, game_map)) {
            new_y = robot_y;
        }
    }

    return {new_x, new_y};
}

bool is_dead(int x, int y, const std::vector<std::vector<std::string>>& game_map) {
    return game_map[x][y] == "C";
}

std::tuple<int, int, bool> update_robot(
    int robot_x, int robot_y,
    int player_x, int player_y,
    const std::vector<std::vector<std::string>>& game_map
) {
    auto [new_x, new_y] = move_towards(robot_x, robot_y, player_x, player_y, game_map);
    bool dead = is_dead(new_x, new_y, game_map);
    return {new_x, new_y, dead};
}

PYBIND11_MODULE(robot_core_ext, m) {
    m.def("move_towards", &move_towards, "Move robot one step toward the player",
          py::arg("robot_x"), py::arg("robot_y"), py::arg("player_x"), py::arg("player_y"), py::arg("game_map"));

    m.def("is_dead", &is_dead, "Check if the robot is dead (on a cleft)",
          py::arg("x"), py::arg("y"), py::arg("game_map"));

    m.def("update_robot", &update_robot, "Update robot state",
          py::arg("robot_x"), py::arg("robot_y"), py::arg("player_x"), py::arg("player_y"), py::arg("game_map"));
}
