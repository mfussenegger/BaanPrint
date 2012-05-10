#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from baanprint import bwprint


class TestBwprint(unittest.TestCase):
    def test_plugin_count(self):
        plugin_dir = './baanprint/plugins/'
        yapsy_files = len([f for f in os.listdir(plugin_dir)
                          if f.endswith('.yapsy-plugin')])
        self.assertEqual(len(bwprint.get_plugins()), yapsy_files)


#class TestDocTypeDetection(unittest.TestCase):
#    def test_type_detection(self):
#        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
#                            'bestellungen.bpf')
#        self.assertEqual('PurchaseOrder', bwprint.testtype(path))
