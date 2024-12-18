#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <tuple>
#include <set>

namespace py = pybind11;

bool is_valid_move(int x, int y, const std::vector<std::vector<std::string>>& game_map) {
    int rows = game_map.size();
    int cols = rows > 0 ? game_map[0].size() : 0;
    return x >= 0 && x < rows && y >= 0 && y < cols;
}

std::vector<std::tuple<int, int>> get_movable_cells(int player_x, int player_y, const std::vector<std::vector<std::string>>& game_map) {
    std::vector<std::tuple<int, int>> cells;
    for (int dx = -1; dx <= 1; ++dx) {
        for (int dy = -1; dy <= 1; ++dy) {
            int new_x = player_x + dx;
            int new_y = player_y + dy;
            if (is_valid_move(new_x, new_y, game_map)) {
                cells.emplace_back(new_x, new_y);
            }
        }
    }
    return cells;
}

std::string move_player(int& player_x, int& player_y, int target_x, int target_y,
                        const std::vector<std::tuple<int, int>>& robots,
                        std::vector<std::tuple<int, int>>& charges,
                        std::vector<std::tuple<int, int>>& keys,
                        const std::vector<std::vector<std::string>>& game_map,
                        int& player_charges, int max_charges, int& player_keys) {
    player_x = target_x;
    player_y = target_y;

    for (const auto& robot : robots) {
        if (player_x == std::get<0>(robot) && player_y == std::get<1>(robot)) {
            return "robot";
        }
    }

    if (game_map[player_x][player_y] == "C") {
        return "cleft";
    }

    for (auto it = charges.begin(); it != charges.end();) {
        if (player_x == std::get<0>(*it) && player_y == std::get<1>(*it) && player_charges < max_charges) {
            ++player_charges;
            it = charges.erase(it);
        } else {
            ++it;
        }
    }

    for (auto it = keys.begin(); it != keys.end();) {
        if (player_x == std::get<0>(*it) && player_y == std::get<1>(*it)) {
            ++player_keys;
            it = keys.erase(it);
        } else {
            ++it;
        }
    }

    return "safe";
}

PYBIND11_MODULE(player_core_ext, m) {
    m.def("is_valid_move", &is_valid_move, "Check if the move is valid",
          py::arg("x"), py::arg("y"), py::arg("game_map"));

    m.def("get_movable_cells", &get_movable_cells, "Get the list of valid cells the player can move to",
          py::arg("player_x"), py::arg("player_y"), py::arg("game_map"));

    m.def("move_player", &move_player, "Move the player and handle interactions",
          py::arg("player_x"), py::arg("player_y"), py::arg("target_x"), py::arg("target_y"),
          py::arg("robots"), py::arg("charges"), py::arg("keys"), py::arg("game_map"),
          py::arg("player_charges"), py::arg("max_charges"), py::arg("player_keys"));
}
