#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import pygame
from button import Button
from pygame.locals import MOUSEBUTTONUP, MOUSEBUTTONDOWN

class MenuState(object):

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

        self.menu_bar = MenuButtonBar(self.display)
        self.menu_bar.update_rect(y=self.title_rect.top +
                self.title_rect.height + 24)
        self.menu_bar.handler = self

    def draw(self):
        # Draw the title.
        self.display.blit(self.title_surface, self.title_rect)

        self.menu_bar.draw()

    def handle(self, event):
        self.menu_bar.handle(event)


class MenuButtonBar(object):

    def __init__(self, display):

        self.display = display
        self.surface = self.display.convert_alpha()
        self.rect = self.surface.get_rect()

        # Maintain a list of buttons in this menu.
        self.buttons = []

        # Create the buttons.
        self.new_button('New Game', 'on_new_click')
        self.new_button('Restart', 'on_restart_click')
        self.new_button('Solve', 'on_solve_click')
        self.new_button('Resume', 'on_resume_click')

        # Incrementally set the `y` coordinate of the buttons.
        y = 0
        button_gap = 12
        for button in self.buttons:
            button.update_rect(y=y)
            y += button.rect.height + button_gap

        self.update_rect(x=0, width=self.display.get_width(),
                height=y - button_gap)

        self.render()

    def render(self):
        self.surface.fill((0, 0, 0, 0))

        for button in self.buttons:
            button.draw()

    def update_rect(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self.rect, name, value)

    def draw(self):
        self.display.blit(self.surface, self.rect)

    def handle(self, event):

        if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN) and event.button == 1:
            # The event `pos` would be based on the coordinates of the root
            # display. It needs to be translated to be based on `self.rect`
            # so the button compares it correctly.

            # Also, events are read-only. So we need to create a new event.

            pos = event.pos
            event = pygame.event.Event(event.type, button=event.button,
                    pos=(pos[0] - self.rect.x, pos[1] - self.rect.y))

        for button in self.buttons:
            button.handle(event)

        self.render()

    def new_button(self, label, handler_name=None):
        button = Button(self.surface, label,
                centerx=self.display.get_width() / 2)
        self.buttons.append(button)

        if handler_name:
            button.on_click = (lambda event:
                    getattr(self.handler, handler_name)(event))
