#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import os
import shutil
import logging
#import tempfile
from time import time, sleep
from io import open

from baanprint import config

from subprocess import call
from pyPdf import PdfFileWriter, PdfFileReader
from argh import ArghParser, command
from yapsy.PluginManager import PluginManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('baanprint')

if sys.platform != 'win32':
    WindowsError = Exception

if sys.version_info[0] == 3:
    unicode = str


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
            if sys.platform == 'win32':
                if is_file_unlocked(filename):
                    break
            else:
                break


def is_file_unlocked(filename):
    """returns True if the file is unlocked, otherwise False

    PDFCreator sometimes still has a lock on the file,
    even if the file size isn't increasing anymore.

    :param filename: path to the file
    """

    tmpfile = filename + '.tmp'
    try:
        shutil.move(filename, tmpfile)
    except IOError as e:
        logger.debug(e)
        return False
    except WindowsError as e:
        logger.debug(e)
        return False
    else:
        shutil.move(tmpfile, filename)
        return True


def find_pdf_file(token):
    """iterates the printers output directory for the pdf

    :param token: token that the filename should contain.
    :returns the absolute path to the pdf file.
    """

    # it might take a while until the file is created
    for i in range(20):
        for filename in os.listdir(config.printer_output):
            if token in filename:
                return os.path.join(config.printer_output, filename)
        sleep(0.1)


@command
def handle(inputf, report, pagelength):
    """Detects the filetype and calls the appropriate handler.

    In order to detect the type all the plugins in the plugins folder are
    tried until a file type is found.
    Once the file type is found the plugins handle() function is called.

    :param inputf: path to the bpf file
    """
    doc = BwDocument(inputf)
    plugins = get_plugins()
    logger.debug('found {0} plugin(s)'.format(len(plugins)))
    logger.debug('trying to find plugin for {0}'.format(report))
    for p in plugins:
        logger.debug('trying plugin {0}'.format(p.name))
        if p.plugin_object.matches(report, doc.pages):
            logger.debug('plugin {0} matched'.format(p.name))
            p.plugin_object.handle(doc)
    os.remove(inputf)


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

    def __init__(self, bpf_path, page_size=config.default_page_size):
        self.creator = None
        self.doc_type = None
        self.pages = {1: ''}
        self.printer = None
        self.page_size = page_size

        # chr(27).. are escape sequences used by bwprint.exe to determine
        # the fonts used.
        # in order to define meta data in the report. use font size small
        # and begin the line with '//+'
        self.md_linestart = chr(27) + chr(20) + chr(33) + chr(34) + '//+'

        self.read_file(bpf_path)

    def _read_creator(self, fp):
        """reads the creator into self.creator

        The creator is supposed to be in the first line. As the baan print session
        should have added logname$ into it.
        """

        self.creator = fp.readline()
        if not self.creator.startswith('%%Creator'):
            fp.seek(0)
            self.creator = None
        else:
            self.creator = self.creator.replace('%%Creator:', '').strip()

    def read_file(self, bpf_path):
        with open(bpf_path, 'r', encoding='latin1') as fp:
            self._read_creator(fp)

            page = 1
            index = 0
            for line in fp:
                if page not in self.pages:
                    self.pages[page] = ''

                # Lines starting with //+ may contain metadata used in the plugins
                # So don't include them for the page splitting
                if not line.startswith(self.md_linestart):
                    index += 1

                self.pages[page] += line

                if index % self.page_size == 0:
                    page += 1

    def dump(self, printer=None, include_md_lines=False):
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

        output = os.path.join(os.curdir, '{0}.bpf'.format(time()))
        token = '{0}_{1}'.format(self.creator, str(time()).replace('.', '_'))

        with open(output, 'w', encoding='latin1') as fd:
            fd.write(unicode(printer.format(token)) + '\n')
            for page in self.pages:
                index = 0
                for line in self.pages[page].split('\n'):
                    # see read_file() for info on self.md_linestart
                    if not line.startswith(self.md_linestart) or include_md_lines:
                        index += 1
                        if index <= self.page_size:
                            fd.write(line + '\n')
                        else:
                            fd.write(line)

        return output, token


def main():
    p = ArghParser()
    p.add_commands([convert, handle])
    p.dispatch()


if __name__ == '__main__':
    main()
