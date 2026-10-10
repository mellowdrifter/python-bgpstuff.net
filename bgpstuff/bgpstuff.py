#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python client for the BGPStuff.net REST API."""

import bogons
import ipaddress
import requests
import time
import warnings
from cachetools import cached, TTLCache
from http.client import responses
from typing import Any, Dict, List, Optional

_version = "3.0.0"
TEN_MINUTES = 10 * 60
ONE_HOUR = 6 * TEN_MINUTES

class BGPStuffError(Exception):
    """GenericError Class for all BGPStuff Client Errors."""

class Client:
    """Class Client is an object with all the required methods to
    interact with the REST API portions of bgpstuff.net. The class
    should be reused to benefit from connection pooling and smart rate limiting.

    Args:
        url (str): The BGPStuff instance to query against.
        api_key (str, optional): API key for authenticated requests.
    """

    def __init__(self, url="https://bgpstuff.net", api_key=None):
        self._url = url
        if "/v1" in self._url or "/v2" in self._url:
            warnings.warn(
                "The bgpstuff.net v1 and v2 APIs are deprecated and no longer available. "
                "Please upgrade to v3. Update your base_url or install the latest version of this library.",
                DeprecationWarning,
                stacklevel=2,
            )
        self._api_key = api_key
        self._session_headers = {
            "Content-Type": "application/json",
            "User-Agent": f"python-bgpstuff.net/{_version}",
        }
        if api_key:
            self._session_headers["Authorization"] = f"Bearer {api_key}"
            
        self._session = self._get_session()
        self._status_code = None
        self._request_id = None
        self._cache_status = None
        
        # State for smart rate limiting
        self._ratelimit_remaining = None
        self._ratelimit_reset = None

    def _get_session(self):
        """Make a requests session object with the proper headers."""
        session = requests.Session()
        session.headers.update(self._session_headers)
        return session

    def _close_session(self):
        """Closes a session"""
        self._session.close()

    @property
    def status(self) -> str:
        if self._status_code is None:
            return ""
        return responses.get(self._status_code, "Unknown Status Code")

    @property
    def status_code(self) -> Optional[int]:
        return self._status_code

    @property
    def request_id(self) -> Optional[str]:
        return self._request_id
        
    @property
    def cache_status(self) -> Optional[str]:
        return self._cache_status

    def _validate_ip_or_prefix(self, ip_or_prefix: str):
        try:
            net = ipaddress.ip_network(ip_or_prefix, strict=False)
            if not bogons.is_public_ip(str(net.network_address)):
                raise ValueError(f"{ip_or_prefix} contains a bogon or private address")
        except ValueError as e:
            raise ValueError(f"{ip_or_prefix} is not a valid public IP address or prefix: {e}")

    def _bgpstuff_request(self, endpoint: str) -> Any:
        """Performs an HTTP GET to BGPStuff with smart rate limiting.

        Args:
            endpoint (str): The REST endpoint to query
        """
        self._request_id = None
        self._status_code = None
        self._cache_status = None

        url = f"{self._url}/api/v3/{endpoint}"
        
        # Smart Rate Limiting Pre-emption
        if self._ratelimit_remaining is not None and self._ratelimit_remaining <= 0:
            if self._ratelimit_reset is not None:
                sleep_time = max(0, int(self._ratelimit_reset) - int(time.time()))
                if sleep_time > 0:
                    time.sleep(sleep_time + 1)

        max_retries = 3
        backoff_factor = 2

        for attempt in range(max_retries + 1):
            request = self._session.get(url)
            self._status_code = request.status_code
            self._request_id = request.headers.get("X-Request-ID")
            self._cache_status = request.headers.get("X-Cache")
            
            remaining = request.headers.get("X-RateLimit-Remaining")
            if remaining is not None:
                self._ratelimit_remaining = int(remaining)
            reset_ts = request.headers.get("X-RateLimit-Reset")
            if reset_ts is not None:
                self._ratelimit_reset = int(reset_ts)
            
            if request.status_code == 429:
                if reset_ts:
                    sleep_time = max(0, int(reset_ts) - int(time.time())) + 1
                else:
                    sleep_time = backoff_factor ** attempt
                    
                if attempt < max_retries:
                    time.sleep(sleep_time)
                    continue
                else:
                    raise BGPStuffError("Rate limit exceeded and max retries reached.")

            if request.status_code == 404:
                return None

            try:
                request.raise_for_status()
            except requests.exceptions.HTTPError as error:
                try:
                    error_msg = request.json().get("error", str(error))
                except Exception:
                    error_msg = str(error)
                raise BGPStuffError(f"HTTP Error {request.status_code}: {error_msg}") from error

            return request.json()

    def get_route(self, ip_address: str) -> Optional[Dict]:
        """Gets the rib entry for the given IP address or prefix."""
        self._validate_ip_or_prefix(ip_address)
        return self._bgpstuff_request(f"route/{ip_address}")

    def get_origin(self, ip_address: str) -> Optional[Dict]:
        """Gets the origin AS for the given IP address or prefix."""
        self._validate_ip_or_prefix(ip_address)
        return self._bgpstuff_request(f"origin/{ip_address}")

    def get_as_path(self, ip_address: str) -> Optional[Dict]:
        """Gets the AS_PATH to the given IP address or prefix."""
        self._validate_ip_or_prefix(ip_address)
        return self._bgpstuff_request(f"aspath/{ip_address}")

    def get_roa(self, ip_address: str) -> Optional[Dict]:
        """Gets the ROA of the route/prefix containing the given IP address or prefix."""
        self._validate_ip_or_prefix(ip_address)
        return self._bgpstuff_request(f"roa/{ip_address}")

    def get_as_name(self, asn: int) -> Optional[Dict]:
        """Gets the name of the given ASN."""
        if not bogons.valid_public_asn(asn):
            raise ValueError(f"{asn} is not a valid ASN")
        return self._bgpstuff_request(f"asname/{asn}")

    def get_geoip(self, ip_address: str) -> Optional[Dict]:
        """Gets the geo location of the IP address."""
        if ip_address != "self":
            self._validate_ip_or_prefix(ip_address)
        return self._bgpstuff_request(f"geoip/{ip_address}")

    def get_sourced_prefixes(self, asn: int) -> Optional[Dict]:
        """Gets a list of prefixes sourced by the given ASN."""
        if not bogons.valid_public_asn(asn):
            raise ValueError(f"{asn} is not a valid ASN")
        return self._bgpstuff_request(f"sourced/{asn}")

    def get_vrps(self, asn: int):
        """Deprecated in v3 API."""
        raise NotImplementedError("VRPs are not supported in the v3 API.")

    def get_totals(self):
        """Deprecated standalone endpoint in v3 API."""
        raise NotImplementedError("Totals are not yet implemented in the v3 API.")

    def get_community(self, high: int, low: int) -> Optional[Dict]:
        """Gets routes matching a standard community (high:low)."""
        return self._bgpstuff_request(f"community/{high}:{low}")

    def get_large_community(self, global_admin: int, local_data1: int, local_data2: int) -> Optional[Dict]:
        """Gets routes matching a large community."""
        return self._bgpstuff_request(f"large-community/{global_admin}:{local_data1}:{local_data2}")

    def get_aspath_search(self, regex: str) -> Optional[Dict]:
        """Gets routes whose AS_PATH matches the regex. Requires Auth."""
        # Using requests' params to properly URL-encode the regex
        # We need to adjust _bgpstuff_request or append it manually.
        # Since it's the only one with query string, doing it manually is simple:
        import urllib.parse
        encoded_regex = urllib.parse.quote(regex)
        return self._bgpstuff_request(f"aspath-search?regex={encoded_regex}")

    def get_peers(self) -> Optional[Dict]:
        """Gets summary of peers."""
        return self._bgpstuff_request("peers")

    def get_masks(self) -> Optional[Dict]:
        """Gets subnet mask distribution."""
        return self._bgpstuff_request("masks")

    def get_whereami(self) -> Optional[Dict]:
        """Gets metadata about the caller."""
        return self._bgpstuff_request("whereami")

    def get_stats(self) -> Optional[Dict]:
        """Gets time-series stats including totals."""
        return self._bgpstuff_request("stats")

    @cached(cache=TTLCache(maxsize=1, ttl=TEN_MINUTES))
    def get_invalids(self, asn: int = 0) -> Optional[Dict]:
        """Gets a list of all invalid prefixes. Requires Auth."""
        if asn != 0:
            if not bogons.valid_public_asn(asn):
                raise ValueError(f"{asn} is not a valid ASN")
            return self._bgpstuff_request(f"invalids/{asn}")
        return self._bgpstuff_request("invalids")

    @cached(cache=TTLCache(maxsize=1, ttl=ONE_HOUR))
    def get_as_names(self) -> Optional[Dict]:
        """Gets a list of all asnumber to asname mappings. Requires Auth."""
        return self._bgpstuff_request("asnames")

if __name__ == "__main__":
    raise BGPStuffError("This is a library, please do not run directly.")
