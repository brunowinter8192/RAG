<!-- source: https://docs.searxng.org/src/searx.favicons.html -->

# Favicons (source)
Implementations for providing the favicons in SearXNG.
There is a command line for developer purposes and for deeper analysis. Here is an example in which the command line is called in the development environment:
```
$ ./manage pyenv.cmd bash --norc --noprofile
(py3) python -m searx.favicons --help

```

searx.favicons.favicon_url(_authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Function to generate the image URL used for favicons in SearXNG’s result lists. The `authority` argument (aka netloc / [**RFC 3986**](https://datatracker.ietf.org/doc/html/rfc3986.html)) is usually a (sub-) domain name. This function is used in the HTML (jinja) templates.
```
<div class="favicon">
   <img src="{{ favicon_url(result.parsed_url.netloc) }}">
</div>

```

The returned URL is a route to [`favicon_proxy`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.favicon_proxy "searx.favicons.favicon_proxy") REST API.
If the favicon is already in the cache, the returned URL is a [data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs) (something like `data:image/png;base64,...`). By generating a data url from the [`cache.FaviconCache`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCache "searx.favicons.cache.FaviconCache"), additional HTTP roundtripps via the [`favicon_proxy`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.favicon_proxy "searx.favicons.favicon_proxy") are saved. However, it must also be borne in mind that data urls are not cached in the client (web browser). 

**favicons.favicon_proxy()**
REST API of SearXNG’s favicon proxy service
```
/favicon_proxy?authority=<...>&h=<...>

```

`authority`:
    
Domain name [**RFC 3986**](https://datatracker.ietf.org/doc/html/rfc3986.html) / see [`favicon_url`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.favicon_url "searx.favicons.favicon_url") 

`h`:
    
HMAC [**RFC 2104**](https://datatracker.ietf.org/doc/html/rfc2104.html), build up from the [server.secret_key](https://docs.searxng.org/admin/settings/settings_server.html#settings-server) setting.
## Favicons Config
**favicons.config.CONFIG_SCHEMA** = `1`
Version of the configuration schema. 

**favicons.config.TOML_CACHE_CFG** = `{}`
Cache config objects by TOML’s filename. 

_class_ searx.favicons.config.FaviconConfig(_cfg_schema: int_, _cache: ~searx.favicons.cache.FaviconCacheConfig = <factory>_, _proxy: ~searx.favicons.proxy.FaviconProxyConfig = <factory>_) 
    
The class aggregates configurations of the favicon tools 

cfg_schema _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Config’s schema version. The specification of the version of the schema is mandatory, currently only version [`CONFIG_SCHEMA`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.config.CONFIG_SCHEMA "searx.favicons.config.CONFIG_SCHEMA") is supported. By specifying a version, it is possible to ensure downward compatibility in the event of future changes to the configuration schema 

cache _:[ FaviconCacheConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig")_ 
    
Setup of the [`cache.FaviconCacheConfig`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig"). 

proxy _:[ FaviconProxyConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.FaviconProxyConfig "searx.favicons.proxy.FaviconProxyConfig")_ 
    
Setup of the [`proxy.FaviconProxyConfig`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.FaviconProxyConfig "searx.favicons.proxy.FaviconProxyConfig"). 

_classmethod_ from_toml_file(_cfg_file :[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)")_, _use_cache :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_) → [FaviconConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.config.FaviconConfig "searx.favicons.config.FaviconConfig") 
    
Create a config object from a TOML file, the `use_cache` argument specifies whether a cache should be used.
## Favicons Proxy
Implementations for a favicon proxy 

_class_ searx.favicons.proxy.FaviconProxyConfig(_max_age: int = 604800_, _secret_key: str = ''_, _resolver_timeout: int = 3.0_, _resolver_map: dict[str_, _str] = <factory>_, _favicon_path: str = '/home/runner/work/searxng/searxng/searx/static/themes/{theme}/img/empty_favicon.svg'_, _favicon_mime_type: str = 'image/svg+xml'_) 
    
Configuration of the favicon proxy. 

max_age _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
HTTP header [Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control) `max-age` 

secret_key _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
By default, the value from [server.secret_key](https://docs.searxng.org/admin/settings/settings_server.html#settings-server) setting is used. 

resolver_timeout _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Timeout which the resolvers should not exceed, is usually passed to the outgoing request of the resolver. By default, the value from [outgoing.request_timeout](https://docs.searxng.org/admin/settings/settings_outgoing.html#settings-outgoing) setting is used. 

resolver_map _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
The resolver_map is a key / value dictionary where the key is the name of the resolver and the value is the fully qualifying name (fqn) of resolver’s function (the callable). The resolvers from the python module `searx.favicons.resolver` are available by default. 

get_resolver(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns the callable object (function) of the resolver with the `name`. If no resolver is registered for the `name`, `None` is returned. 

favicon(_** replacements_) 
    
Returns pathname and mimetype of the default favicon. 

favicon_data_url(_** replacements_) 
    
Returns data image URL of the default favicon. 

**favicons.proxy.favicon_proxy()**
REST API of SearXNG’s favicon proxy service
```
/favicon_proxy?authority=<...>&h=<...>

```

`authority`:
    
Domain name [**RFC 3986**](https://datatracker.ietf.org/doc/html/rfc3986.html) / see [`favicon_url`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.favicon_url "searx.favicons.proxy.favicon_url") 

`h`:
    
HMAC [**RFC 2104**](https://datatracker.ietf.org/doc/html/rfc2104.html), build up from the [server.secret_key](https://docs.searxng.org/admin/settings/settings_server.html#settings-server) setting. 

searx.favicons.proxy.search_favicon(_resolver :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Sends the request to the favicon resolver and returns a tuple for the favicon. The tuple consists of `(data, mime)`, if the resolver has not determined a favicon, both values are `None`. 

`data`:
    
Binary data of the favicon. 

`mime`:
    
Mime type of the favicon. 

searx.favicons.proxy.favicon_url(_authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Function to generate the image URL used for favicons in SearXNG’s result lists. The `authority` argument (aka netloc / [**RFC 3986**](https://datatracker.ietf.org/doc/html/rfc3986.html)) is usually a (sub-) domain name. This function is used in the HTML (jinja) templates.
```
<div class="favicon">
   <img src="{{ favicon_url(result.parsed_url.netloc) }}">
</div>

```

The returned URL is a route to [`favicon_proxy`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.favicon_proxy "searx.favicons.proxy.favicon_proxy") REST API.
If the favicon is already in the cache, the returned URL is a [data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs) (something like `data:image/png;base64,...`). By generating a data url from the [`cache.FaviconCache`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCache "searx.favicons.cache.FaviconCache"), additional HTTP roundtripps via the [`favicon_proxy`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.favicon_proxy "searx.favicons.proxy.favicon_proxy") are saved. However, it must also be borne in mind that data urls are not cached in the client (web browser).
## Favicons Resolver
Implementations of the favicon _resolvers_ that are available in the favicon proxy by default. A _resolver_ is a function that obtains the favicon from an external source. The _resolver_ function receives two arguments (`domain, timeout`) and returns a tuple `(data, mime)`. 

searx.favicons.resolvers.allesedv(_domain :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _timeout :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Favicon Resolver from allesedv.com / <https://favicon.allesedv.com/> 

searx.favicons.resolvers.duckduckgo(_domain :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _timeout :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Favicon Resolver from duckduckgo.com / <https://blog.jim-nielsen.com/2021/displaying-favicons-for-any-domain/> 

searx.favicons.resolvers.google(_domain :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _timeout :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Favicon Resolver from google.com 

searx.favicons.resolvers.yandex(_domain :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _timeout :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Favicon Resolver from yandex.com
## Favicons Cache
Implementations for caching favicons. 

[`FaviconCacheConfig`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig"):
    
Configuration of the favicon cache 

[`FaviconCache`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCache "searx.favicons.cache.FaviconCache"):
    
Abstract base class for the implementation of a favicon cache. 

[`FaviconCacheSQLite`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheSQLite "searx.favicons.cache.FaviconCacheSQLite"):
    
Favicon cache that manages the favicon BLOBs in a SQLite DB. 

[`FaviconCacheNull`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheNull "searx.favicons.cache.FaviconCacheNull"):
    
Fallback solution if the configured cache cannot be used for system reasons.
* * * 

**favicons.cache.state()**
show state of the cache 

searx.favicons.cache.maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=True_, _debug :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
perform maintenance of the cache 

searx.favicons.cache.init(_cfg :[FaviconCacheConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig")_) 
    
Initialization of a global `CACHE` 

_final class_searx.favicons.cache.FaviconCacheConfig(_db_type :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['sqlite','mem']='sqlite'_, _db_url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='/tmp/faviconcache.db'_, _HOLD_TIME :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=2592000_, _LIMIT_TOTAL_BYTES :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=52428800_, _BLOB_MAX_BYTES :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=20480_, _MAINTENANCE_PERIOD :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=3600_, _MAINTENANCE_MODE :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['auto','off']='auto'_) 
    
Configuration of the favicon cache. 

db_type _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['sqlite','mem']_ 
    
Type of the database: 

`sqlite`:
    
[`cache.FaviconCacheSQLite`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheSQLite "searx.favicons.cache.FaviconCacheSQLite") 

`mem`:
    
[`cache.FaviconCacheMEM`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheMEM "searx.favicons.cache.FaviconCacheMEM") (not recommended) 

db_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of the SQLite DB, the path to the database file. 

HOLD_TIME _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Hold time (default in sec.), after which a BLOB is removed from the cache. 

LIMIT_TOTAL_BYTES _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Maximum of bytes (default) stored in the cache of all blobs. Note: The limit is only reached at each maintenance interval after which the oldest BLOBs are deleted; the limit is exceeded during the maintenance period. If the maintenance period is _too long_ or maintenance is switched off completely, the cache grows uncontrollably. 

BLOB_MAX_BYTES _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
The maximum BLOB size in bytes that a favicon may have so that it can be saved in the cache. If the favicon is larger, it is not saved in the cache and must be requested by the client via the proxy. 

MAINTENANCE_PERIOD _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Maintenance period in seconds / when [`MAINTENANCE_MODE`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_MODE "searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_MODE") is set to `auto`. 

MAINTENANCE_MODE _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['auto','off']_ 
    
Type of maintenance mode 

`auto`:
    
Maintenance is carried out automatically as part of the maintenance intervals ([`MAINTENANCE_PERIOD`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_PERIOD "searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_PERIOD")); no external process is required. 

`off`:
    
Maintenance is switched off and must be carried out by an external process if required. 

_class_ searx.favicons.cache.FaviconCacheStats(_favicons: int | None = None, bytes: int | None = None, domains: int | None = None, resolvers: int | None = None, field_descr: tuple[tuple[str, str, ~typing.Callable[[int, int], str] | type], ...] = (('favicons', 'number of favicons in cache', <function humanize_number>), ('bytes', 'total size (approx. bytes) of cache', <function humanize_bytes>), ('domains', 'total number of domains in cache', <function humanize_number>), ('resolvers', 'number of resolvers', <class 'str'>))_) 
    
Dataclass which provides information on the status of the cache. 

_class_ searx.favicons.cache.FaviconCache(_cfg :[FaviconCacheConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig")_) 
    
Abstract base class for the implementation of a favicon cache. 

_abstractmethod_ set(_resolver :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _mime :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _data :[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Set data and mime-type in the cache. If data is None, the `FALLBACK_ICON` is registered. in the cache. 

_abstractmethod_ state() → [FaviconCacheStats](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheStats "searx.favicons.cache.FaviconCacheStats") 
    
Returns a [`FaviconCacheStats`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheStats "searx.favicons.cache.FaviconCacheStats") (key/values) with information on the state of the cache. 

_abstractmethod_ maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Performs maintenance on the cache 

_final class_searx.favicons.cache.FaviconCacheNull(_cfg :[FaviconCacheConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig")_) 
    
A dummy favicon cache that caches nothing / a fallback solution. The NullCache is used when more efficient caches such as the [`FaviconCacheSQLite`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheSQLite "searx.favicons.cache.FaviconCacheSQLite") cannot be used because, for example, the SQLite library is only available in an old version and does not meet the requirements. 

set(_resolver :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _mime :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _data :[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Set data and mime-type in the cache. If data is None, the `FALLBACK_ICON` is registered. in the cache. 

state() 
    
Returns a [`FaviconCacheStats`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheStats "searx.favicons.cache.FaviconCacheStats") (key/values) with information on the state of the cache. 

maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Performs maintenance on the cache 

_final class_searx.favicons.cache.FaviconCacheSQLite(_cfg :[FaviconCacheConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig")_) 
    
Favicon cache that manages the favicon BLOBs in a SQLite DB. The DB model in the SQLite DB is implemented using the abstract class `sqlitedb.SQLiteAppl`.
For introspection of the DB, jump into developer environment and run command to show cache state:
```
$ ./manage pyenv.cmd bash --norc --noprofile
(py3) python -m searx.favicons cache state

```

The following configurations are required / supported:
  * `MAINTENANCE_PERIOD`
  * `MAINTENANCE_MODE`

DB_SCHEMA _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ _= 1_ 
    
As soon as changes are made to the DB schema, the version number must be increased. Changes to the version number require the DB to be recreated (or migrated / if an migration path exists and is implemented). 

DDL_BLOBS _= 'CREATE TABLE IF NOT EXISTS blobs (\n sha256 TEXT,\n bytes_c INTEGER,\n mime TEXT NOT NULL,\n data BLOB NOT NULL,\n PRIMARY KEY (sha256))'_ 
    
Table to store BLOB objects by their sha256 hash values. 

DDL_BLOB_MAP _= "CREATE TABLE IF NOT EXISTS blob_map (\n m_time INTEGER DEFAULT (strftime('%s', 'now')), -- last modified (unix epoch) time in sec.\n sha256 TEXT,\n resolver TEXT,\n authority TEXT,\n PRIMARY KEY (resolver, authority))"_ 
    
Table to map from (resolver, authority) to sha256 hash values. 

SQL_DROP_LEFTOVER_BLOBS _= 'DELETE FROM blobs WHERE sha256 IN ( SELECT b.sha256 FROM blobs b LEFT JOIN blob_map bm ON b.sha256 = bm.sha256 WHERE bm.sha256 IS NULL)'_ 
    
Delete blobs.sha256 (BLOBs) no longer in blob_map.sha256. 

set(_resolver :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _mime :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _data :[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Set data and mime-type in the cache. If data is None, the `FALLBACK_ICON` is registered. in the cache. 

_property_ next_maintenance_time _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Returns (unix epoch) time of the next maintenance. 

maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Performs maintenance on the cache 

state() → [FaviconCacheStats](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheStats "searx.favicons.cache.FaviconCacheStats") 
    
Returns a [`FaviconCacheStats`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheStats "searx.favicons.cache.FaviconCacheStats") (key/values) with information on the state of the cache. 

_final class_searx.favicons.cache.FaviconCacheMEM(_cfg :[FaviconCacheConfig](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig "searx.favicons.cache.FaviconCacheConfig")_) 
    
Favicon cache in process’ memory. Its just a POC that stores the favicons in the memory of the process.
Attention
Don’t use it in production, it will blow up your memory!! 

set(_resolver :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _authority :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _mime :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _data :[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Set data and mime-type in the cache. If data is None, the `FALLBACK_ICON` is registered. in the cache. 

state() 
    
Returns a [`FaviconCacheStats`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheStats "searx.favicons.cache.FaviconCacheStats") (key/values) with information on the state of the cache. 

maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Performs maintenance on the cache
