#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import pygame, sys
from pygame.locals import *
import time
import random

class Game(object):

    def __init__(self, level=None):

        self.display = pygame.display.set_mode((320, 420))
        pygame.display.set_caption('Lights poof!')

        self.on_image = pygame.image.load('light-on.png')
        self.off_image = pygame.image.load('light-off.png')

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

        self.board = [[False] * self.game_size for _ in range(self.game_size)]
        self.apply_level(level)

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
        solution_coordinates = all_coordinates[:turns]

        # Toggle each of the selected coordinate.
        for i, j in solution_coordinates:
            self.toggle(i, j)

        return [[False] * self.game_size for _ in range(self.game_size)]

    def draw(self):
        # Draw background.
        self.display.fill((40, 40, 40))

        # Draw the title.
        self.display.blit(self.title_surface, self.title_rect)

        # Draw the lights.
        y = self.board_y
        for i, row in enumerate(self.board):
            x = self.board_x

            for j, status in enumerate(row):

                image = self.on_image if status else self.off_image
                self.display.blit(image, (x, y))

                x += self.light_size + self.light_gap

            y += self.light_size + self.light_gap

        pygame.display.update()

    def handle(self, event):

        # Left click.
        if event.type == MOUSEBUTTONUP and event.button == 1:
            self.on_left_click(event)

    def on_left_click(self, event):

        # Get the light's coordinates under the click, if any.
        light_pos = self.get_light_under_point(event.pos)

        # No light under the click. Do nothing.
        if light_pos is None:
            return

        self.toggle(*light_pos)

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
            self.board[i][j] = not self.board[i][j]


pygame.init()
game = Game()

while True:

    for event in pygame.event.get():

        if event.type == QUIT or (event.type == KEYUP and event.key == 27):
            pygame.quit()
            sys.exit()

        else:
            game.handle(event)

    game.draw()

    time.sleep(.01)
