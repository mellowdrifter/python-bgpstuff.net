#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python client for the BGPStuff.net API.
"""
import ipaddress
import requests
from http.client import responses
from ratelimit import limits, sleep_and_retry
from typing import List


class BGPStuffError(Exception):
    """GenericError Class for all BGPStuff Client Errors."""


class Client:
    """Class Client is an object with all the required methods to
    interact with the REST API portions of bgpstuff.net. The class
    should be reused as it has a built in rate-limiter as long as
    you use the same object

    Args:
        url (str): The BGPStuff instance to query against.
    """

    def __init__(self, url="https://bgpstuff.net"):
        self.url = url
        self.session_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'python-bgpstuff.net/x.x.x',
        }
        self.session = self._get_session()
        self._status_code = None
        self._id = None
        self._route = None
        self._origin = None
        self._as_path = None
        self._as_set = None
        self._roa = None

    def _get_session(self):
        """Make a requests session object with the proper headers."""
        session = requests.Session()
        session.headers.update(self.session_headers)

        return session

    def _close_session(self):
        self.session.close()

    @property
    def status(self) -> str:
        return responses[self.status_code]

    @property
    def status_code(self) -> int:
        return self._status_code

    @status_code.setter
    def status_code(self, code: int):
        self._status_code = code

    @property
    def request_id(self) -> str:
        return self._id

    @request_id.setter
    def request_id(self, id: str):
        self._id = id

    @property
    def route(self) -> str:
        return self._route

    @route.setter
    def route(self, route: str):
        self._route = route

    @property
    def origin(self) -> int:
        return self._origin

    @origin.setter
    def origin(self, origin: str):
        self._origin = int(origin)

    @property
    def as_path(self) -> List[int]:
        return self._as_path

    @as_path.setter
    def as_path(self, path: List[str]):
        if path:
            self._as_path = list(map(int, path))

    @property
    def as_set(self) -> List[int]:
        return self._as_set

    @as_set.setter
    def as_set(self, path: List[str]):
        if path:
            self._as_set = list(map(int, path))

    @property
    def roa(self) -> str:
        return self._roa

    @roa.setter
    def roa(self, roa: str):
        self._roa = roa

    @sleep_and_retry
    @limits(calls=30, period=60)
    def _bgpstuff_request(self, endpoint):
        """Performs an arbitrary HTTP GET to BGPStuff.

        Args:
            endpoint (str): The REST endpoint to query

        Returns:
            value (dict): Deserialized JSON response from BGPStuff.
        """
        # Reset exists and statuses as the query will fill these with new values.
        self.exists = False

        url = f"{self.url}/{endpoint}"

        request = self.session.get(url)

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise BGPStuffError from error

        value = request.json()
        self.exists = value['Response']['Exists']

        return value

    def get_route(self, ip_address):
        """Gets the route/prefix for the given IP address.

        Args:
            ip_address (str): The IP address to lookup.

        Returns:
            route (str): The route/prefix that the IP belongs into.
        """
        _validate_ip(ip_address)

        endpoint = "route"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.route = resp["Response"]["Route"]

    def get_origin(self, ip_address):
        """Gets the origin AS for the given IP address.

        Args:
            ip_address (str): The IP address to lookup.

        Returns:
            origin (str): The ASN originating the route/prefix this IP
            address belongs to.
        """
        _validate_ip(ip_address)

        endpoint = "origin"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.origin = resp["Response"]["Origin"]

    def get_as_path(self, ip_address):
        """Gets the AS_PATH to the given IP address.

        Args:
            ip_address (str): The IP address to lookup.

        Returns:
            as_path (list): The AS_PATH to the prefix this IP belongs to.
        TODO: Combine with self.get_as_set()
        """
        _validate_ip(ip_address)

        endpoint = "aspath"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.as_path = resp["Response"]["ASPath"]
        self.as_set = resp["Response"]["ASSet"]

    def get_roa(self, ip_address):
        """Gets the ROA of the route/prefix containing the given IP address.

        Args:
            ip_address (str): The IP address to lookup.

        Returns:
            roa (str): The AS_PATH to the prefix this IP belongs to.
        TODO: Combine with self.get_as_path()
        """
        _validate_ip(ip_address)

        endpoint = "roa"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.roa = resp["Response"]["ROA"]

    def get_as_name(self, asn):
        """Gets the name of the given ASN.

        Args:
            asn (str): The ASN to lookup.

        Returns:
            as_name (str): The name of the given ASN.
        TODO: Add function to validate ASN
        """
        endpoint = "asname"
        resp = self._bgpstuff_request(f"{endpoint}/{asn}")

        as_name = resp["Response"]["ASName"]

        return as_name

    def get_sourced_prefixes(self, asn):
        """Gets a list of prefixes sourced by the given ASN.

        Args:
            asn (str): The ASN to lookup.

        Returns:
            sourced_prefixes (list): List of prefixes originated.
        TODO: Add function to validate ASN
        """
        endpoint = "sourced"
        resp = self._bgpstuff_request(f"{endpoint}/{asn}")

        sourced_prefixes = resp["Response"]["Sourced"]["Prefixes"]

        return sourced_prefixes

# TODO: most queries I see are for both of these at the same time. I'd rather
# return a single query with both values
    def get_totals(self, ip_version=6):
        """Gets the total number of prefixes seen by the collector for the
        given IP version.

        Args:
            ip_version (int): IP version to get. Default: IPv6

        Returns:
            total_v6 (int): Total number of IPv6 prefixes
            total_v4 (int): Total number of IPv4 prefixes
        """
        endpoint = "totals"
        resp = self._bgpstuff_request(f"{endpoint}")

        totals = resp["Response"]["Totals"]
        if ip_version == 6:
            return totals["Ipv6"]
        if ip_version == 4:
            return totals["Ipv4"]

        raise BGPStuffError("Only IPv6 and IPv4 are supported.")

    def get_invalids(self):
        """Gets a list of all invalid prefixes observed by the BGPStuff
        route collector.

        Args:
            asn (str): The ASN to lookup.

        Returns:
            resp (json): The JSON returned from the REST endpoint.
        """
        # Reset exists and statuses as the query will fill these with new values.
        self.exists = False
        self.status_code = 0
        # TODO: Add function to validate ASN
        endpoint = "invalids"
        resp = self._bgpstuff_request(f"{endpoint}/")

        invalid_list = resp["Response"]["Invalids"]

        invalids = {}
        for invalid in invalid_list:
            invalids[invalid["ASN"]] = invalid["Prefixes"]

        return invalids


def _validate_ip(ip_address):
    """Ensures that an IP address is valid

    Args:
        ip_address(str): The IP Address to validate(v4 or v6)

    Returns:
        None

    Raises:
        BGPStuffError: If address is invalid.
    """
    try:
        ipaddress.ip_address(ip_address)
    except ValueError as error:
        raise BGPStuffError("Invalid IP Address") from error


if __name__ == "__main__":
    raise BGPStuffError("This is a library, please do not run directly.")
