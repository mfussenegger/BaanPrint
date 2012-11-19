#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
from baanprint import bwprint as bw
from io import open


class BwDocumentTest(unittest.TestCase):
    def test_init(self):
        doc = bw.BwDocument('./tests/bwtest.bpf', (4, 132))
        self.assertEqual(doc.page_size, (4, 132))
        self.assertEqual(doc.creator, 'user1')
        self.assertEqual(len(doc.pages), 3)

    def test_dump(self):
        doc = bw.BwDocument('./tests/bwtest.bpf', (4, 132))
        output, token = doc.dump()
        try:
            with open(output, 'r', encoding='latin1') as fp:
                lines = fp.readlines()
                self.assertEqual(len(lines), 13)
        finally:
            os.remove(output)

    def test_dump_with_md_lines(self):
        doc = bw.BwDocument('./tests/bwtest2.bpf', (4, 132))
        output, token = doc.dump()
        try:
            with open(output, 'r', encoding='latin1') as fp:
                lines = fp.readlines()
                self.assertEqual(len(lines), 13)
        finally:
            os.remove(output)
