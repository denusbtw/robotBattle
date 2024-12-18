import pygame

from start_menu import StartMenu


def test_initialization():
    screen = pygame.display.set_mode((800, 600))
    menu = StartMenu(screen)
    assert menu.options == ["Easy", "Normal", "Hard"]
    assert menu.selected_index == 0
    assert menu.WHITE == (255, 255, 255)


def test_render_menu(mocker):
    screen = mocker.Mock()
    screen.get_width.return_value = 800
    screen.get_height.return_value = 600
    menu = StartMenu(screen)
    menu.render_menu()
    screen.blit.assert_called()


def test_option_selection():
    screen = pygame.display.set_mode((800, 600))
    menu = StartMenu(screen)
    menu.selected_index = 1
    selected_option = menu.options[menu.selected_index].lower()
    assert selected_option == "normal"

