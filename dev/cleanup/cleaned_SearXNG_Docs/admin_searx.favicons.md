<!-- source: https://docs.searxng.org/admin/searx.favicons.html -->

# Favicons
warning
Don’t activate the favicons before reading the documentation.
Activating the favicons in SearXNG is very easy, but this **generates a significantly higher load** in the client/server communication and increases resources needed on the server.
To mitigate these disadvantages, various methods have been implemented, including a _cache_. The cache must be parameterized according to your own requirements and maintained regularly.
To activate favicons in SearXNG’s result list, set a default `favicon_resolver` in the [search](https://docs.searxng.org/admin/settings/settings_search.html#settings-search) settings:
```
search:
  favicon_resolver: "duckduckgo"

```

By default and without any extensions, SearXNG serves these resolvers:
  * `duckduckgo`
  * `allesedv`
  * `google`
  * `yandex`

With the above setting favicons are displayed, the user has the option to deactivate this feature in his settings. If the user is to have the option of selecting from several _resolvers_ , a further setting is required / but this setting will be discussed [later](https://docs.searxng.org/admin/searx.favicons.html#register-resolvers) in this article, first we have to setup the favicons cache.
## Infrastructure
The infrastructure for providing the favicons essentially consists of three parts:
  * [`Favicons-Proxy`](https://docs.searxng.org/src/searx.favicons.html#module-searx.favicons.proxy "searx.favicons.proxy") (aka _proxy_)
  * [`Favicons-Resolvers`](https://docs.searxng.org/src/searx.favicons.html#module-searx.favicons.resolvers "searx.favicons.resolvers") (aka _resolver_)
  * [`Favicons-Cache`](https://docs.searxng.org/src/searx.favicons.html#module-searx.favicons.cache "searx.favicons.cache") (aka _cache_)

To protect the privacy of users, the favicons are provided via a _proxy_. This _proxy_ is automatically activated with the above activation of a _resolver_. Additional requests are required to provide the favicons: firstly, the _proxy_ must process the incoming requests and secondly, the _resolver_ must make outgoing requests to obtain the favicons from external sources.
A _cache_ has been developed to massively reduce both, incoming and outgoing requests. This _cache_ is also activated automatically with the above activation of a _resolver_. In its defaults, however, the _cache_ is minimal and not well suitable for a production environment!
## Setting up the cache
To parameterize the _cache_ and more settings of the favicons infrastructure, a [TOML](https://toml.io/en/) configuration is created in the file `/etc/searxng/favicons.toml`.
```
[favicons]

cfg_schema = 1   # config's schema version no.

[favicons.cache]

db_url = "/var/cache/searxng/faviconcache.db"  # default: "/tmp/faviconcache.db"
LIMIT_TOTAL_BYTES = 2147483648                 # 2 GB / default: 50 MB
# HOLD_TIME = 5184000                            # 60 days / default: 30 days
# BLOB_MAX_BYTES = 40960                         # 40 KB / default 20 KB
# MAINTENANCE_MODE = "off"                       # default: "auto"
# MAINTENANCE_PERIOD = 600                       # 10min / default: 1h

```

[`cfg_schema`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.config.FaviconConfig.cfg_schema "searx.favicons.config.FaviconConfig.cfg_schema"):
    
Is required to trigger any processes required for future upgrades / don’t change it. 

[`cache.db_url`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig.db_url "searx.favicons.cache.FaviconCacheConfig.db_url"):
    
The path to the ([SQLite](https://www.sqlite.org/)) database file. The default path is in the [/tmp](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s18.html) folder, which is deleted on every reboot and is therefore unsuitable for a production environment. The [FHS](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html) provides the folder [/var/cache](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch05s05.html) for the cache of applications, so a suitable storage location of SearXNG’s caches is folder `/var/cache/searxng`.
In a standard installation (compare [Create user](https://docs.searxng.org/admin/installation-searxng.html#create-searxng-user)), the folder must be created and the user under which the SearXNG process is running must be given write permission to this folder.
```
$ sudo mkdir /var/cache/searxng
$ sudo chown root:searxng /var/cache/searxng/
$ sudo chmod g+w /var/cache/searxng/

```

In container systems, a volume should be mounted for this folder. Check whether the process in the container has read/write access to the mounted folder. 

[`cache.LIMIT_TOTAL_BYTES`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig.LIMIT_TOTAL_BYTES "searx.favicons.cache.FaviconCacheConfig.LIMIT_TOTAL_BYTES"):
    
Maximum of bytes stored in the cache of all blobs. The limit is only reached at each maintenance interval after which the oldest BLOBs are deleted; the limit is exceeded during the maintenance period.
Attention
If the maintenance period is too long or maintenance is switched off completely, the cache grows uncontrollably.
SearXNG hosters can change other parameters of the cache as required:
### Maintenance of the cache
Regular maintenance of the cache is required! By default, regular maintenance is triggered automatically as part of the client requests:
  * [`cache.MAINTENANCE_MODE`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_MODE "searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_MODE") (default `auto`)
  * [`cache.MAINTENANCE_PERIOD`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_PERIOD "searx.favicons.cache.FaviconCacheConfig.MAINTENANCE_PERIOD") (default `6000` / 1h)

As an alternative to maintenance as part of the client request process, it is also possible to carry out maintenance using an external process. For example, by creating a [crontab](https://manpages.debian.org/jump?q=crontab) entry for maintenance:
```
$ python -m searx.favicons cache maintenance

```

The following command can be used to display the state of the cache:
```
$ python -m searx.favicons cache state

```

## Proxy configuration
Most of the options of the [`Favicons-Proxy`](https://docs.searxng.org/src/searx.favicons.html#module-searx.favicons.proxy "searx.favicons.proxy") are already set sensibly with settings from the [settings.yml](https://docs.searxng.org/admin/settings/index.html#searxng-settings-yml) and should not normally be adjusted.
```
[favicons.proxy]

max_age = 5184000             # 60 days / default: 7 days (604800 sec)

```

[`max_age`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.FaviconProxyConfig.max_age "searx.favicons.proxy.FaviconProxyConfig.max_age"):
    
The [HTTP Cache-Control max-age](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#response_directives) response directive indicates that the response remains fresh until N seconds after the response is generated. This setting therefore determines how long a favicon remains in the client’s cache. As a rule, in the favicons infrastructure of SearXNG’s this setting only affects favicons whose byte size exceeds [BLOB_MAX_BYTES](https://docs.searxng.org/admin/searx.favicons.html#favicon-cache-setup) (the other favicons that are already in the cache are embedded as [data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs) in the [`generated HTML`](https://docs.searxng.org/src/searx.favicons.html#searx.favicons.proxy.favicon_url "searx.favicons.proxy.favicon_url"), which can greatly reduce the number of additional requests).
### Register resolvers
A `resolver` is a function that obtains the favicon from an external source. The resolver functions available to the user are registered with their fully qualified name ([FQN](https://en.wikipedia.org/wiki/Fully_qualified_name)) in a `resolver_map`.
If no `resolver_map` is defined in the `favicon.toml`, the favicon infrastructure of SearXNG generates this `resolver_map` automatically depending on the `settings.yml`. SearXNG would automatically generate the following TOML configuration from the following YAML configuration:
```
search:
  favicon_resolver: "duckduckgo"

```

```
[favicons.proxy.resolver_map]

"duckduckgo" = "searx.favicons.resolvers.duckduckgo"

```

If this automatism is not desired, then (and only then) a separate `resolver_map` must be created. For example, to give the user two resolvers to choose from, the following configuration could be used:
```
[favicons.proxy.resolver_map]

"duckduckgo" = "searx.favicons.resolvers.duckduckgo"
"allesedv" = "searx.favicons.resolvers.allesedv"
# "google" = "searx.favicons.resolvers.google"
# "yandex" = "searx.favicons.resolvers.yandex"

```

Note
With each resolver, the resource requirement increases significantly.
The number of resolvers increases:
  * the number of incoming/outgoing requests and
  * the number of favicons to be stored in the cache.

In the following we list the resolvers available in the core of SearXNG, but via the [FQN](https://en.wikipedia.org/wiki/Fully_qualified_name) it is also possible to implement your own resolvers and integrate them into the _proxy_ :
