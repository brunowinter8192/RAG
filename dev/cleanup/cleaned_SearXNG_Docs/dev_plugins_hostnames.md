<!-- source: https://docs.searxng.org/dev/plugins/hostnames.html -->

# Hostnames
During the initialization phase, the plugin checks whether a `hostnames:` configuration exists. If this is not the case, the plugin is not included in the PluginStorage (it is not available for selection).
  * `hostnames.replace`: A **mapping** of regular expressions to hostnames to be replaced by other hostnames.
```
hostnames:
  replace:
    '(.*\.)?youtube\.com$': 'invidious.example.com'
    '(.*\.)?youtu\.be$': 'invidious.example.com'
    ...

```

  * `hostnames.remove`: A **list** of regular expressions of the hostnames whose results should be taken from the results list.
```
hostnames:
  remove:
    - '(.*\.)?facebook.com$'
    - ...

```

  * `hostnames.high_priority`: A **list** of regular expressions for hostnames whose result should be given higher priority. The results from these hosts are arranged higher in the results list.
```
hostnames:
  high_priority:
    - '(.*\.)?wikipedia.org$'
    - ...

```

  * `hostnames.lower_priority`: A **list** of regular expressions for hostnames whose result should be given lower priority. The results from these hosts are arranged lower in the results list.
```
hostnames:
  low_priority:
    - '(.*\.)?google(\..*)?$'
    - ...

```

If the URL matches the pattern of `high_priority` AND `low_priority`, the higher priority wins over the lower priority.
Alternatively, you can also specify a file name for the **mappings** or **lists** to load these from an external file:
```
hostnames:
  replace: 'rewrite-hosts.yml'
  remove:
    - '(.*\.)?facebook.com$'
    - ...
  low_priority:
    - '(.*\.)?google(\..*)?$'
    - ...
  high_priority:
    - '(.*\.)?wikipedia.org$'
    - ...

```

The `rewrite-hosts.yml` from the example above must be in the folder in which the `settings.yml` file is already located (`/etc/searxng`). The file then only contains the lists or the mapping tables without further information on the namespaces. In the example above, this would be a mapping table that looks something like this:
```
'(.*\.)?youtube\.com$': 'invidious.example.com'
'(.*\.)?youtu\.be$': 'invidious.example.com'

```

_class_ searx.plugins.hostnames.SXNGPlugin(_plg_cfg :[PluginCfg](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins.PluginCfg")_) 
    
Rewrite hostnames, remove results or prioritize them. 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'hostnames'_ 
    
The ID (suffix) in the HTML form. 

on_result(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_, _result :[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Runs for each result of each engine and returns a boolean:
  * `True` to keep the result
  * `False` to remove the result from the result list

The `result` can be modified to the needs.
Hint
If [`Result.url`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.url "searx.result_types._base.Result.url") is modified, [`Result.parsed_url`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.parsed_url "searx.result_types._base.Result.parsed_url") must be changed accordingly:
```
result["parsed_url"] = urlparse(result["url"])

```

init(_app :[flask.Flask](https://flask.palletsprojects.com/en/stable/api/#flask.Flask "\(in Flask v3.1.x\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the plugin, the return value decides whether this plugin is active or not. Initialization only takes place once, at the time the WEB application is set up. The base method always returns `True`, the method can be overwritten in the inheritances,
  * `True` plugin is active
  * `False` plugin is inactive

searx.plugins.hostnames.filter_url_field(_result :[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")|[LegacyResult](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.LegacyResult "searx.result_types._base.LegacyResult")_, _field_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _url_src :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Returns bool `True` to use URL unchanged (`False` to ignore URL). If URL should be modified, the returned string is the new URL to use.
