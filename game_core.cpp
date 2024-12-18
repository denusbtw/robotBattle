#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <utility>
#include <map>
#include <random>

namespace py = pybind11;

std::pair<int, int> get_cell_from_mouse(int x, int y, int cell_size) {
    int row = y / cell_size;
    int col = x / cell_size;
    return {row, col};
}

bool check_for_cleft(const std::vector<std::vector<std::string>>& game_map, int player_x, int player_y) {
    if (player_x < 0 || player_x >= static_cast<int>(game_map.size()) ||
        player_y < 0 || player_y >= static_cast<int>(game_map[0].size())) {
        throw std::out_of_range("Player position out of game map bounds.");
    }

    return game_map[player_x][player_y] == "C";
}

std::string select_death_message(const std::string& reason) {
    static const std::map<std::string, std::vector<std::string>> messages = {
        {"robot", {
            "A robot intercepted you! Your journey ends here.",
            "The cold steel of the robot crushed your dreams.",
            "A robot caught you off guard.",
            "You were overrun by the relentless robot swarm.",
            "A robot's trap has sealed your fate.",
            "You’ve been terminated by a robot’s relentless pursuit.",
            "A robot found you in its crosshairs. Mission failed.",
            "The robotic menace outmaneuvered you. Try again!",
            "A robot has eliminated you. Be more cautious next time.",
            "A machine’s unyielding grip has ended your quest."
        }},
        {"cleft", {
            "You stepped into the abyss. Watch your step next time!",
            "The ground gave way beneath you.",
            "You fell into a dark cleft. Beware of the terrain!",
            "The unforgiving chasm has claimed your life!",
            "A single misstep, and now you’re lost in the void.",
            "The cleft swallowed you whole.",
            "The treacherous terrain caught you off guard.",
            "You plummeted into the unknown depths. Be more vigilant!",
            "The cleft was waiting, and you walked right into it.",
            "Your careless steps led you into the abyss."
        }}
    };

    auto it = messages.find(reason);
    if (it == messages.end()) {
        throw std::invalid_argument("Invalid reason for death: " + reason);
    }

    const auto& reason_messages = it->second;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, reason_messages.size() - 1);
    return reason_messages[dis(gen)];
}

bool check_for_collision(int player_x, int player_y, const std::vector<std::tuple<int, int>>& robots) {
    for (const auto& robot : robots) {
        int robot_x, robot_y;
        std::tie(robot_x, robot_y) = robot;

        if (player_x == robot_x && player_y == robot_y) {
            return true;
        }
    }
    return false;
}


std::tuple<std::vector<std::tuple<int, int>>,
           std::vector<std::tuple<int, int>>,
           std::vector<std::tuple<int, int>>,
           std::tuple<int, int>>
convert_map(const std::vector<std::vector<std::string>>& game_map) {
    std::vector<std::tuple<int, int>> robots;
    std::vector<std::tuple<int, int>> charges;
    std::vector<std::tuple<int, int>> keys;
    std::tuple<int, int> player = {-1, -1};

    for (size_t x = 0; x < game_map.size(); ++x) {
        for (size_t y = 0; y < game_map[x].size(); ++y) {
            const std::string& cell = game_map[x][y];
            if (cell == "R") {
                robots.emplace_back(static_cast<int>(x), static_cast<int>(y));
            } else if (cell == "G") {
                charges.emplace_back(static_cast<int>(x), static_cast<int>(y));
            } else if (cell == "K") {
                keys.emplace_back(static_cast<int>(x), static_cast<int>(y));
            } else if (cell == "P") {
                player = {static_cast<int>(x), static_cast<int>(y)};
            }
        }
    }

    return {robots, charges, keys, player};
}



PYBIND11_MODULE(game_core_ext, m) {
    m.def("get_cell_from_mouse", &get_cell_from_mouse, "Convert mouse position to grid cell",
          py::arg("x"), py::arg("y"), py::arg("cell_size"));

    m.def("check_for_cleft", &check_for_cleft, "Check if player is on a cleft",
          py::arg("game_map"), py::arg("player_x"), py::arg("player_y"));

    m.def("select_death_message", &select_death_message, "Select a random death message based on the reason",
          py::arg("reason"));

    m.def("check_for_collision", &check_for_collision, "Check if player collided with a robot",
          py::arg("player_x"), py::arg("player_y"), py::arg("robots"));

    m.def("convert_map", &convert_map, "Convert the game map into structured objects",
          py::arg("game_map"));
}