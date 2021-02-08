#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bgpstuff
import ipaddress
import unittest


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = bgpstuff.Client()

    def test_get_route(self):
        self.client.get_route("8.8.8.8")
        self.assertEqual(ipaddress.ip_network(
            '8.8.8.0/24'), self.client.route)
        self.client.get_route("2600::")
        self.assertEqual(ipaddress.ip_network(
            '2600::/48'), self.client.route)
        with self.assertRaises(ValueError):
            self.client.get_route("10.0.0.0")

    def test_get_origin(self):
        self.client.get_origin("8.8.8.8")
        self.assertEqual(15169, self.client.origin)
        with self.assertRaises(ValueError):
            self.client.get_route("10.0.0.0")

    def test_get_as_path(self):
        self.client.get_as_path("8.8.8.8")
        self.assertEqual(15169, self.client.as_path[-1])

    def test_get_roa(self):
        self.client.get_roa("1.1.1.1")
        self.assertEqual("VALID", self.client.roa)
        with self.assertRaises(ValueError):
            self.client.get_route("10.0.0.0")

    def test_as_name(self):
        self.client.get_as_name(15169)
        self.assertEqual("GOOGLE", self.client.as_name)
        with self.assertRaises(ValueError):
            self.client.get_route("hi")

    def test_get_sourced_prefixes(self):
        self.client.get_sourced_prefixes(15169)
        dns = ipaddress.ip_network("8.8.4.0/24")
        if dns not in self.client.sourced:
            self.assert_("8.8.4.0/24 network not found")
        with self.assertRaises(ValueError):
            self.client.get_sourced_prefixes("hi")

    def test_get_totals(self):
        self.client.get_totals()
        self.assertGreater(self.client.total_v4, 800000)
        self.assertGreater(self.client.total_v6, 100000)

    def tearDown(self):
        self.client._close_session()
