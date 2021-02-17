# python-bgpstuff.net

python-bgpstuff.net is a Python library that can access the various functions on [bgpstuff.net](bgpstuff.net).

## Requirements
```pip install bgpstuff```

## Simple demo
```
>>> import bgpstuff
>>> q = bgpstuff.Client()
>>> q.get_route("4.2.2.1")
>>> print(f"The route for 4.2.2.1 is {q.route}")
>>> The route for 4.2.2.1 is 4.0.0.0/9
```

## Notes
The library has a built in rate limiter to limit 30 requests per minute. If you go over this limit the application will sleep until there is more available requests.

While you could change this in the code, if you do that I'll permanently ban your source IPs.

### Documentation
Documentation for installation and all the methods can be found at [https://dev.bgpstuff.net/](https://dev.bgpstuff.net/)