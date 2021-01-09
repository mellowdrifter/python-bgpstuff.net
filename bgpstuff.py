#!/usr/bin/env python3

import requests
import json
from http.client import responses
from typing import List

baseURL = "https://test.bgpstuff.net"


class Response:

    @property
    def ip(self) -> str:
        return self._ip

    @ip.setter
    def ip(self, ip):
        self._ip = ip

    @property
    def asn(self) -> int:
        return self._asn

    @asn.setter
    def asn(self, asn):
        self._asn = asn

    @property
    def status(self) -> str:
        return responses[self.status_code]

    @property
    def status_code(self) -> int:
        return self._code

    @status_code.setter
    def status_code(self, code):
        self._code = code

    @property
    def exists(self) -> bool:
        return self._exists

    @exists.setter
    def exists(self, exists):
        self._exists = exists

    @property
    def route(self) -> str:
        return self._route

    @route.setter
    def route(self, route):
        self._route = route

    def getRoute(self):
        resp = self.__getRequest("/route/" + self.ip)
        # print(json.dumps(resp.json(), indent=4))
        if self.status_code != 200:
            return
        self.route = resp.json()['Response']['Route']

    @property
    def origin(self) -> str:
        return self._origin

    @origin.setter
    def origin(self, origin):
        self._origin = origin

    def getOrigin(self):
        resp = self.__getRequest("/origin/" + self.ip)
        if self.status_code != 200:
            return
        self.origin = resp.json()['Response']['Origin']

    @property
    def as_path(self) -> List[str]:
        return self._as_path

    @as_path.setter
    def as_path(self, as_path):
        self._as_path = as_path

    @property
    def as_set(self) -> List[str]:
        return self._as_set

    @as_set.setter
    def as_set(self, as_set):
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
        resp = self.__getRequest("/aspath/" + self.ip)
        if self.status_code != 200:
            return
        self.as_path = resp.json()['Response']['ASPath']
        self.as_set = resp.json()['Response']['ASSet']

    @property
    def roa(self):
        return self._roa

    @roa.setter
    def roa(self, roa):
        self._roa = roa

    def getROA(self):
        resp = self.__getRequest("/roa/" + self.ip)
        if self.status_code != 200:
            return
        self.roa = resp.json()['Response']['ROA']

    @property
    def asname(self) -> str:
        return self._asname

    @asname.setter
    def asname(self, asname):
        self._asname = asname

    def getASName(self):
        resp = self.__getRequest("/asname/{}".format(self.asn))
        if self.status_code != 200:
            return
        self.asname = resp.json()['Response']['ASName']

    def __getRequest(self, url):
        resp = requests.get(baseURL + url, headers=getJSONHeader())
        self.status_code = resp.status_code
        # Temp. Once queries working, user will need to check status
        if self.status_code != 200:
            return

        self.exists = resp.json()['Response']['Exists']
        return resp


def getJSONHeader():
    return {'Content-Type': 'application/json'}


if __name__ == "__main__":
    ips = ["1.1.1.1", "4.2.2.1", "123.1.204.0", "11.1.1.1", "10.0.0.0"]
    asns = [123, 3356, 15169, 66000, 3049573045]
    '''for ip in ips:
        q = Response()
        q.ip = ip
        q.getRoute()
        if q.status_code != 200:
            print(q.status + " for " + q.ip)
            break
        if q.exists:
            print(q.route)
        else:
            print("route does not exist for " + q.ip)

    for ip in ips:
        q = Response()
        q.ip = ip
        q.getOrigin()
        if q.status_code != 200:
            print(q.status + " for " + q.ip)
            break
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
            print(q.status + " for " + q.ip)
            break
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
            print(q.status + " for " + q.ip)
            break
        if q.exists:
            print("The roa for {} is {}".format(q.ip, q.roa))
        else:
            print("route does not exist for " + q.ip +
                  " so unable to check the roa")'''

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
