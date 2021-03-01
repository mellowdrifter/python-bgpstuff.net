#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python client for the BGPStuff.net REST API.
"""
import bogons
import ipaddress
import requests
from http.client import responses
from ratelimit import limits, sleep_and_retry
from typing import Dict, List, Tuple


_version = "1.0.7"


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
            'User-Agent': f'python-bgpstuff.net/{_version}',
        }
        self.session = self._get_session()
        self._status_code = None
        self._request_id = None
        self._route = None
        self._origin = None
        self._as_name = None
        self._all_as_names = None
        self._as_path = None
        self._as_set = None
        self._roa = None
        self._total_v4 = None
        self._total_v6 = None
        self._sourced = None
        self._all_invalids = None
        self._exists = False

    def _get_session(self):
        """Make a requests session object with the proper headers."""
        session = requests.Session()
        session.headers.update(self.session_headers)

        return session

    def _close_session(self):
        """Closes a session"""
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
    def exists(self) -> bool:
        return self._exists

    @exists.setter
    def exists(self, exists: str):
        if exists == "true":
            self._exists = True
        else:
            self._exists = False

    @property
    def request_id(self) -> str:
        return self._request_id

    @request_id.setter
    def request_id(self, request_id: str):
        self._request_id = request_id

    @property
    def route(self) -> ipaddress.ip_network:
        return self._route

    @route.setter
    def route(self, route: str):
        # TODO: Prevent returning of this value
        if route == "/0":
            return
        try:
            self._route = ipaddress.ip_network(route)
        except:
            raise

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

    @property
    def as_name(self) -> str:
        return self._as_name

    @as_name.setter
    def as_name(self, as_name: str):
        self._as_name = as_name

    @property
    def total_v4(self) -> int:
        return self._total_v4

    @total_v4.setter
    def total_v4(self, total: str):
        self._total_v4 = int(total)

    @property
    def total_v6(self) -> int:
        return self._total_v6

    @total_v6.setter
    def total_v6(self, total: str):
        self._total_v6 = int(total)

    @property
    def sourced(self) -> List[ipaddress.ip_network]:
        return self._sourced

    @sourced.setter
    def sourced(self, prefixes: List[str]):
        self._sourced = []
        for prefix in prefixes:
            try:
                net = ipaddress.ip_network(prefix)
            except:
                raise
            self._sourced.append(net)

    def invalids(self, asn: int) -> List[ipaddress.ip_network]:
        if not self._all_invalids:
            raise BGPStuffError(
                "call get_invalids() before calling get_invalids()")
        if asn in self._all_invalids:
            return self._all_invalids[asn]
        return None

    @property
    def all_invalids(self) -> Dict:
        return self._all_invalids

    @all_invalids.setter
    def all_invalids(self, invalids: Dict):
        self._all_invalids = {}
        for invalid in invalids:
            prefixes = []
            for prefix in invalid["Prefixes"]:
                try:
                    net = ipaddress.ip_network(prefix)
                except:
                    raise
                prefixes.append(net)
            self._all_invalids[int(invalid["ASN"])] = prefixes

    @property
    def all_as_names(self) -> Dict:
        return self._all_as_names

    @all_as_names.setter
    def all_as_names(self, asnames: Dict):
        self._all_as_names = {}
        for asn in asnames:
            self._all_as_names[int(asn["ASN"])] = asn["ASName"]

    @sleep_and_retry
    @limits(calls=30, period=60)
    def _bgpstuff_request(self, endpoint: str):
        """Performs an arbitrary HTTP GET to BGPStuff.

        Args:
            endpoint (str): The REST endpoint to query
        """
        # Reset exists and statuses as the query will fill these with new values.
        self.exists = False
        self.request_id = None

        url = f"{self.url}/{endpoint}"

        request = self.session.get(url)

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise BGPStuffError from error

        self._status_code = request.status_code
        value = request.json()
        if "ID" in value:
            self._request_id = value["ID"]
        if "Exists" in value["Response"]:
            self._exists = value['Response']['Exists']

        return value

    def get_route(self, ip_address: str):
        """Gets the rib entry for the given IP address.

        Args:
            ip_address (str): The IP address to lookup.
        """
        if not bogons.is_public_ip(ip_address):
            raise ValueError(f"{ip_address} is not a public IP address")

        endpoint = "route"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.route = resp["Response"]["Route"]

    def get_origin(self, ip_address: str):
        """Gets the origin AS for the given IP address.

        Args:
            ip_address (str): The IP address to lookup.
        """
        if not bogons.is_public_ip(ip_address):
            raise ValueError(f"{ip_address} is not a public IP address")

        endpoint = "origin"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.origin = resp["Response"]["Origin"]

    def get_as_path(self, ip_address: str):
        """Gets the AS_PATH to the given IP address.

        Args:
            ip_address (str): The IP address to lookup.
        """
        if not bogons.is_public_ip(ip_address):
            raise ValueError(f"{ip_address} is not a public IP address")

        endpoint = "aspath"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.as_path = resp["Response"]["ASPath"]

        if "ASSet" in resp["Response"]:
            self.as_set = resp["Response"]["ASSet"]

    def get_roa(self, ip_address: str):
        """Gets the ROA of the route/prefix containing the given IP address.

        Args:
            ip_address (str): The IP address to lookup.
        """
        if not bogons.is_public_ip(ip_address):
            raise ValueError(f"{ip_address} is not a public IP address")

        endpoint = "roa"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        self.roa = resp["Response"]["ROA"]

    def get_as_name(self, asn: int):
        """Gets the name of the given ASN.

        Args:
            asn (int): The ASN to lookup.
        """
        if not bogons.valid_public_asn(asn):
            raise ValueError(f"{asn} is not a valid ASN")

        # Check local all_asnames first
        if self._all_as_names:
            self._status_code = 200
            if asn in self._all_as_names:
                self._as_name = self._all_as_names[asn]
                self._exists = True
                return
            self._exists = False
            return

        endpoint = "asname"
        resp = self._bgpstuff_request(f"{endpoint}/{asn}")

        self.as_name = resp["Response"]["ASName"]

    def get_sourced_prefixes(self, asn: int):
        """Gets a list of prefixes sourced by the given ASN.

        Args:
            asn (int): The ASN to lookup.
        """
        if not bogons.valid_public_asn(asn):
            raise ValueError(f"{asn} is not a valid ASN")

        endpoint = "sourced"
        resp = self._bgpstuff_request(f"{endpoint}/{asn}")

        self.sourced = resp["Response"]["Sourced"]["Prefixes"]

    def get_totals(self) -> Tuple[int, int]:
        """Gets the total number of prefixes seen by the collector for the
        both IPv4 and IPv6.

        Args:
            None
        """
        endpoint = "totals"
        resp = self._bgpstuff_request(f"{endpoint}")

        self.total_v4 = resp["Response"]["Totals"]["Ipv4"]
        self.total_v6 = resp["Response"]["Totals"]["Ipv6"]

    def get_invalids(self, asn: int = 0):
        """Gets a list of all invalid prefixes observed by the BGPStuff
        route collector.

        Args:
            asn (int): The ASN to lookup. Using 0 means ALL ASNs.
        """
        if asn != 0:
            if not bogons.valid_public_asn(asn):
                raise ValueError(f"{asn} is not a valid ASN")

        endpoint = "invalids"
        if asn == 0:
            resp = self._bgpstuff_request(f"{endpoint}/")
            self.all_invalids = resp["Response"]["Invalids"]
            return

    def get_as_names(self):
        """Gets a list of all asnumber to asname mappings from the
        BGPStuff route collector

        Args:
            None
        """

        endpoint = "asnames"
        resp = self._bgpstuff_request(f"{endpoint}/")
        self.all_as_names = resp["Response"]["ASNames"]


if __name__ == "__main__":
    raise BGPStuffError("This is a library, please do not run directly.")
