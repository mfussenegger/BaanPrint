#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from baanprint import config

from argh import ArghParser, command
from yapsy.PluginManager import PluginManager, IPlugin

logging.basicConfig(level=logging.INFO)


class IBwPlugin(IPlugin):
    """Interface for the Yapsy plugins"""

    def matches(self, pages):
        """called in order to detect the document type"""
        pass

    def handle(self, bwdocument):
        """called if the document type matched"""
        pass


@command
def convert(inputf, outputf, template=None):
    """Converts the given file into a pdf

    :param inputf: path to the bpf file (generated from baan)
    :param outpuf: path to the pdf file that will be created
    :param template: 1 page pdf file, will be overlayed onto each page
    """
    pass


@command
def handle(inputf, template=None):
    """Detects the filetype and calls the appropriate handler.

    In order to detect the type all the plugins in the plugins folder are
    tried until a file type is found.
    Once the file type is found the plugins handle() function is called.

    :param inputf: path to the bpf file
    :param template: 1 page pdf file, usage depends on the doctype/plugin called
    """
    pass


@command
def testtype(inputf):
    doc = BwDocument(inputf)
    plugins = get_plugins()
    for p in plugins:
        if p.plugin_object.matches(doc.pages):
            print(p.plugin_object.name)
            return p.plugin_object.name


def get_plugins():
    """Returns all yapsy plugins in the plugin directory

    >>> plugins = get_plugins()
    >>> type(plugins) is list
    True

    :return: :class:`list`
    """
    manager = PluginManager()
    manager.setPluginPlaces([
        os.path.join(os.path.dirname(__file__), 'plugins')])

    manager.collectPlugins()
    plugins = [p for p in manager.getAllPlugins()]
    return plugins


class BwDocument(object):
    """In memory input file"""

    def __init__(self, bpf_path):
        self.creator = None
        self.doc_type = None
        self.pages = {1: ''}
        self.page_size = config.default_page_size
        self.read_file(bpf_path)

    def read_file(self, bpf_path):
        with open(bpf_path, 'r', encoding='latin1') as fp:

            # The Baan print session should add logname$ into the first line
            self.creator = fp.readline()
            if not self.creator.startswith('%%Creator'):
                fp.seek(0)
                self.creator = None
            else:
                self.creator = self.creator.replace('%%Creator:', '')

            page = 1
            for index, line in enumerate(fp.readlines()):
                if index >= self.page_size and index % self.page_size == 0:
                    page += 1
                    self.pages[page] = ''

                self.pages[page] += line + os.linesep


def main():
    p = ArghParser()
    p.add_commands([convert, handle, testtype])
    p.dispatch()


if __name__ == '__main__':
    main()
