#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import time
import copy
from events import EventSystem

class SolverState(EventSystem):

    def __init__(self, display):
        self.display = display

        self.game = None

        self.spotlight = None
        self.spotlight_pos = 0, 0

        # Specified what stage we are in, in solving. Can take following values.
        #   show - A spotlight is being shown.
        #   hide - No spotlight is currently shown.
        self.spot_stage = 'show'

        # The last time at which spot stage changed. Helps with delays between
        # stage changes.
        self.last_spot_time = 0

        self._board = self._solution = None

    def draw(self):

        # Time since last spot stage change.
        time_diff = time.time() - self.last_spot_time

        if not self.spotlight or \
                (self.spot_stage == 'show' and time_diff > 1) or \
                (self.spot_stage == 'hide' and time_diff > .6):

            self.last_spot_time = time.time()

            if self.spotlight and self.spot_stage == 'show':
                # When there is a spotlight and the stage is `show`. These two
                # conditions might seem redundant, but on the first run, there
                # is no spotlight but the stage is `show`.

                self.spotlight.in_spotlight = False
                self.game.toggle(*self.spotlight_pos)
                self.spot_stage = 'hide'

            elif self.game.solution:
                # There is no spotlight, but the solution is still non-empty.

                i, j = self.spotlight_pos = self.game.solution.pop()

                self.spotlight = self.game.board[i][j]
                self.spotlight.in_spotlight = True

                self.spot_stage = 'show'

            else:
                # Solution is empty. Finished.
                self.emit('done-solving')

        self.game.draw()

    def handle(self, event):
        # XXX: This is a hack. There should be a better way.
        self.game.menu_btn.handle(event)

    def activated(self):
        # These values will be used to restore the `self.game` to its state
        # before the solver bagan.
        self._board = copy.deepcopy(self.game.board)
        self._solution = copy.deepcopy(self.game.solution)
        self._level = copy.deepcopy(self.game.level)

    def deactivated(self):

        self.game.board = self._board
        self.game.solution = self._solution
        self.game.level = self._level

        self._board = self._solution = self._level = None

        self.spotlight.in_spotlight = False
        self.spotlight = None
        self.spot_stage = 'show'
