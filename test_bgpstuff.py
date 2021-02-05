#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bgpstuff
import unittest


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = bgpstuff.Client()

    def test_get_route(self):
        self.client.get_route("8.8.8.8")
        self.assertEqual("8.8.8.0/24", self.client.route)

    def test_get_origin(self):
        self.client.get_origin("8.8.8.8")
        self.assertEqual(15169, self.client.origin)

    def test_get_as_path(self):
        self.client.get_as_path("8.8.8.8")
        self.assertEqual(15169, self.client.as_path[-1])

    def test_get_roa(self):
        self.client.get_roa("1.1.1.1")
        self.assertEqual("VALID", self.client.roa)

    def tearDown(self):
        self.client._close_session()
