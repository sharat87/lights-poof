#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import sys
import time
import random
import pygame
from pygame.locals import QUIT, KEYUP, MOUSEBUTTONUP, MOUSEBUTTONDOWN

class App(object):

    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((320, 420))
        pygame.display.set_caption('Lights poof!')

        self.init_bg_surface()

        self.solver = Solver(self.display)
        self.solver.on_solver_done = self.on_solver_done

        self.init_new_game()

        self.menu = Menu(self.display)
        self.menu.on_resume_click = self.on_resume_click
        self.menu.on_new_click = self.on_new_click
        self.menu.on_solve_click = self.on_solve_click

        self.current_state = self.game

    def main_loop(self):

        while True:

            for event in pygame.event.get():
                self.handle(event)

            self.draw()
            time.sleep(.01)

    def draw(self):
        # Draw background.
        self.display.blit(self.bg_surface, (0, 0))

        # Draw the state.
        self.current_state.draw()

        # Update the display.
        pygame.display.update()

    def handle(self, event):

        if event.type == QUIT or (event.type == KEYUP and event.key == 27):
            pygame.quit()
            sys.exit()

        else:
            self.current_state.handle(event)

    def init_bg_surface(self):
        bg_image = pygame.image.load('bg.png')
        self.bg_surface = pygame.Surface(self.display.get_size())

        x = y = 0
        image_width, image_height = bg_image.get_size()
        bg_width, bg_height = self.display.get_size()

        while x < bg_width:
            y = 0

            while y < bg_height:
                self.bg_surface.blit(bg_image, (x, y))
                y += image_height

            x += image_width

    def init_new_game(self):
        self.game = Game(self.display)
        self.game.on_menu_click = self.on_menu_click

        self.solver.game = self.game

    def on_menu_click(self, event):
        self.current_state = self.menu

    def on_resume_click(self, event):
        self.current_state = self.game

    def on_new_click(self, event):
        self.init_new_game()
        self.current_state = self.game

    def on_solve_click(self, event):
        self.current_state = self.solver
        print(self.solver.game.solution)

    def on_solver_done(self):
        print('Solving complete')
        self.current_state = self.game


class Game(object):

    def __init__(self, display, level=None):

        self.display = display

        title_font = pygame.font.Font('Signika-Regular.ttf', 36)
        self.title_surface = title_font.render('Lights poof!', True,
                (213, 85, 148))
        self.title_rect = self.title_surface.get_rect()
        self.title_rect.centerx = self.display.get_width() / 2
        self.title_rect.top = 24

        self.game_size = 5
        self.light_size = 42
        self.light_gap = 6

        self.board_size = ((self.light_size + self.light_gap) * self.game_size
                - self.light_gap)

        self.board_x = (self.display.get_width() - self.board_size) / 2
        self.board_y = (self.display.get_height() - self.board_size) / 2

        self.board = [[Light(self.display) for _ in range(self.game_size)]
                for _ in range(self.game_size)]
        self.apply_level(level)
        self.update_light_positions()

        self.menu_btn = Button('Menu', centerx=self.display.get_width() / 2,
                y=self.board_y + self.board_size + 24)

        # Menu button click handler should be set from outside this class.
        self.menu_btn.on_click = self._on_menu_click
        self.on_menu_click = None

    def apply_level(self, level):

        # How many turns should the game be of?
        min_turns = self.game_size
        max_turns = self.game_size * 2
        turns = random.randint(min_turns, max_turns)

        # Create a list of all possible coordinates and select `turns` of them
        # in random.
        all_coordinates = [(i, j) for i in range(self.game_size)
                for j in range(self.game_size)]
        random.shuffle(all_coordinates)

        # They are also the solution of this game.
        self.solution = all_coordinates[:turns]

        # Toggle each of the selected coordinate.
        for i, j in self.solution:
            self.toggle(i, j)

    def draw(self):
        # Draw the title.
        self.display.blit(self.title_surface, self.title_rect)

        # Draw the lights.
        for row in self.board:
            for light in row:
                light.draw()

        # Draw the buttons.
        self.menu_btn.draw(self.display)

    def handle(self, event):

        # Pass to any components that might need it.
        self.menu_btn.handle(event)

        # Left click.
        if event.type == MOUSEBUTTONUP and event.button == 1:
            self.on_left_click(event)

    def update_light_positions(self):

        y = self.board_y
        for i, row in enumerate(self.board):
            x = self.board_x

            for j, light in enumerate(row):
                light.update_rect(x=x, y=y)
                x += self.light_size + self.light_gap

            y += self.light_size + self.light_gap

    def on_left_click(self, event):

        # Get the light's coordinates under the click, if any.
        light_pos = self.get_light_under_point(event.pos)

        # No light under the click. Do nothing.
        if light_pos is not None:

            # Toggle this light and all the lights that go with it.
            self.toggle(*light_pos)

            # Add/remove it to/from the solution.
            try:
                self.solution.remove(light_pos)
            except ValueError:
                self.solution.append(light_pos)

    def get_light_under_point(self, point):
        point_x, point_y = point

        # Check if the point is even on the board or not.
        if not (self.board_x < point_x < self.board_x + self.board_size and
                self.board_y < point_y < self.board_y + self.board_size):
            return None

        # Find the (i, j) of the cell, i.e., a light square and its right and
        # bottom padding, all three combined is a cell. Offsets represent the
        # location of the click within the cell.
        i, offset_y = divmod(point_y - self.board_y,
                self.light_size + self.light_gap)

        j, offset_x = divmod(point_x - self.board_x,
                self.light_size + self.light_gap)

        # Return this (i, j) only if the click is not in the padding space.
        if offset_x <= self.light_size and offset_y <= self.light_size:
            return i, j
        else:
            return None

    def toggle(self, light_i, light_j):
        # List of coordinates of lights to be toggled.
        toggle_positions = [(light_i, light_j)]

        game_size = self.game_size

        if light_j < game_size - 1:
            toggle_positions.append((light_i, light_j + 1))

        if light_j > 0:
            toggle_positions.append((light_i, light_j - 1))

        if light_i < game_size - 1:
            toggle_positions.append((light_i + 1, light_j))

        if light_i > 0:
            toggle_positions.append((light_i - 1, light_j))

        # Toggle the light at this location.
        for i, j in toggle_positions:
            self.board[i][j].toggle()

    def _on_menu_click(self, event):
        if self.on_menu_click is not None:
            self.on_menu_click(event)


class Solver(object):

    def __init__(self, display):
        self.display = display
        self.spotlight = None
        self.spotlight_pos = 0, 0

        self._on_solver_done = (lambda: self.on_solver_done and
                self.on_solver_done())
        self.on_solver_done = None

        self.spot_stage = 'show'
        self.last_spot_time = 0

    def draw(self):

        time_diff = time.time() - self.last_spot_time

        if not self.spotlight or \
                (self.spot_stage == 'show' and time_diff > 1) or \
                (self.spot_stage == 'hide' and time_diff > .6):

            self.last_spot_time = time.time()

            if self.spotlight and self.spot_stage == 'show':
                self.spotlight.in_spotlight = False
                self.game.toggle(*self.spotlight_pos)
                self.spot_stage = 'hide'

            elif self.game.solution:
                i, j = self.spotlight_pos = self.game.solution.pop()

                self.spotlight = self.game.board[i][j]
                self.spotlight.in_spotlight = True

                self.spot_stage = 'show'

            else:
                self._on_solver_done()

        self.game.draw()

    def handle(self, event):
        self.game.handle(event)


class Light(object):

    on_image = None
    off_image = None

    def __init__(self, display, value=False):
        self.display = display
        self.value = value

        if Light.on_image is None:
            Light.on_image = pygame.image.load('light-on.png')
            Light.off_image = pygame.image.load('light-off.png')

        self.rect = pygame.Rect((0, 0), Light.on_image.get_size())

        # Whether to highlight this light. Used by solver.
        self.in_spotlight = False
        self.spotlight_rect = self.rect.copy()
        self.spotlight_rect.width = self.rect.width / 2
        self.spotlight_rect.height = self.rect.height / 2

    def update_rect(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self.rect, name, value)

        self.spotlight_rect.center = self.rect.center

    def draw(self):
        self.display.blit(Light.on_image if self.value else Light.off_image,
                self.rect)

        if self.in_spotlight:
            pygame.draw.ellipse(self.display, (255, 0, 0), self.spotlight_rect,
                    0)

    def toggle(self):
        self.value = not self.value


class Menu(object):

    def __init__(self, display):
        self.display = display

        # The title is a bit bigger in the menu, than the game.
        # FIXME: Remove repetition with the title display code in `Game`.
        title_font = pygame.font.Font('Signika-Regular.ttf', 48)
        self.title_surface = title_font.render('Lights poof!', True,
                (213, 85, 148))
        self.title_rect = self.title_surface.get_rect()
        self.title_rect.centerx = self.display.get_width() / 2
        self.title_rect.top = 18

        # Maintain a list of buttons in this menu.
        self.buttons = []

        # Create the buttons.
        self.new_button('New Game', 'on_new_click')
        self.new_button('Solve', 'on_solve_click')
        self.new_button('Resume', 'on_resume_click')

        # Incrementally set the `y` coordinate of the buttons.
        y = self.title_rect.top + self.title_rect.height + 24
        button_gap = 12
        for button in self.buttons:
            button.update_rect(y=y)
            y += button.rect.height + button_gap

    def draw(self):
        # Draw the title.
        self.display.blit(self.title_surface, self.title_rect)

        for button in self.buttons:
            button.draw(self.display)

    def handle(self, event):
        for button in self.buttons:
            button.handle(event)

    def new_button(self, label, handler_name=None):
        button = Button(label, centerx=self.display.get_width() / 2)
        self.buttons.append(button)

        if handler_name:
            button.on_click = (lambda event: getattr(self, handler_name)(event))


class Button(object):

    active_image = None
    inactive_image = None

    def __init__(self, label, **kwargs):

        if Button.active_image is None:
            Button.label_font = pygame.font.Font('Signika-Light.ttf', 24)
            Button.active_image = pygame.image.load('button-active.png')
            Button.inactive_image = pygame.image.load('button-inactive.png')

        self.is_mousedown = False
        self.on_click = None

        self.label = label
        self.label_surface = Button.label_font.render(self.label, True,
                (240, 240, 240))

        self.rect = pygame.Rect((0, 0), Button.active_image.get_size())
        self.label_rect = self.label_surface.get_rect()

        self.update_rect(**kwargs)

    def update_rect(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self.rect, name, value)

        self.label_rect.center = self.rect.center

    def draw(self, surface):

        if self.is_mousedown:
            surface.blit(Button.active_image, self.rect)
        else:
            surface.blit(Button.inactive_image, self.rect)

        surface.blit(self.label_surface, self.label_rect)

    def handle(self, event):
        if self.on_click is None:
            return

        if event.type == MOUSEBUTTONDOWN and self.contains(event.pos):
            self.is_mousedown = True

        elif event.type == MOUSEBUTTONUP:

            if self.is_mousedown and self.contains(event.pos):
                self.on_click(event)

            self.is_mousedown = False

    def contains(self, point):
        return self.rect.collidepoint(point)


if __name__ == '__main__':
    App().main_loop()
