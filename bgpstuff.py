#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import json
from http.client import responses
from ratelimit import limits, sleep_and_retry
from typing import Dict, List, Mapping


class Response:
    """Class Response is an object with all the required methods to
    interact with the REST API portions of bgpstuff.net. The class
    should be reused as it has a built in rate-limiter as long as
    you use the same object"""

    def __init__(self, baseURL=None):
        if baseURL is None:
            self._baseurl = "https://bgpstuff.net"
        else:
            self._baseurl = baseURL

    @property
    def baseURL(self) -> str:
        return self._baseurl

    @property
    def ip(self) -> str:
        return self._ip

    @ip.setter
    def ip(self, ip: str):
        self._ip = ip

    @property
    def asn(self) -> int:
        return self._asn

    @asn.setter
    def asn(self, asn: int):
        self._asn = asn

    @property
    def status(self) -> str:
        return responses[self.status_code]

    @property
    def status_code(self) -> int:
        return self._code

    @status_code.setter
    def status_code(self, code: int):
        self._code = code

    @property
    def request_id(self) -> str:
        return self._id

    @request_id.setter
    def request_id(self, id: str):
        self._id = id

    @property
    def exists(self) -> bool:
        return self._exists

    @exists.setter
    def exists(self, exists: bool):
        self._exists = exists

    @property
    def route(self) -> str:
        return self._route

    @route.setter
    def route(self, route: str):
        self._route = route

    def getRoute(self):
        '''Gets the route prefix for the IP and sets it to the 
        self.route attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/route/" + self.ip)
        if self.status_code != 200:
            return
        self.route = resp.json()['Response']['Route']

    @property
    def origin(self) -> int:
        return self._origin

    @origin.setter
    def origin(self, origin: int):
        self._origin = origin

    def getOrigin(self):
        '''Gets the origin ASN for the IP and sets it to the
        self.origin attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/origin/" + self.ip)
        if self.status_code != 200:
            return
        self.origin = resp.json()['Response']['Origin']

    @property
    def as_path(self) -> List[str]:
        return self._as_path

    @as_path.setter
    def as_path(self, as_path: str):
        self._as_path = as_path

    @property
    def as_set(self) -> List[str]:
        return self._as_set

    @as_set.setter
    def as_set(self, as_set: List[str]):
        self._as_set = as_set

    def full_as_path(self) -> str:
        path = " "
        path = path.join(self.as_path)
        if self.as_set:
            aset = " "
            aset = aset.join(self.as_set)
            aset = " { " + aset
            aset = aset + " }"
            path = path + aset
        return path

    def getASPath(self):
        '''Gets the origin ASPath for the IP and sets it to the
        self.as_path attribute, and gets the AS SET and sets it
        to the self.as_set attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/aspath/" + self.ip)
        if self.status_code != 200:
            return
        self.as_path = resp.json()['Response']['ASPath']
        self.as_set = resp.json()['Response']['ASSet']

    @property
    def roa(self):
        return self._roa

    @roa.setter
    def roa(self, roa: str):
        self._roa = roa

    def getROA(self):
        '''Gets the ROA status for the IP and sets it to the self.roa
        attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/roa/" + self.ip)
        if self.status_code != 200:
            return
        self.roa = resp.json()['Response']['ROA']

    @property
    def asname(self) -> str:
        return self._asname

    @asname.setter
    def asname(self, asname: str):
        self._asname = asname

    def getASName(self):
        '''Gets the ASN Name for the self.asn attribute and sets it to
        the self.asname attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/asname/{}".format(self.asn))
        if self.status_code != 200:
            return
        self.asname = resp.json()['Response']['ASName']

    @property
    def total_ipv4(self) -> int:
        return self._total_ipv4

    @total_ipv4.setter
    def total_ipv4(self, count: int):
        self._total_ipv4 = count

    @property
    def total_ipv6(self) -> int:
        return self._total_ipv6

    @total_ipv6.setter
    def total_ipv6(self, count: int):
        self._total_ipv6 = count

    def getTotals(self):
        '''Gets the total number of routes on the collector and sets it
        to the self.total_ipv[4|6] attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/totals/")
        if self.status_code != 200:
            return
        self.total_ipv4 = resp.json()['Response']['Totals']['Ipv4']
        self.total_ipv6 = resp.json()['Response']['Totals']['Ipv6']

    @property
    def invalids(self) -> Dict:
        return self._invalids

    @invalids.setter
    def invalids(self, invalids: Mapping):
        self._invalids = invalids

    def checkInvalid(self, asn) -> List:
        return self._invalids.get(asn, [])

    def getInvalids(self):
        '''Gets all Invalid prefixes from the Collector and sets them
        to the self.invalids attribute.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/invalids/")
        if self.status_code != 200:
            return
        data = resp.json()['Response']['Invalids']
        invalids = {}
        for d in data:
            invalids[d['ASN']] = d['Prefixes']
        self.invalids = invalids

    @property
    def sourced(self) -> List:
        return self._sourced

    @sourced.setter
    def sourced(self, sourced: List[str]):
        self._sourced = sourced

    def getSourced(self):
        '''Gets the prefixes sourced by the ASN in self.asn. Sets the
        self.sourced attrivute to a list of sourced prefixes.

        Args:
            None

        Returns:
            None
        '''
        resp = self.__getRequest("/sourced/{}".format(self.asn))
        if self.status_code != 200:
            return
        self.sourced = resp.json()['Response']['Sourced']['Prefixes']

    @sleep_and_retry
    @limits(calls=30, period=60)
    def __getRequest(self, url):
        '''Performs an HTTP GET on a given URL and returns the response.

        Args:
            url (str): The REST endpoint to get. 

        Returns:
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

        # Grab the request ID
        # TODO: request_id should come even if there is a server error, if server is reachable!
        self.request_id = resp.json()['ID']

        #print(json.dumps(resp.json(), indent=4))
        self.exists = resp.json()['Response']['Exists']
        return resp


def getRequestHeaders() -> Dict:
    '''Returns the HTTP Header Parameters

        Args:
            None

        Returns:
            header (dict): The HTTP Headers, including both
            setting the request to json and setting the
            user agent.
    '''
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'python-bgpstuff.net/x.x.x',
    }


if __name__ == "__main__":
    ips = ["1.1.1.1", "4.2.2.1", "123.1.204.0",
           "11.1.1.1", "10.0.0.0", "2600::", "50.114.112.0"]
    asns = [123, 3356, 15169, 66000, 3049573045]
    for ip in ips:
        q = Response()
        q.ip = ip
        q.getRoute()
        if q.status_code != 200:
            print("{} for {}".format(q.status, q.ip))
            continue
        if q.exists:
            print("The route for {} is {}".format(q.ip, q.route))
            print("The request ID was {}".format(q.request_id))
        else:
            print("route does not exist for " + q.ip)

    for ip in ips:
        q = Response()
        q.ip = ip
        q.getOrigin()
        if q.status_code != 200:
            print("{} for {}".format(q.status, q.ip))
            continue
        if q.exists:
            print("The origin for " + q.ip + " is " + q.origin)
        else:
            print("route does not exist for " + q.ip +
                  " so unable to check the origin")

    for ip in ips:
        q = Response()
        q.ip = ip
        q.getASPath()
        if q.status_code != 200:
            print("{} for {}".format(q.status, q.ip))
            continue
        if q.exists:
            print("The aspath for {} is {}".format(q.ip, q.full_as_path()))
        else:
            print("route does not exist for " + q.ip +
                  " so unable to check the aspath")

    for ip in ips:
        q = Response()
        q.ip = ip
        q.getROA()
        if q.status_code != 200:
            print("{} for {}".format(q.status, q.ip))
            continue
        if q.exists:
            print("The roa for {} is {}".format(q.ip, q.roa))
        else:
            print("route does not exist for " + q.ip +
                  " so unable to check the roa")

    for asn in asns:
        q = Response()
        q.asn = asn
        q.getASName()
        if q.status_code != 200:
            print("{} for {}".format(q.status, q.asn))
            continue
        if q.exists:
            print("The asname for {} is {}".format(q.asn, q.asname))
        else:
            print("AS{} does not exist, hence no name".format(q.asn))

    q = Response()
    q.getTotals()
    if q.status_code == 200:
        print("There are {} IPv4 prefixes and {} IPv6 prefixes in the table.".format(
            q.total_ipv4, q.total_ipv6))

    q = Response()
    q.getInvalids()

    for i in range(512):
        inv = q.checkInvalid("{}".format(i + 1))
        if len(inv) > 0:
            print("AS{} is originating {} ROA invalid prefixes".format(i+1, len(inv)))

    for asn in asns:
        q = Response()
        q.asn = asn
        q.getSourced()
        if q.status_code != 200:
            print("{} for {}".format(q.status, q.asn))
            continue
        if q.exists:
            print("AS{} is sourcing {} prefixes".format(q.asn, len(q.sourced)))
        else:
            print("AS{} does not exist, hence not sourcing any prefixes".format(q.asn))
