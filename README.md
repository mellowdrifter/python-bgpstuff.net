# python-bgpstuff.net

python-bgpstuff.net is a Python library that can access the farious functions on [bgpstuff.net](bgpstuff.net).

## Requirements
```pip install ratelimit requests```

## Simple demo
```>>> import bgpstuff
>>> q = bgpstuff.Response()
>>> q.ip = "4.2.2.1"
>>> q.getRoute()
>>> if q.status_code == 200 and q.exists:
...     print("The route for {} is {}".format(q.ip, q.route))
... 
The route for 4.2.2.1 is 4.0.0.0/9

>>> q.asn = 3356
>>> q.getASName()
>>> if q.status_code == 200 and q.exists:
...     print("The asname for {} is {}".format(q.asn, q.asname))
... 
The asname for 3356 is LEVEL3

>>> q.getTotals()
>>> if q.status_code == 200:
...     print("There are {} IPv4 prefixes and {} IPv6 prefixes in the table.".format(
...         q.total_ipv4, q.total_ipv6))
... 
There are 846425 IPv4 prefixes and 106110 IPv6 prefixes in the table.
```

## Notes
The library has a built in rate limiter to limit 20 requests per minute. If you go over this limit the application will sleep until there is more available requests.

While you could change this in the code, if you do that I'll permananly ban your source IPs.