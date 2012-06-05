#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yapsy.PluginManager import IPlugin
import re


class OrderDetector(IPlugin):
    def __init__(self):
        self.name = 'PurchaseOrder'
        self.pattern = '.*ORDER.*'

    def matches(self, report, pages):
        for line in pages[1]:
            if re.match(self.pattern, line):
                return True
        return False

    def handle(self, bwdoc):
        pass
