<!-- source: https://docs.searxng.org/src/searx.botdetection.html -->

# Bot Detection
searx.botdetection.get_network(_real_ip :[IPv4Address](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address "\(in Python v3.14\)")|[IPv6Address](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address "\(in Python v3.14\)")_, _cfg :[config.Config](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config "searx.botdetection.config.Config")_) → [IPv4Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network "\(in Python v3.14\)")|[IPv6Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network "\(in Python v3.14\)") 
    
Returns the (client) network of whether the `real_ip` is part of.
The `ipv4_prefix` and `ipv6_prefix` define the number of leading bits in an address that are compared to determine whether or not an address is part of a (client) network.
```
[botdetection]

ipv4_prefix = 32
ipv6_prefix = 48

```

searx.botdetection.too_many_requests(_network :[IPv4Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network "\(in Python v3.14\)")|[IPv6Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network "\(in Python v3.14\)")_, _log_msg :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [Response](https://werkzeug.palletsprojects.com/en/stable/wrappers/#werkzeug.wrappers.Response "\(in Werkzeug v3.1.x\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns a HTTP 429 response object and writes a ERROR message to the ‘botdetection’ logger. This function is used in part by the filter methods to return the default `Too Many Requests` response. 

_class_ searx.botdetection.ProxyFix(_wsgi_app :WSGIApplication_) 
    
A middleware like the [ProxyFix](https://werkzeug.palletsprojects.com/middleware/proxy_fix/) class, where the `x_for` argument is replaced by a method that determines the number of trusted proxies via the `botdetection.trusted_proxies` setting.
[`flask.Request.remote_addr`](https://flask.palletsprojects.com/en/stable/api/#flask.Request.remote_addr "\(in Flask v3.1.x\)")
SearXNG uses Werkzeug’s [ProxyFix](https://werkzeug.palletsprojects.com/middleware/proxy_fix/) (with it default `x_for=1`).
The remote IP ([`flask.Request.remote_addr`](https://flask.palletsprojects.com/en/stable/api/#flask.Request.remote_addr "\(in Flask v3.1.x\)")) of the request is taken from (first match):
  * [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For): If the header is set, the first untrusted IP that comes before the IPs that are still part of the `botdetection.trusted_proxies` is used.
  * [X-Real-IP](https://github.com/searxng/searxng/issues/1237#issuecomment-1147564516): If [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) is not set, X-Real-IP is used (`botdetection.trusted_proxies` is ignored).

If none of the header is set, the [REMOTE_ADDR](https://wsgi.readthedocs.io/en/latest/proposals-2.0.html#making-some-keys-required) from the WSGI layer is used. If (for whatever reasons) none IP can be determined, an error message is displayed and `100::` is used instead ([**RFC 6666**](https://datatracker.ietf.org/doc/html/rfc6666.html)).
## IP lists
### Method `ip_lists`
The `ip_lists` method implements [`block-list`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_lists.block_ip "searx.botdetection.ip_lists.block_ip") and [`pass-list`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_lists.pass_ip "searx.botdetection.ip_lists.pass_ip").
```
[botdetection.ip_lists]

pass_ip = [
  '167.235.158.251', # IPv4 of check.searx.space
  '192.168.0.0/16',  # IPv4 private network
  'fe80::/10',       # IPv6 linklocal
]

block_ip = [
  '93.184.216.34',   # IPv4 of example.org
  '257.1.1.1',       # invalid IP --> will be ignored, logged in ERROR class
]

```

**botdetection.ip_lists.SEARXNG_ORG** = `['167.235.158.251', '2a01:04f8:1c1c:8fc2::/64']`
Passlist of IPs from the SearXNG organization, e.g. check.searx.space. 

searx.botdetection.ip_lists.pass_ip(_real_ip :[IPv4Address](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address "\(in Python v3.14\)")|[IPv6Address](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address "\(in Python v3.14\)")_, _cfg :[Config](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config "searx.botdetection.config.Config")_) → [Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple "\(in Python v3.14\)")[[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Checks if the IP on the subnet is in one of the members of the `botdetection.ip_lists.pass_ip` list. 

searx.botdetection.ip_lists.block_ip(_real_ip :[IPv4Address](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address "\(in Python v3.14\)")|[IPv6Address](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address "\(in Python v3.14\)")_, _cfg :[Config](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config "searx.botdetection.config.Config")_) → [Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple "\(in Python v3.14\)")[[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Checks if the IP on the subnet is in one of the members of the `botdetection.ip_lists.block_ip` list.
## Rate limit
### Method `ip_limit`
The `ip_limit` method counts request from an IP in _sliding windows_. If there are to many requests in a sliding window, the request is evaluated as a bot request. This method requires a valkey DB and needs a HTTP [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) header. To take privacy only the hash value of an IP is stored in the valkey DB and at least for a maximum of 10 minutes.
The [`link_token`](https://docs.searxng.org/src/searx.botdetection.html#module-searx.botdetection.link_token "searx.botdetection.link_token") method can be used to investigate whether a request is _suspicious_. To activate the [`link_token`](https://docs.searxng.org/src/searx.botdetection.html#module-searx.botdetection.link_token "searx.botdetection.link_token") method in the [`ip_limit`](https://docs.searxng.org/src/searx.botdetection.html#module-searx.botdetection.ip_limit "searx.botdetection.ip_limit") method add the following configuration:
```
[botdetection.ip_limit]
link_token = true

```

If the [`link_token`](https://docs.searxng.org/src/searx.botdetection.html#module-searx.botdetection.link_token "searx.botdetection.link_token") method is activated and a request is _suspicious_ the request rates are reduced:
  * [`BURST_MAX`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.BURST_MAX "searx.botdetection.ip_limit.BURST_MAX") -> [`BURST_MAX_SUSPICIOUS`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.BURST_MAX_SUSPICIOUS "searx.botdetection.ip_limit.BURST_MAX_SUSPICIOUS")
  * [`LONG_MAX`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.LONG_MAX "searx.botdetection.ip_limit.LONG_MAX") -> [`LONG_MAX_SUSPICIOUS`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.LONG_MAX_SUSPICIOUS "searx.botdetection.ip_limit.LONG_MAX_SUSPICIOUS")

To intercept bots that get their IPs from a range of IPs, there is a [`SUSPICIOUS_IP_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.SUSPICIOUS_IP_WINDOW "searx.botdetection.ip_limit.SUSPICIOUS_IP_WINDOW"). In this window the suspicious IPs are stored for a longer time. IPs stored in this sliding window have a maximum of [`SUSPICIOUS_IP_MAX`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.SUSPICIOUS_IP_MAX "searx.botdetection.ip_limit.SUSPICIOUS_IP_MAX") accesses before they are blocked. As soon as the IP makes a request that is not suspicious, the sliding window for this IP is dropped. 

**botdetection.ip_limit.BURST_WINDOW** = `20`
Time (sec) before sliding window for _burst_ requests expires. 

**botdetection.ip_limit.BURST_MAX** = `15`
Maximum requests from one IP in the [`BURST_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.BURST_WINDOW "searx.botdetection.ip_limit.BURST_WINDOW") 

**botdetection.ip_limit.BURST_MAX_SUSPICIOUS** = `2`
Maximum of suspicious requests from one IP in the [`BURST_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.BURST_WINDOW "searx.botdetection.ip_limit.BURST_WINDOW") 

**botdetection.ip_limit.LONG_WINDOW** = `600`
Time (sec) before the longer sliding window expires. 

**botdetection.ip_limit.LONG_MAX** = `150`
Maximum requests from one IP in the [`LONG_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.LONG_WINDOW "searx.botdetection.ip_limit.LONG_WINDOW") 

**botdetection.ip_limit.LONG_MAX_SUSPICIOUS** = `10`
Maximum suspicious requests from one IP in the [`LONG_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.LONG_WINDOW "searx.botdetection.ip_limit.LONG_WINDOW") 

**botdetection.ip_limit.API_WINDOW** = `3600`
Time (sec) before sliding window for API requests (format != html) expires. 

**botdetection.ip_limit.API_MAX** = `4`
Maximum requests from one IP in the [`API_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.API_WINDOW "searx.botdetection.ip_limit.API_WINDOW") 

**botdetection.ip_limit.SUSPICIOUS_IP_WINDOW** = `2592000`
Time (sec) before sliding window for one suspicious IP expires. 

**botdetection.ip_limit.SUSPICIOUS_IP_MAX** = `3`
Maximum requests from one suspicious IP in the [`SUSPICIOUS_IP_WINDOW`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.ip_limit.SUSPICIOUS_IP_WINDOW "searx.botdetection.ip_limit.SUSPICIOUS_IP_WINDOW").
### Method `link_token`
The `link_token` method evaluates a request as [`suspicious`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.link_token.is_suspicious "searx.botdetection.link_token.is_suspicious") if the URL `/client<token>.css` is not requested by the client. By adding a random component (the token) in the URL, a bot can not send a ping by request a static URL.
Note
This method requires a valkey DB and needs a HTTP [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) header.
To get in use of this method a flask URL route needs to be added:
```
@app.route('/client<token>.css', methods=['GET', 'POST'])
def client_token(token=None):
    link_token.ping(request, token)
    return Response('', mimetype='text/css')

```

And in the HTML template from flask a stylesheet link is needed (the value of `link_token` comes from [`get_token`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.link_token.get_token "searx.botdetection.link_token.get_token")):
```
<link rel="stylesheet"
      href="{{ url_for('client_token', token=link_token) }}"
      type="text/css" >

```

**botdetection.link_token.TOKEN_LIVE_TIME** = `600`
Lifetime (sec) of limiter’s CSS token. 

**botdetection.link_token.PING_LIVE_TIME** = `3600`
Lifetime (sec) of the ping-key from a client (request) 

**botdetection.link_token.PING_KEY** = `'SearXNG_limiter.ping'`
Prefix of all ping-keys generated by [`get_ping_key`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.link_token.get_ping_key "searx.botdetection.link_token.get_ping_key") 

**botdetection.link_token.TOKEN_KEY** = `'SearXNG_limiter.token'`
Key for which the current token is stored in the DB 

searx.botdetection.link_token.is_suspicious(_network :[IPv4Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network "\(in Python v3.14\)")|[IPv6Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network "\(in Python v3.14\)")_, _request :[Request](https://flask.palletsprojects.com/en/stable/api/#flask.Request "\(in Flask v3.1.x\)")_, _renew :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Checks whether a valid ping is exists for this (client) network, if not this request is rated as _suspicious_. If a valid ping exists and argument `renew` is `True` the expire time of this ping is reset to [`PING_LIVE_TIME`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.link_token.PING_LIVE_TIME "searx.botdetection.link_token.PING_LIVE_TIME"). 

searx.botdetection.link_token.ping(_request :[Request](https://flask.palletsprojects.com/en/stable/api/#flask.Request "\(in Flask v3.1.x\)")_, _token :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
This function is called by a request to URL `/client<token>.css`. If `token` is valid a [`PING_KEY`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.link_token.PING_KEY "searx.botdetection.link_token.PING_KEY") for the client is stored in the DB. The expire time of this ping-key is [`PING_LIVE_TIME`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.link_token.PING_LIVE_TIME "searx.botdetection.link_token.PING_LIVE_TIME"). 

searx.botdetection.link_token.get_ping_key(_network :[IPv4Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network "\(in Python v3.14\)")|[IPv6Network](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network "\(in Python v3.14\)")_, _request :[Request](https://flask.palletsprojects.com/en/stable/api/#flask.Request "\(in Flask v3.1.x\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Generates a hashed key that fits (more or less) to a _WEB-browser session_ in a network. 

searx.botdetection.link_token.get_token() → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Returns current token. If there is no currently active token a new token is generated randomly and stored in the Valkey DB. Without without a database connection, string “12345678” is returned.
## Probe HTTP headers
### Method `http_accept`
The `http_accept` method evaluates a request as the request of a bot if the [Accept](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept) header ..
  * did not contain `text/html`

### Method `http_accept_encoding`
The `http_accept_encoding` method evaluates a request as the request of a bot if the [Accept-Encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding) header ..
  * did not contain `gzip` AND `deflate` (if both values are missed)
  * did not contain `text/html`

### Method `http_accept_language`
The `http_accept_language` method evaluates a request as the request of a bot if the [Accept-Language](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent) header is unset.
### Method `http_connection`
The `http_connection` method evaluates a request as the request of a bot if the [Connection](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection) header is set to `close`.
### Method `http_user_agent`
The `http_user_agent` method evaluates a request as the request of a bot if the [User-Agent](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent) header is unset or matches the regular expression [`USER_AGENT`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.http_user_agent.USER_AGENT "searx.botdetection.http_user_agent.USER_AGENT"). 

**botdetection.http_user_agent.USER_AGENT** = `'(unknown|[Cc][Uu][Rr][Ll]|[wW]get|Scrapy|splash|JavaFX|FeedFetcher|python-requests|Go-http-client|Java|Jakarta|okhttp|HttpClient|Jersey|Python|libwww-perl|Ruby|SynHttpClient|UniversalFeedParser|Googlebot|GoogleImageProxy|bingbot|Baiduspider|yacybot|YandexMobileBot|YandexBot|Yahoo! Slurp|MJ12bot|AhrefsBot|archive.org_bot|msnbot|MJ12bot|SeznamBot|linkdexbot|Netvibes|SMTBot|zgrab|James BOT|Sogou|Abonti|Pixray|Spinn3r|SemrushBot|Exabot|ZmEu|BLEXBot|bitlybot|HeadlessChrome|Mozilla/5\\\\.0\\\ \\\\(compatible;\\\ Farside/0\\\\.1\\\\.0;\\\ \\\\+https://farside\\\\.link\\\\)|.*PetalBot.*)'`
Regular expression that matches to [User-Agent](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent) from known _bots_
### Method `http_sec_fetch`
The `http_sec_fetch` method protect resources from web attacks with [Fetch Metadata](https://developer.mozilla.org/en-US/docs/Glossary/Fetch_metadata_request_header). A request is filtered out in case of:
  * http header [Sec-Fetch-Mode](https://developer.mozilla.org/en-US/docs/Web/API/Request/mode) is invalid
  * http header [Sec-Fetch-Dest](https://developer.mozilla.org/en-US/docs/Web/API/Request/destination) is invalid

searx.botdetection.http_sec_fetch.is_browser_supported(_user_agent :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Check if the browser supports Sec-Fetch headers.
<https://caniuse.com/mdn-http_headers_sec-fetch-dest> <https://caniuse.com/mdn-http_headers_sec-fetch-mode> <https://caniuse.com/mdn-http_headers_sec-fetch-site>
Supported browsers: - Chrome >= 80 - Firefox >= 90 - Safari >= 16.4 - Edge (mirrors Chrome) - Opera (mirrors Chrome)
## Config
Configuration class [`Config`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config "searx.botdetection.config.Config") with deep-update, schema validation and deprecated names.
The [`Config`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config "searx.botdetection.config.Config") class implements a configuration that is based on structured dictionaries. The configuration schema is defined in a dictionary structure and the configuration data is given in a dictionary structure. 

_class_ searx.botdetection.config.Config(_cfg_schema :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_, _deprecated :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) 
    
Base class used for configuration 

validate(_cfg :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) 
    
Validation of dictionary `cfg` on `Config.SCHEMA`. Validation is done by [`validate`](https://docs.searxng.org/src/searx.botdetection.html#searx.botdetection.config.Config.validate "searx.botdetection.config.Config.validate"). 

update(_upd_cfg :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) 
    
Update this configuration by `upd_cfg`. 

default(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Returns default value of field `name` in `self.cfg_schema`. 

get(_name: str_, _default: ~typing.Any = <UNSET>_, _replace: bool = True_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Returns the value to which `name` points in the configuration.
If there is no such `name` in the config and the `default` is `UNSET`, a [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError "\(in Python v3.14\)") is raised. 

set(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _val :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_) 
    
Set the value to which `name` points in the configuration.
If there is no such `name` in the config, a [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError "\(in Python v3.14\)") is raised. 

path(_name: str_, _default: ~typing.Any = <UNSET>_) 
    
Get a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)") object from a config string. 

pyobj(_name: str_, _default: ~typing.Any = <UNSET>_) 
    
Get python object referred by full qualiffied name (FQN) in the config string. 

_final exception_searx.botdetection.config.SchemaIssue(_level :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['warn','invalid']_, _msg :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Exception to store and/or raise a message from a schema issue.
