#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import pygame
from pygame.locals import MOUSEBUTTONUP, MOUSEBUTTONDOWN

class Button(object):

    active_image = None
    inactive_image = None

    def __init__(self, display, label, **kwargs):

        if Button.active_image is None:
            Button.label_font = pygame.font.Font('Signika-Light.ttf', 24)
            Button.active_image = pygame.image.load('img/button-active.png')
            Button.inactive_image = pygame.image.load('img/button-inactive.png')

        self.display = display
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

    def draw(self):

        if self.is_mousedown:
            self.display.blit(Button.active_image, self.rect)
        else:
            self.display.blit(Button.inactive_image, self.rect)

        self.display.blit(self.label_surface, self.label_rect)

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
