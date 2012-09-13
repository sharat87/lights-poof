#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

import sys
from app import App

if '--dev' in sys.argv:
    app = App(dev=True)
else:
    app = App()

app.main_loop()
