#!/usr/bin/env python
# coding=utf-8
"""
This module contains meta-information about the package.
It is kept simple and separate from the main module, because this information
is also read by the setup.py. And during installation the module cannot
yet be imported.
"""
from __future__ import division, print_function, unicode_literals

import os

VERSION = 'latest'
if os.environ.get('VERSION') is not None:
    VERSION = os.environ.get('VERSION')
    if VERSION in ['master', 'develop']:
        VERSION = 'latest'

__all__ = ("__version__", "__author__", "__url__")

__version__ = VERSION

__author__ = 'me@philips.com'

__url__ = "https://www.philips.com/"
