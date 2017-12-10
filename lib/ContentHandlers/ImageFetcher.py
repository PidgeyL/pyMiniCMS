#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Content Generator Helper ImageFetcher
#   Fetches images from a folder and returns the paths
#
#  Settings
#    dir      (required): the directory to fetch the images from
#    listName (optional): Name for the list. Default is 'images'
#
# Software is free software released under the "Modified BSD license"
#
# Copyright (c) 2017 	Pieter-Jan Moreels

# imports
import os
import sys
from PIL import Image

_runPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_runPath, ".."))

from lib.Config import Configuration as conf

class ImageFetcher:
    def __init__(self, settings):
        self.images = []
        self.varname = settings.get('listName') or 'images'

        if not settings.get('dir'):
            print("ImageFetcher not initialized correctly")
            sys.exit(201)
        path = settings['dir']
        if not os.path.exists(path):
            print("'%s' does not exist"%path)
            sys.exit(202)
        if not os.path.isdir(path):
            print("'%s' is not a directory"%path)
            sys.exit(203)

        for item in [os.path.join(path, x) for x in os.listdir(path)]:
            if os.path.isfile(item):
                self.images.append(item)

    def getContent(self):
        return {self.varname: self.images}
