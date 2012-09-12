#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import pygame
from button import Button

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
        self.new_button('Restart', 'on_restart_click')
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
