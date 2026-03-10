<!-- source: https://docs.searxng.org/dev/engines/json_engine.html -->

# JSON Engine
The JSON engine is a _generic_ engine with which it is possible to configure engines in the settings.
## Configuration
Request:
Paging:
Time Range:
Safe-Search:
Response:
JSON query:
## Example
Here is a simple example of a JSON engine configure in the [engines:](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines) section, further read [Engine Overview](https://docs.searxng.org/dev/engines/engine_overview.html#engines-dev).
```
- name : mdn
  engine : json_engine
  paging : True
  search_url : https://developer.mozilla.org/api/v1/search?q={query}&page={pageno}
  results_query : documents
  url_query : mdn_url
  url_prefix : https://developer.mozilla.org
  title_query : title
  content_query : summary

```

## Implementations
**engines.json_engine.search_url** = `None`
Search URL of the engine. Example:
```
https://example.org/?search={query}&page={pageno}{time_range}{safe_search}

```

Replacements are: 

`{query}`:
    
Search terms from user. 

`{pageno}`:
    
Page number if engine supports paging [`paging`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.paging "searx.engines.json_engine.paging") 

`{lang}`:
    
ISO 639-1 language code (en, de, fr ..) 

`{time_range}`:
    
[`URL parameter`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.time_range_url "searx.engines.json_engine.time_range_url") if engine [`supports time range`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.time_range_support "searx.engines.json_engine.time_range_support"). The value for the parameter is taken from [`time_range_map`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.time_range_map "searx.engines.json_engine.time_range_map"). 

`{safe_search}`:
    
Safe-search [`URL parameter`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.safe_search_map "searx.engines.json_engine.safe_search_map") if engine [`supports safe-search`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.safe_search_support "searx.engines.json_engine.safe_search_support"). The `{safe_search}` replacement is taken from the `safes_search_map`. Filter results:
```
0: none, 1: moderate, 2:strict

```

If not supported, the URL parameter is an empty string. 

**engines.json_engine.lang_all** = `'en'`
Replacement `{lang}` in [`search_url`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.search_url "searx.engines.json_engine.search_url") if language `all` is selected. 

**engines.json_engine.no_result_for_http_status** = `[]`
Return empty result for these HTTP status codes instead of throwing an error.
```
no_result_for_http_status: []

```

**engines.json_engine.soft_max_redirects** = `0`
Maximum redirects, soft limit. Record an error but don’t stop the engine 

**engines.json_engine.method** = `'GET'`
Some engines might require to do POST requests for search. 

**engines.json_engine.request_body** = `''`
The body of the request. This can only be used if different [`method`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.method "searx.engines.json_engine.method") is set, e.g. `POST`. For formatting see the documentation of [`search_url`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.search_url "searx.engines.json_engine.search_url").
Note: Curly brackets which aren’t encapsulating a replacement placeholder must be escaped by doubling each `{` and `}`.
```
request_body: >-
  {{
    "search": "{query}",
    "page": {pageno},
    "extra": {{
      "time_range": {time_range},
      "rating": "{safe_search}"
    }}
  }}

```

**engines.json_engine.cookies** = `{}`
Some engines might offer different result based on cookies. Possible use-case: To set safesearch cookie. 

**engines.json_engine.headers** = `{}`
Some engines might offer different result based on cookies or headers. Possible use-case: To set safesearch cookie or header to moderate. 

**engines.json_engine.paging** = `False`
Engine supports paging [True or False]. 

**engines.json_engine.page_size** = `1`
Number of results on each page. Only needed if the site requires not a page number, but an offset. 

**engines.json_engine.first_page_num** = `1`
Number of the first page (usually 0 or 1). 

**engines.json_engine.results_query** = `''`
JSON query for the list of result items.
The query string is a slash / separated path of JSON key names. Array entries can be specified using the index or can be omitted entirely, in which case each entry is considered - most implementations will default to the first entry in this case. 

**engines.json_engine.url_query** = `None`
JSON query of result’s `url`. For the query string documentation see [`results_query`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.results_query "searx.engines.json_engine.results_query") 

**engines.json_engine.url_prefix** = `''`
String to prepend to the result’s `url`. 

**engines.json_engine.title_query** = `None`
JSON query of result’s `title`. For the query string documentation see [`results_query`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.results_query "searx.engines.json_engine.results_query") 

**engines.json_engine.content_query** = `None`
JSON query of result’s `content`. For the query string documentation see [`results_query`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.results_query "searx.engines.json_engine.results_query") 

**engines.json_engine.thumbnail_query** = `False`
JSON query of result’s `thumbnail`. For the query string documentation see [`results_query`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.results_query "searx.engines.json_engine.results_query") 

**engines.json_engine.thumbnail_prefix** = `''`
String to prepend to the result’s `thumbnail`. 

**engines.json_engine.suggestion_query** = `''`
JSON query of result’s `suggestion`. For the query string documentation see [`results_query`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.results_query "searx.engines.json_engine.results_query") 

**engines.json_engine.title_html_to_text** = `False`
Extract text from a HTML title string 

**engines.json_engine.content_html_to_text** = `False`
Extract text from a HTML content string 

**engines.json_engine.time_range_support** = `False`
Engine supports search time range. 

**engines.json_engine.time_range_url** = `'&hours={time_range_val}'`
Time range URL parameter in the in [`search_url`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.search_url "searx.engines.json_engine.search_url"). If no time range is requested by the user, the URL parameter is an empty string. The `{time_range_val}` replacement is taken from the [`time_range_map`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.time_range_map "searx.engines.json_engine.time_range_map").
```
time_range_url : '&days={time_range_val}'

```

**engines.json_engine.time_range_map** = `{'day': 24, 'month': 720, 'week': 168, 'year': 8760}`
Maps time range value from user to `{time_range_val}` in [`time_range_url`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.time_range_url "searx.engines.json_engine.time_range_url").
```
time_range_map:
  day: 1
  week: 7
  month: 30
  year: 365

```

**engines.json_engine.safe_search_support** = `False`
Engine supports safe-search. 

**engines.json_engine.safe_search_map** = `{0: '&filter=none', 1: '&filter=moderate', 2: '&filter=strict'}`
Maps safe-search value to `{safe_search}` in [`search_url`](https://docs.searxng.org/dev/engines/json_engine.html#searx.engines.json_engine.search_url "searx.engines.json_engine.search_url").
```
safesearch: true
safes_search_map:
  0: '&filter=none'
  1: '&filter=moderate'
  2: '&filter=strict'

```

**engines.json_engine.request(_query_ , _params_)**
Build request parameters (see [Making a Request](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request)). 

**engines.json_engine.response(_resp_)**
Scrap _results_ from the response (see [Result Types](https://docs.searxng.org/dev/result_types/index.html#result-types)).
