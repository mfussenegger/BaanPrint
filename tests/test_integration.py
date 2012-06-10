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
        plugins = bwprint.get_plugins()
        self.assertIsInstance(plugins, list)
        self.assertEqual(len(plugins), yapsy_files)


#class TestDocTypeDetection(unittest.TestCase):
#    def test_type_detection(self):
#        path = './tests/purchase_orders.bpf'
#        self.assertEqual('PurchaseOrder', bwprint.testtype(path))


class TestConvert(unittest.TestCase):
    def test_convert(self):
        path = './tests/purchase_orders.bpf'
        bwprint.convert(path, './tests/purchase_orders.pdf')
        self.assertTrue(os.path.exists('./tests/purchase_orders.pdf'))

    def test_add_template(self):
        pdf = './tests/purchase_orders.pdf'
        output = './tests/purchase_orders_w_logo.pdf'
        template = './tests/template.pdf'
        bwprint.add_template(pdf, template, output)
        self.assertTrue(os.path.exists('./tests/purchase_orders_w_logo.pdf'))
