#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import sys
import time
import pygame
from pygame.locals import QUIT, KEYUP
from game import GameState
from game import GameOverState
from menu import MenuState
from solver import SolverState

# TODO: Create a better Event system.

class App(object):

    def __init__(self, dev=False):
        self.dev = dev

        pygame.init()

        self.display = pygame.display.set_mode((320, 420))
        pygame.display.set_caption('Lights poof!')

        self.init_bg_surface()

        self.solver = SolverState(self.display)
        self.solver.on_solver_done = self.on_solver_done

        self.game_over_state = GameOverState(self.display)

        self.init_new_game()

        self.menu = MenuState(self.display)
        self.menu.on_resume_click = self.on_resume_click
        self.menu.on_new_click = self.on_new_click
        self.menu.on_restart_click = self.on_restart_click
        self.menu.on_solve_click = self.on_solve_click

        self.current_state = None
        self.set_state(self.game)

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
        bg_image = pygame.image.load('img/bg.png')
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
        self.game = GameState(self.display,
                level=([(2, 2)] if self.dev else None))
        self.game.on_menu_click = self.on_menu_click
        self.game.on_game_over = self.on_game_over

        self.solver.game = self.game

        self.game_over_state.game = self.game

    def set_state(self, state):
        old_state = self.current_state
        self.current_state = state

        if hasattr(old_state, 'deactivated'):
            old_state.deactivated()

        if hasattr(self.current_state, 'activated'):
            self.current_state.activated()

    def on_menu_click(self):
        self.set_state(self.menu)

    def on_game_over(self):
        self.set_state(self.game_over_state)

    def on_resume_click(self):
        self.set_state(self.game)

    def on_new_click(self):
        self.init_new_game()
        self.set_state(self.game)

    def on_restart_click(self):
        self.game.restart()
        self.set_state(self.game)

    def on_solve_click(self):
        self.set_state(self.solver)
        print(self.solver.game.solution)

    def on_solver_done(self):
        print('Solving complete')
        self.set_state(self.game)
