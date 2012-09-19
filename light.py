#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import pygame

class Light(object):

    on_image = None
    off_image = None

    def __init__(self, display, value=False):
        self.display = display
        self.value = value

        if Light.on_image is None:
            Light.on_image = pygame.image.load('img/light-on.png')
            Light.off_image = pygame.image.load('img/light-off.png')
            Light.spotlight_image = pygame.image.load('img/light-spotlight.png')

        self.rect = pygame.Rect((0, 0), Light.on_image.get_size())

        # Whether to highlight this light. Used by solver.
        self.in_spotlight = False

    def update_rect(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self.rect, name, value)

    def draw(self):
        self.display.blit(Light.on_image if self.value else Light.off_image,
                self.rect)

        if self.in_spotlight:
            self.display.blit(Light.spotlight_image, self.rect)

    def toggle(self):
        self.value = not self.value

    def __deepcopy__(self, memo):
        # Deep copying the surface doesn't make sense and doesn't work out
        # either.
        clone = Light(self.display, self.value)

        clone.update_rect(x=self.rect.x, y=self.rect.y)

        return clone

    def __unicode__(self):
        return '<Light ' + ('on' if self.value else 'off') + '>'

    __str__ = __repr__ = __unicode__
