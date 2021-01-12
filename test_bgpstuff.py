#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bgpstuff
import unittest
from unittest.mock import Mock, patch
import requests
import json


class TestGetJSONHeader(unittest.TestCase):
    def test_getJSONHeader(self):
        self.assertDictEqual(bgpstuff.getJSONHeader(), {
                             'Content-Type': 'application/json'})


class TestAttributes(unittest.TestCase):

    def test_ip(self):
        for i in range(10):
            resp = bgpstuff.Response()
            resp.asn = i+1
            self.assertEqual(resp.asn, i+1)

    def test_asn(self):
        for i in range(10):
            resp = bgpstuff.Response()
            resp.ip = "192.168.0.{}".format(i)
            self.assertEqual(resp.ip, "192.168.0.{}".format(i))


class TestFormatting(unittest.TestCase):

    def test_full_as_path(self):
        resp = bgpstuff.Response()
        resp.as_path = ["1", "2", "3"]
        resp.as_set = []
        self.assertEqual(resp.full_as_path(), "1 2 3")

        resp.as_path = ["1"]
        resp.as_set = []
        self.assertEqual(resp.full_as_path(), "1")

        resp.as_path = ["1"]
        resp.as_set = ["5"]
        self.assertEqual(resp.full_as_path(), "1 { 5 }")

        resp.as_path = ["1"]
        resp.as_set = ["1", "2"]
        self.assertEqual(resp.full_as_path(), "1 { 1 2 }")

        resp.as_path = ["1", "2"]
        resp.as_set = ["3", "4"]
        self.assertEqual(resp.full_as_path(), "1 2 { 3 4 }")


if __name__ == '__main__':
    unittest.main()
