#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import logging
#import tempfile
from time import time, sleep

from baanprint import config

from subprocess import check_call as call
from pyPdf import PdfFileWriter, PdfFileReader
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
    doc = BwDocument(inputf)
    bpf, token = doc.dump()

    args = config.bwprint_exe + ['/p', '/r', bpf]
    call(args)
    if os.path.exists(bpf):
        os.remove(bpf)

    pdf = get_pdf_file(token)

    if pdf and template:
        add_template(pdf, template, outputf)
    elif pdf:
        shutil.move(pdf, outputf)


def add_template(pdf, template, outputpath):
    """Adds the template to every page in pdf

    :param pdf: path to a pdf file
    :param template: path to a pdf file. First page is used as template
                     that is added to every page of "pdf"
    :param outputpath: filename where the resulting pdf is saved.
    """
    pdf_input = PdfFileReader(open(pdf, 'rb'))
    pdf_template = PdfFileReader(open(template, 'rb'))
    pdf_output = PdfFileWriter()

    template_page = pdf_template.getPage(0)

    for i in range(pdf_input.getNumPages()):
        page = pdf_input.getPage(i)
        page.mergePage(template_page)
        pdf_output.addPage(page)

    pdf_output.write(open(outputpath, 'wb'))


def get_pdf_file(token):
    absfilename = find_pdf_file(token)
    assert isinstance(absfilename, str)
    wait_until_file_is_written(absfilename)
    return absfilename


def wait_until_file_is_written(filename):
    """sleep until the file doesn't increase in size

    cups created the file immediately, but keeps writting to it.
    :param filename: file whose size is checked
    """

    while True:
        lastsize = os.path.getsize(filename)
        sleep(0.1)
        if os.path.getsize(filename) == lastsize:
            break


def find_pdf_file(token):
    """iterates the printers output directory for the pdf

    :param token: token that the filename should contain.
    :returns the absolute path to the pdf file.
    """

    # it might take a while until the file is created
    for i in range(20):
        for filename in os.listdir(config.printer_output):
            if filename.startswith(token):
                return os.path.join(config.printer_output, filename)
        sleep(0.1)


@command
def handle(inputf):
    """Detects the filetype and calls the appropriate handler.

    In order to detect the type all the plugins in the plugins folder are
    tried until a file type is found.
    Once the file type is found the plugins handle() function is called.

    :param inputf: path to the bpf file
    """
    doc = BwDocument(inputf)
    plugins = get_plugins()
    for p in plugins:
        if p.plugin_object.matches(doc.pages):
            p.plugin_object.handle(doc)


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
    return manager.getAllPlugins()


class BwDocument(object):
    """In memory input file"""

    def __init__(self, bpf_path):
        self.creator = None
        self.doc_type = None
        self.pages = {1: ''}
        self.printer = None
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

    def dump(self, printer=None):
        """writes the in-memory bp-file into a temporary file on disk

        :param printer: printer line that is added in the first line of the file.
                        In case the printer is null, config.pdf_printer is used.

        The printer line is read by bwprint.exe and is required to specify the
        printer which should be used. In addition, settings like page margins,
        page width and size are also specified.

        A token is added into the printer line. This token is used to identify
        the file that is printed using the pdf printer.
        """

        if not printer:
            printer = self.printer or config.pdf_printer

        # this line doesn't work as bwprint.exe doesn't accept the bp file.
        # I have no idea why that is, if you know - please enlighten me.
        #_, output = tempfile.mkstemp('.bpf', dir=os.curdir)

        output = os.path.join(os.curdir, 'test.bpf')
        token = str(time()).replace('.', '_')

        with open(output, 'w', encoding='latin1') as fd:
            fd.write(printer.format(token) + '\n')
            for page in self.pages:
                fd.writelines(self.pages[page])

        return output, token


def main():
    p = ArghParser()
    p.add_commands([convert, handle, testtype])
    p.dispatch()


if __name__ == '__main__':
    main()
