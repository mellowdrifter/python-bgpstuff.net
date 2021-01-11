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
```

## Notes
The library has a built in rate limiter to limit 20 requests per minute. If you go over this limit the application will sleep until there is more available requests.

While you could change this in the code, if you do that I'll permananly ban your source IPs.