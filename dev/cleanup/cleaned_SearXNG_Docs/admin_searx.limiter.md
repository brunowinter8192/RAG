<!-- source: https://docs.searxng.org/admin/searx.limiter.html -->

# Limiter
> **Info:**
The limiter requires a [Valkey](https://docs.searxng.org/admin/settings/settings_valkey.html#settings-valkey) database.
Bot protection / IP rate limitation. The intention of rate limitation is to limit suspicious requests from an IP. The motivation behind this is the fact that SearXNG passes through requests from bots and is thus classified as a bot itself. As a result, the SearXNG engine then receives a CAPTCHA or is blocked by the search engine (the origin) in some other way.
To avoid blocking, the requests from bots to SearXNG must also be blocked, this is the task of the limiter. To perform this task, the limiter uses the methods from the [Bot Detection](https://docs.searxng.org/src/searx.botdetection.html#botdetection):
  * Analysis of the HTTP header in the request / [Probe HTTP headers](https://docs.searxng.org/src/searx.botdetection.html#botdetection-probe-headers) can be easily bypassed.
  * Block and pass lists in which IPs are listed / [IP lists](https://docs.searxng.org/src/searx.botdetection.html#botdetection-ip-lists) are hard to maintain, since the IPs of bots are not all known and change over the time.
  * Detection & dynamically [Rate limit](https://docs.searxng.org/src/searx.botdetection.html#botdetection-rate-limit) of bots based on the behavior of the requests. For dynamically changeable IP lists a Valkey database is needed.

The prerequisite for IP based methods is the correct determination of the IP of the client. The IP of the client is determined via the [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) HTTP header.
Attention
A correct setup of the HTTP request headers `X-Forwarded-For` and `X-Real-IP` is essential to be able to assign a request to an IP correctly:
## Enable Limiter
To enable the limiter activate:
```
server:
  ...
  limiter: true  # rate limit the number of request on the instance, block some bots

```

and set the valkey-url connection. Check the value, it depends on your valkey DB (see [valkey:](https://docs.searxng.org/admin/settings/settings_valkey.html#settings-valkey)), by example:
```
valkey:
  url: valkey://localhost:6379/0

```

## Configure Limiter
The methods of [Bot Detection](https://docs.searxng.org/src/searx.botdetection.html#botdetection) the limiter uses are configured in a local file `/etc/searxng/limiter.toml`. The defaults are shown in [limiter.toml](https://docs.searxng.org/admin/searx.limiter.html#limiter-toml) / Don’t copy all values to your local configuration, just enable what you need by overwriting the defaults. For instance to activate the `link_token` method in the [Method ip_limit](https://docs.searxng.org/src/searx.botdetection.html#botdetection-ip-limit) you only need to set this option to `true`:
```
[botdetection.ip_limit]
link_token = true

```

## `limiter.toml`
In this file the limiter finds the configuration of the [Bot Detection](https://docs.searxng.org/src/searx.botdetection.html#botdetection):
```
[botdetection]

# The prefix defines the number of leading bits in an address that are compared
# to determine whether or not an address is part of a (client) network.

ipv4_prefix = 32
ipv6_prefix = 48

# If the request IP is in trusted_proxies list, the client IP address is
# extracted from the X-Forwarded-For and X-Real-IP headers. This should be
# used if SearXNG is behind a reverse proxy or load balancer.

trusted_proxies = [
  '127.0.0.0/8',
  '::1',
  # '192.168.0.0/16',
  # '172.16.0.0/12',
  # '10.0.0.0/8',
  # 'fd00::/8',
]

[botdetection.ip_limit]

# To get unlimited access in a local network, by default link-local addresses
# (networks) are not monitored by the ip_limit
filter_link_local = false

# activate link_token method in the ip_limit method
link_token = false

[botdetection.ip_lists]

# In the limiter, the ip_lists method has priority over all other methods -> if
# an IP is in the pass_ip list, it has unrestricted access and it is also not
# checked if e.g. the "user agent" suggests a bot (e.g. curl).

block_ip = [
  # '93.184.216.34',  # IPv4 of example.org
  # '257.1.1.1',      # invalid IP --> will be ignored, logged in ERROR class
]

pass_ip = [
  # '192.168.0.0/16',      # IPv4 private network
  # 'fe80::/10'            # IPv6 linklocal / wins over botdetection.ip_limit.filter_link_local
]

# Activate passlist of (hardcoded) IPs from the SearXNG organization,
# e.g. `check.searx.space`.
pass_searxng_org = true

```

## Implementation
**limiter.LIMITER_CFG_SCHEMA** = `PosixPath('/home/runner/work/searxng/searxng/searx/limiter.toml')`
Base configuration (schema) of the botdetection. 

searx.limiter.get_cfg() → [Config](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config "searx.botdetection.config.Config") 
    
Returns SearXNG’s global limiter configuration. 

**limiter.pre_request()**
See [`flask.Flask.before_request`](https://flask.palletsprojects.com/en/stable/api/#flask.Flask.before_request "\(in Flask v3.1.x\)") 

**limiter.is_installed()**
Returns `True` if limiter is active and a valkey DB is available. 

searx.limiter.initialize(_app :[Flask](https://flask.palletsprojects.com/en/stable/api/#flask.Flask "\(in Flask v3.1.x\)")_, _settings_) 
    
Install the limiter
