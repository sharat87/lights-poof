#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

from collections import defaultdict

class EventSystem(object):

    def init(self):
        # So that the subclasses don't have to call this class's __init__
        # method.
        try:
            self.handlers
        except AttributeError:
            self.handlers = defaultdict(list)

    def emit(self, event_name):
        self.init()
        for handler in self.handlers[event_name]:
            handler()

    def listen(self, event_name, fn):
        self.init()
        self.handlers[event_name].append(fn)
