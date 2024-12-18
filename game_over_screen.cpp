#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <sstream>
#include <cmath>

namespace py = pybind11;

std::vector<std::string> wrap_text(const std::string& text, size_t max_width, size_t font_width) {
    std::istringstream words(text);
    std::string word;
    std::vector<std::string> lines;
    std::string current_line;

    while (words >> word) {
        if (current_line.length() + word.length() + 1 <= max_width / font_width) {
            if (!current_line.empty()) current_line += " ";
            current_line += word;
        } else {
            lines.push_back(current_line);
            current_line = word;
        }
    }
    if (!current_line.empty()) lines.push_back(current_line);
    return lines;
}



std::vector<std::vector<std::vector<int>>> apply_gaussian_blur(
    const std::vector<std::vector<std::vector<int>>>& image, double sigma) {

    int height = image.size();
    int width = image[0].size();
    int kernel_radius = std::ceil(3 * sigma);

    std::vector<std::vector<std::vector<int>>> blurred_image(height, std::vector<std::vector<int>>(width, {0, 0, 0}));

    std::vector<double> kernel(2 * kernel_radius + 1);
    double sum = 0.0;
    for (int i = -kernel_radius; i <= kernel_radius; ++i) {
        kernel[i + kernel_radius] = std::exp(-0.5 * (i * i) / (sigma * sigma));
        sum += kernel[i + kernel_radius];
    }
    for (auto& k : kernel) k /= sum;

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            std::vector<double> temp(3, 0.0);
            for (int i = -kernel_radius; i <= kernel_radius; ++i) {
                int ny = std::clamp(y + i, 0, height - 1);
                for (int c = 0; c < 3; ++c) {
                    temp[c] += image[ny][x][c] * kernel[i + kernel_radius];
                }
            }
            for (int c = 0; c < 3; ++c) {
                blurred_image[y][x][c] = static_cast<int>(temp[c]);
            }
        }
    }

    return blurred_image;
}


PYBIND11_MODULE(game_over_screen_ext, m) {
    m.def("wrap_text", &wrap_text, "Wrap text to fit within a specified width",
          py::arg("text"), py::arg("max_width"), py::arg("font_width"));

    m.def("apply_gaussian_blur", &apply_gaussian_blur, "Apply Gaussian blur to an image",
          py::arg("image"), py::arg("sigma"));
}
