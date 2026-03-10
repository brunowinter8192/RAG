<!-- source: https://docs.searxng.org/dev/engines/engine_overview.html -->

# Engine Overview
Further reading ..
SearXNG is a [metasearch-engine](https://en.wikipedia.org/wiki/Metasearch_engine), so it uses different search engines to provide better results.
Because there is no general search API which could be used for every search engine, an adapter has to be built between SearXNG and the external search engines. Adapters are stored under the folder [git://searx/engines](https://github.com/searxng/searxng/blob/master/searx/engines).
## General Engine Configuration
It is required to tell SearXNG the type of results the engine provides. The arguments can be set in the engine file or in the settings file (normally `settings.yml`). The arguments in the settings file override the ones in the engine file.
It does not matter if an option is stored in the engine file or in the settings. However, the standard way is the following:
### Engine File
Table 2 Common options in the engine module argument | type | information  
---|---|---  
categories | list | categories, in which the engine is working  
paging | boolean | support multiple pages  
time_range_support | boolean | support search time range  
engine_type | str | 
  * `online` [[ref]](https://docs.searxng.org/dev/engines/index.html#online-engines) by default, other possibles values are:
  * `offline` [[ref]](https://docs.searxng.org/dev/engines/index.html#offline-engines)
  * `online_dictionary` [[ref]](https://docs.searxng.org/dev/engines/index.html#online-dictionary)
  * `online_currency` [[ref]](https://docs.searxng.org/dev/engines/index.html#online-currency)
  * `online_url_search` [[ref]](https://docs.searxng.org/dev/engines/index.html#online-url-search)

  
### Engine `settings.yml`
For a more detailed description, see [engines:](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines) in the [settings.yml](https://docs.searxng.org/admin/settings/settings.html#settings-yml).
Table 3 Common options in the engine setup (`settings.yml`) argument | type | information  
---|---|---  
name | string | name of search-engine  
engine | string | name of searxng-engine (file name without `.py`)  
enable_http | bool | enable HTTP (by default only HTTPS is enabled).  
shortcut | string | shortcut of search-engine  
timeout | string | specific timeout for search-engine  
display_error_messages | boolean | display error messages on the web UI  
proxies | dict | set proxies for a specific engine (e.g. `proxies : {http: socks5://proxy:port, https: socks5://proxy:port}`)  
### Overrides
A few of the options have default values in the namespace of the engine’s python module, but are often overwritten by the settings. If `None` is assigned to an option in the engine file, it has to be redefined in the settings, otherwise SearXNG will not start with that engine (global names with a leading underline can be `None`).
Here is an very simple example of the global names in the namespace of engine’s module:
```
# engine dependent config
categories = ['general']
paging = True
_non_overwritten_global = 'foo'

```

Table 4 The naming of overrides is arbitrary / recommended overrides are: argument | type | information  
---|---|---  
base_url | string | base-url, can be overwritten to use same engine on other URL  
number_of_results | int | maximum number of results per request  
language | string | ISO code of language and country like en_US  
api_key | string | api-key if required by engine  
## Making a Request
To perform a search an URL have to be specified. In addition to specifying an URL, arguments can be passed to the query.
### Passed Arguments (request)
These arguments can be used to construct the search query. Furthermore, parameters with default value can be redefined for special purposes.
Table 5 If the `engine_type` is [`online`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineProcessor.get_params "searx.search.processors.online.OnlineProcessor.get_params") argument | type | default-value, information  
---|---|---  
url | str | `''`  
method | str | `'GET'`  
headers | dict | `{}`  
data | dict | `{}`  
cookies | dict | `{}`  
verify | bool | `True`  
headers.User-Agent | str | a random User-Agent  
category | str | current category, like `'general'`  
safesearch | int | `0`, between `0` and `2` (normal, moderate, strict)  
time_range | Optional[str] | `None`, can be `day`, `week`, `month`, `year`  
pageno | int | current pagenumber  
searxng_locale | str | SearXNG’s locale selected by user. Specific language code like `'en'`, `'en-US'`, or `'all'` if unspecified.  
Table 6 If the `engine_type` is [`online_dictionary`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_dictionary.OnlineDictionaryProcessor.get_params "searx.search.processors.online_dictionary.OnlineDictionaryProcessor.get_params"), in addition to the [online](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online) arguments: argument | type | default-value, information  
---|---|---  
from_lang | str | specific language code like `'en_US'`  
to_lang | str | specific language code like `'en_US'`  
query | str | the text query without the languages  
Table 7 If the `engine_type` is [`online_currency`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_currency.OnlineCurrencyProcessor.get_params "searx.search.processors.online_currency.OnlineCurrencyProcessor.get_params"), in addition to the [online](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online) arguments: argument | type | default-value, information  
---|---|---  
amount | float | the amount to convert  
from | str | ISO 4217 code  
to | str | ISO 4217 code  
from_name | str | currency name  
to_name | str | currency name  
Table 8 If the `engine_type` is [`online_url_search`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_url_search.OnlineUrlSearchProcessor.get_params "searx.search.processors.online_url_search.OnlineUrlSearchProcessor.get_params"), in addition to the [online](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online) arguments: argument | type | default-value, information  
---|---|---  
search_url | dict |  URLs from the search query: ```
{
  'http': str,
  'ftp': str,
  'data:image': str
}

```
  
### Specify Request
The function [`def request(query, params):`](https://docs.searxng.org/dev/engines/demo/demo_online.html#searx.engines.demo_online.request "searx.engines.demo_online.request") always returns the `params` variable, the following parameters can be used to specify a search request:
argument | type | information  
---|---|---  
url | str | requested url  
method | str | HTTP request method  
headers | dict | HTTP header information  
data | dict | HTTP data information  
cookies | dict | HTTP cookies  
verify | bool | Performing SSL-Validity check  
allow_redirects | bool | Follow redirects  
max_redirects | int | maximum redirects, hard limit  
soft_max_redirects | int | maximum redirects, soft limit. Record an error but don’t stop the engine  
raise_for_httperror | bool | True by default: raise an exception if the HTTP code of response is >= 300  
## Making a Response
In the `response` function of the engine, the HTTP response (`resp`) is parsed and a list of results is returned.
A engine can append result-items of different media-types and different result-types to the result list. The list of the result items is render to HTML by templates. For more details read section:
