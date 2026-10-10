# python-bgpstuff.net

python-bgpstuff.net is a Python library that interacts with the various BGP routing and RPKI functions available on [bgpstuff.net](https://bgpstuff.net). This version of the library (v3.0.0+) is designed to interface with the brand new **BGPStuff v3 API**.

## Installation

```bash
pip install bgpstuff
```

## Simple Demo

The v3 library is entirely stateless. Methods directly return the JSON response from the API instead of modifying properties on the client object.

```python
import bgpstuff

# Initialize the client. 
# You can optionally pass an API key to access higher rate limits.
client = bgpstuff.Client(api_key="bgs_yourapikeyhere")

# Query a route
route_info = client.get_route("8.8.8.8")
print(route_info)

# Query ROA status
roa_info = client.get_roa("1.1.1.1")
print(roa_info)
```

## Rate Limiting

The BGPStuff v3 API enforces rate limiting server-side. This library features a built-in "smart rate limiter". It tracks the `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers returned by the server on each request.

If you exhaust your allowed requests, the library will intelligently sleep until the reset timestamp *before* making the next request. This ensures you never overwhelm the backend, while seamlessly handling pauses for your application. If a `429 Too Many Requests` is encountered unexpectedly, it will also gracefully back off and retry.

## Documentation

Full documentation for all available endpoints and methods can be found at [https://dev.bgpstuff.net/](https://dev.bgpstuff.net/).