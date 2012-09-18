#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

from collections import defaultdict
from itertools import chain

class Event(object):

    def __init__(self, type_, **kwargs):
        self.type = type_
        self.props = kwargs

        for name, value in kwargs.items():
            setattr(self, name, value)

    def __unicode__(self):
        return '<Event (' + self.type + ')>'

    __str__ = __repr__ = __unicode__


class EventSystem(object):

    def init(self):
        # So that the subclasses don't have to call this class's __init__
        # method.
        try:
            self.handlers
        except AttributeError:
            self.handlers = defaultdict(list)

    def emit(self, event, **kwargs):
        self.init()

        if not isinstance(event, Event):
            event = Event(event, **kwargs)

        elif kwargs:
            raise ValueError('When emitting an event object, no keyword '
                    'arguments are accepted.')

        for handler in chain(self.handlers[event.type], self.handlers['*']):
            handler(event)

    def listen(self, event_name, fn):
        self.init()
        self.handlers[event_name].append(fn)
