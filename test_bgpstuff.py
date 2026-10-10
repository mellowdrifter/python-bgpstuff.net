#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bgpstuff
import ipaddress
import unittest
from unittest.mock import patch

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = bgpstuff.Client()

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_get_route(self, mock_request):
        mock_request.return_value = {"prefix": "8.8.8.0/24"}
        resp = self.client.get_route("8.8.8.8")
        self.assertEqual(resp["prefix"], "8.8.8.0/24")
        mock_request.assert_called_with("route/8.8.8.8")

        mock_request.return_value = None
        resp = self.client.get_route("1.2.3.4")
        self.assertIsNone(resp)

        with self.assertRaises(ValueError):
            self.client.get_route("10.0.0.0")

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_get_origin(self, mock_request):
        mock_request.return_value = {"origin": 15169}
        resp = self.client.get_origin("8.8.8.8")
        self.assertEqual(resp["origin"], 15169)
        mock_request.assert_called_with("origin/8.8.8.8")

        with self.assertRaises(ValueError):
            self.client.get_origin("10.0.0.0")

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_get_as_path(self, mock_request):
        mock_request.return_value = {"as_path": [15169]}
        resp = self.client.get_as_path("8.8.8.8")
        self.assertEqual(resp["as_path"][-1], 15169)

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_get_roa(self, mock_request):
        mock_request.return_value = {"roa": "VALID"}
        resp = self.client.get_roa("1.1.1.1")
        self.assertEqual(resp["roa"], "VALID")

        with self.assertRaises(ValueError):
            self.client.get_roa("10.0.0.0")

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_as_name(self, mock_request):
        mock_request.return_value = {"asname": "GOOGLE"}
        resp = self.client.get_as_name(15169)
        self.assertEqual(resp["asname"], "GOOGLE")

        with self.assertRaises(ValueError):
            self.client.get_as_name(-1)

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_get_sourced_prefixes(self, mock_request):
        mock_request.return_value = {"prefixes": ["8.8.4.0/24"]}
        resp = self.client.get_sourced_prefixes(15169)
        self.assertIn("8.8.4.0/24", resp["prefixes"])

        with self.assertRaises(ValueError):
            self.client.get_sourced_prefixes(-1)

    def test_get_totals(self):
        with self.assertRaises(NotImplementedError):
            self.client.get_totals()

    @patch('bgpstuff.Client._bgpstuff_request')
    def test_get_all_as_names(self, mock_request):
        mock_request.return_value = {"15169": "GOOGLE"}
        resp = self.client.get_as_names()
        self.assertEqual(resp["15169"], "GOOGLE")

    def test_get_vrps(self):
        with self.assertRaises(NotImplementedError):
            self.client.get_vrps(15169)

    def test_deprecation_warning(self):
        import warnings
        with self.assertWarns(DeprecationWarning):
            client = bgpstuff.Client(url="https://bgpstuff.net/v1")
            client._close_session()

        with self.assertWarns(DeprecationWarning):
            client = bgpstuff.Client(url="https://bgpstuff.net/v2")
            client._close_session()

        # Should not raise warning for normal url
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client = bgpstuff.Client(url="https://bgpstuff.net")
            client._close_session()
            self.assertEqual(len(w), 0)

    def tearDown(self):
        self.client._close_session()

if __name__ == '__main__':
    unittest.main()
