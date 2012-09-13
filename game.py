#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import random
import pygame
from pygame.locals import MOUSEBUTTONUP
from light import Light
from button import Button
from menu import MenuButtonBar

class GameState(object):

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

        self.level = self.solution = None
        self.is_game_over = False

        self.board_size = ((self.light_size + self.light_gap) * self.game_size
                - self.light_gap)

        self.board_x = (self.display.get_width() - self.board_size) / 2
        self.board_y = (self.display.get_height() - self.board_size) / 2

        self.board = [[Light(self.display) for _ in range(self.game_size)]
                for _ in range(self.game_size)]
        self.apply_level(level)
        self.update_light_positions()

        self.menu_btn = Button(self.display, 'Menu',
                centerx=self.display.get_width() / 2,
                y=self.board_y + self.board_size + 24)

        # Menu button click handler should be set from outside this class.
        self.menu_btn.listen('click', self._on_menu_click)
        self.on_menu_click = None

        # Handler for when the game is over.
        self.on_game_over = None

    def apply_level(self, level):

        if level is None:
            # How many turns should the game be of?
            min_turns = self.game_size
            max_turns = self.game_size * 2
            turns = random.randint(min_turns, max_turns)

            # Create a list of all possible coordinates and select `turns` of
            # them in random.
            all_coordinates = [(i, j) for i in range(self.game_size)
                    for j in range(self.game_size)]
            random.shuffle(all_coordinates)

            # Here's the level. Toggling these coordinates will give us the
            # level just generated.
            self.level = all_coordinates[:turns]

            # They are also the solution of this game. Keeping it separate as
            # the level representation might change in the future.
            self.solution = all_coordinates[:turns]

        else:
            self.level = level
            self.solution = list(level)

        # Empty the board first.
        for row in self.board:
            for light in row:
                light.value = False

        # Toggle each of the selected coordinate.
        for i, j in self.level:
            self.toggle(i, j)

    def draw(self):
        # Draw the title.
        self.display.blit(self.title_surface, self.title_rect)

        # Draw the lights.
        for row in self.board:
            for light in row:
                light.draw()

        # Draw the buttons.
        self.menu_btn.draw()

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

        self.check_game_over()

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

    def check_game_over(self):

        for row in self.board:
            for light in row:
                if light.value:
                    self.is_game_over = False
                    return

        self.is_game_over = True

        if self.on_game_over is not None:
            self.on_game_over()

    def restart(self):
        self.apply_level(self.level)

    def _on_menu_click(self):
        if self.on_menu_click is not None:
            self.on_menu_click()


class GameOverState(object):

    def __init__(self, display, game=None):
        self.display = display
        self.game = game

        self.overlay_surface = self.display.convert_alpha()
        self.overlay_surface.fill((0, 0, 0, 230))

        title_font = pygame.font.Font('Signika-Regular.ttf', 40)
        title_surface = title_font.render('Yay! You won!', True,
                (213, 85, 148))

        title_rect = title_surface.get_rect()
        title_rect.centerx = self.display.get_width() / 2
        title_rect.top = 64

        self.overlay_surface.blit(title_surface, title_rect)

        self.menu_bar = MenuButtonBar(self.overlay_surface)
        self.menu_bar.update_rect(y=title_rect.top + title_rect.height + 18)

    def draw(self):
        self.game.draw()
        self.display.blit(self.overlay_surface, (0, 0))
        self.menu_bar.draw()

    def handle(self, event):
        pass
