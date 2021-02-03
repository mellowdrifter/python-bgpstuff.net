#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python client for the BGPStuff.net API.
"""
import ipaddress
import requests
from ratelimit import limits, sleep_and_retry


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
        self.session_headers = {"Content-Type": "application/json"}
        self.session = self._get_session()

    def _get_session(self):
        """Make a requests session object with the proper headers."""
        session = requests.Session()
        session.headers.update(self.session_headers)

        return session

    @sleep_and_retry
    @limits(calls=30, period=60)
    def _bgpstuff_request(self, endpoint):
        """Performs an arbitrary HTTP GET to BGPStuff.

        Args:
            endpoint (str): The REST endpoint to query

        Returns:
            value (dict): Deserialized JSON response from BGPStuff.
        """
        url = f"{self.url}/{endpoint}"

        request = self.session.get(url)

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise BGPStuffError from error

        value = request.json()

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

        route = resp["Response"]["Route"]

        return route

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

        origin = resp["Response"]["Origin"]

        return origin

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

        as_path = resp["Response"]["ASPath"]

        return as_path

    def get_as_set(self, ip_address):
        """Gets the AS_SET of the route/prefix containing the given IP address.

        Args:
            ip_address (str): The IP address to lookup.

        Returns:
            as_set (str): The AS_PATH to the prefix this IP belongs to.
        TODO: Combine with self.get_as_path()
        """
        _validate_ip(ip_address)

        endpoint = "aspath"
        resp = self._bgpstuff_request(f"{endpoint}/{ip_address}")

        as_set = resp["Response"]["ASSet"]

        return as_set

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

        roa = resp["Response"]["ROA"]

        return roa

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
<<<<<<< HEAD
            sourced_prefixes (list): List of prefixes originated.
        TODO: Add function to validate ASN
        """
        endpoint = "invalids"
        resp = self._bgpstuff_request(f"{endpoint}/")
=======
            resp (json): The JSON returned from the REST endpoint.
        '''
        # Reset exists and statuses as the query will fill these with new values.
        self.exists = False
        self.status_code = 0
        self.status = ""

        resp = requests.get(self.baseURL + url, headers=getRequestHeaders())
        self.status_code = resp.status_code
        if self.status_code != 200:
            return
>>>>>>> upstream/main

        invalid_list = resp["Response"]["Invalids"]

        invalids = {}
        for invalid in invalid_list:
            invalids[invalid["ASN"]] = invalid["Prefixes"]

        return invalids


def _validate_ip(ip_address):
    """Ensures that an IP address is valid

    Args:
        ip_address (str): The IP Address to validate (v4 or v6)

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


# if __name__ == "__main__":
#     ips = ["1.1.1.1", "4.2.2.1", "123.1.204.0",
#            "11.1.1.1", "10.0.0.0", "2600::", "50.114.112.0"]
#     asns = [123, 3356, 15169, 66000, 3049573045]
#     for ip in ips:
#         q = Response()
#         q.ip = ip
#         q.getRoute()
#         if q.status_code != 200:
#             print("{} for {}".format(q.status, q.ip))
#             continue
#         if q.exists:
#             print("The route for {} is {}".format(q.ip, q.route))
#             print("The request ID was {}".format(q.request_id))
#         else:
#             print("route does not exist for " + q.ip)

#     for ip in ips:
#         q = Response()
#         q.ip = ip
#         q.getOrigin()
#         if q.status_code != 200:
#             print("{} for {}".format(q.status, q.ip))
#             continue
#         if q.exists:
#             print("The origin for " + q.ip + " is " + q.origin)
#         else:
#             print("route does not exist for " + q.ip +
#                   " so unable to check the origin")

#     for ip in ips:
#         q = Response()
#         q.ip = ip
#         q.getASPath()
#         if q.status_code != 200:
#             print("{} for {}".format(q.status, q.ip))
#             continue
#         if q.exists:
#             print("The aspath for {} is {}".format(q.ip, q.full_as_path()))
#         else:
#             print("route does not exist for " + q.ip +
#                   " so unable to check the aspath")

#     for ip in ips:
#         q = Response()
#         q.ip = ip
#         q.getROA()
#         if q.status_code != 200:
#             print("{} for {}".format(q.status, q.ip))
#             continue
#         if q.exists:
#             print("The roa for {} is {}".format(q.ip, q.roa))
#         else:
#             print("route does not exist for " + q.ip +
#                   " so unable to check the roa")

#     for asn in asns:
#         q = Response()
#         q.asn = asn
#         q.getASName()
#         if q.status_code != 200:
#             print("{} for {}".format(q.status, q.asn))
#             continue
#         if q.exists:
#             print("The asname for {} is {}".format(q.asn, q.asname))
#         else:
#             print("AS{} does not exist, hence no name".format(q.asn))

#     q = Response()
#     q.getTotals()
#     if q.status_code == 200:
#         print("There are {} IPv4 prefixes and {} IPv6 prefixes in the table.".format(
#             q.total_ipv4, q.total_ipv6))

#     q = Response()
#     q.getInvalids()

#     for i in range(512):
#         inv = q.checkInvalid("{}".format(i + 1))
#         if len(inv) > 0:
#             print("AS{} is originating {} ROA invalid prefixes".format(i+1, len(inv)))

#     for asn in asns:
#         q = Response()
#         q.asn = asn
#         q.getSourced()
#         if q.status_code != 200:
#             print("{} for {}".format(q.status, q.asn))
#             continue
#         if q.exists:
#             print("AS{} is sourcing {} prefixes".format(q.asn, len(q.sourced)))
#         else:
#             print("AS{} does not exist, hence not sourcing any prefixes".format(q.asn))
