#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <random>
#include <vector>
#include <utility>
#include <string>
#include <cctype>
#include <algorithm>


namespace py = pybind11;

struct ConfigData {
    int rows;
    int cols;
    std::vector<int> default_textures;
    std::pair<int, int> player_pos;
    std::pair<int, int> exit_pos;
    double clefts_coeff;
    double initial_robots_coeff;
    double charges_coeff;
    double key_coefficient;
    int number_of_keys;
    char cleft_char;
    char robot_char;
    char charge_char;
    char key_char;
    char player_char;
    char exit_char;
};

class MapGenerator {
public:
    static std::vector<std::vector<std::string>> generate_map(const ConfigData &cfg) {
        std::vector<std::vector<std::string>> game_map(cfg.rows, std::vector<std::string>(cfg.cols, " "));

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> distr(0, (int)cfg.default_textures.size() - 1);

        for (int x = 0; x < cfg.rows; ++x) {
            for (int y = 0; y < cfg.cols; ++y) {
                int tex = cfg.default_textures[distr(gen)];
                game_map[x][y] = std::to_string(tex);
            }
        }

        init_object(cfg, game_map, std::string(1, cfg.cleft_char), cfg.clefts_coeff, true);
        init_object(cfg, game_map, std::string(1, cfg.robot_char), cfg.initial_robots_coeff);
        init_object(cfg, game_map, std::string(1, cfg.charge_char), cfg.charges_coeff);
        init_object(cfg, game_map, std::string(1, cfg.key_char), cfg.key_coefficient);

        game_map[cfg.player_pos.first][cfg.player_pos.second] = std::string(1, cfg.player_char);
        game_map[cfg.exit_pos.first][cfg.exit_pos.second] = std::string(1, cfg.exit_char);

        return game_map;
    }


static void init_object(const ConfigData &cfg, std::vector<std::vector<std::string>> &game_map, const std::string &obj, double coeff, bool check_cleft_spawn = false) {
    int total_objects = static_cast<int>(std::round(cfg.rows * cfg.cols * coeff));

    std::vector<std::pair<int, int>> empty_positions;
    for (int x = 0; x < cfg.rows; ++x) {
        for (int y = 0; y < cfg.cols; ++y) {
            if (is_numeric(game_map[x][y])) {
                if (check_cleft_spawn && obj == std::string(1, cfg.cleft_char) && !can_cleft_spawn(cfg, x, y)) {
                    continue;
                }
                empty_positions.emplace_back(x, y);
            }
        }
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::shuffle(empty_positions.begin(), empty_positions.end(), gen);

    for (int i = 0; i < std::min(total_objects, static_cast<int>(empty_positions.size())); ++i) {
        int x = empty_positions[i].first;
        int y = empty_positions[i].second;
        game_map[x][y] = obj;
    }
}


    static bool can_cleft_spawn(const ConfigData &cfg, int x, int y) {
        std::vector<std::pair<int, int>> danger_zone = {
            {cfg.rows / 2 - 1, 0}, {cfg.rows / 2 - 1, 1},
            {cfg.rows / 2 + 1, 0}, {cfg.rows / 2 + 1, 1},
            {cfg.rows / 2, 1},
            {cfg.rows / 2 - 1, cfg.cols - 1}, {cfg.rows / 2 - 1, cfg.cols - 2},
            {cfg.rows / 2 + 1, cfg.cols - 1}, {cfg.rows / 2 + 1, cfg.cols - 2},
            {cfg.rows / 2, cfg.cols - 2}
        };

        for (const auto &dz : danger_zone) {
            if (dz.first == x && dz.second == y) {
                return false;
            }
        }
        return true;
    }

    static bool is_numeric(const std::string &s) {
        return !s.empty() && std::all_of(s.begin(), s.end(), ::isdigit);
    }
};

PYBIND11_MODULE(map_generator_ext, m) {
    py::class_<ConfigData>(m, "ConfigData")
        .def(py::init<>())
        .def_readwrite("rows", &ConfigData::rows)
        .def_readwrite("cols", &ConfigData::cols)
        .def_readwrite("default_textures", &ConfigData::default_textures)
        .def_readwrite("player_pos", &ConfigData::player_pos)
        .def_readwrite("exit_pos", &ConfigData::exit_pos)
        .def_readwrite("clefts_coeff", &ConfigData::clefts_coeff)
        .def_readwrite("initial_robots_coeff", &ConfigData::initial_robots_coeff)
        .def_readwrite("charges_coeff", &ConfigData::charges_coeff)
        .def_readwrite("key_coefficient", &ConfigData::key_coefficient)
        .def_readwrite("number_of_keys", &ConfigData::number_of_keys)
        .def_readwrite("cleft_char", &ConfigData::cleft_char)
        .def_readwrite("robot_char", &ConfigData::robot_char)
        .def_readwrite("charge_char", &ConfigData::charge_char)
        .def_readwrite("key_char", &ConfigData::key_char)
        .def_readwrite("player_char", &ConfigData::player_char)
        .def_readwrite("exit_char", &ConfigData::exit_char);

    m.def("generate_map", &MapGenerator::generate_map, "Generate the game map");
}
