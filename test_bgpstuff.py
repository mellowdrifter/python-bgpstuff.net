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

    def tearDown(self):
        self.client._close_session()
