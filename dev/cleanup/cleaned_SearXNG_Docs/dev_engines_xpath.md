<!-- source: https://docs.searxng.org/dev/engines/xpath.html -->

# XPath Engine
The XPath engine is a _generic_ engine with which it is possible to configure engines in the settings.
## Configuration
Request:
Paging:
Time Range:
Safe-Search:
Response:
  * [`no_result_for_http_status`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.no_result_for_http_status "searx.engines.xpath.no_result_for_http_status")

[XPath selector](https://quickref.me/xpath.html#xpath-selectors):
## Example
Here is a simple example of a XPath engine configured in the [engines:](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines) section, further read [Engine Overview](https://docs.searxng.org/dev/engines/engine_overview.html#engines-dev).
```
- name : bitbucket
  engine : xpath
  paging : True
  search_url : https://bitbucket.org/repo/all/{pageno}?name={query}
  url_xpath : //article[@class="repo-summary"]//a[@class="repo-link"]/@href
  title_xpath : //article[@class="repo-summary"]//a[@class="repo-link"]
  content_xpath : //article[@class="repo-summary"]/p

```

## Implementations
**engines.xpath.search_url** = `None`
Search URL of the engine. Example:
```
https://example.org/?search={query}&page={pageno}{time_range}{safe_search}

```

Replacements are: 

`{query}`:
    
Search terms from user. 

`{pageno}`:
    
Page number if engine supports paging [`paging`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.paging "searx.engines.xpath.paging") 

`{lang}`:
    
ISO 639-1 language code (en, de, fr ..) 

`{time_range}`:
    
[`URL parameter`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.time_range_url "searx.engines.xpath.time_range_url") if engine [`supports time range`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.time_range_support "searx.engines.xpath.time_range_support"). The value for the parameter is taken from [`time_range_map`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.time_range_map "searx.engines.xpath.time_range_map"). 

`{safe_search}`:
    
Safe-search [`URL parameter`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.safe_search_map "searx.engines.xpath.safe_search_map") if engine [`supports safe-search`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.safe_search_support "searx.engines.xpath.safe_search_support"). The `{safe_search}` replacement is taken from the `safes_search_map`. Filter results:
```
0: none, 1: moderate, 2:strict

```

If not supported, the URL parameter is an empty string. 

**engines.xpath.lang_all** = `'en'`
Replacement `{lang}` in [`search_url`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.search_url "searx.engines.xpath.search_url") if language `all` is selected. 

**engines.xpath.no_result_for_http_status** = `[]`
Return empty result for these HTTP status codes instead of throwing an error.
```
no_result_for_http_status: []

```

**engines.xpath.soft_max_redirects** = `0`
Maximum redirects, soft limit. Record an error but don’t stop the engine 

**engines.xpath.results_xpath** = `''`
[XPath selector](https://quickref.me/xpath.html#xpath-selectors) for the list of result items 

**engines.xpath.url_xpath** = `None`
[XPath selector](https://quickref.me/xpath.html#xpath-selectors) of result’s `url`. 

**engines.xpath.content_xpath** = `None`
[XPath selector](https://quickref.me/xpath.html#xpath-selectors) of result’s `content`. 

**engines.xpath.title_xpath** = `None`
[XPath selector](https://quickref.me/xpath.html#xpath-selectors) of result’s `title`. 

**engines.xpath.thumbnail_xpath** = `False`
[XPath selector](https://quickref.me/xpath.html#xpath-selectors) of result’s `thumbnail`. 

**engines.xpath.suggestion_xpath** = `''`
[XPath selector](https://quickref.me/xpath.html#xpath-selectors) of result’s `suggestion`. 

**engines.xpath.cookies** = `{}`
Some engines might offer different result based on cookies. Possible use-case: To set safesearch cookie. 

**engines.xpath.headers** = `{}`
Some engines might offer different result based headers. Possible use-case: To set header to moderate. 

**engines.xpath.method** = `'GET'`
Some engines might require to do POST requests for search. 

**engines.xpath.request_body** = `''`
The body of the request. This can only be used if different [`method`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.method "searx.engines.xpath.method") is set, e.g. `POST`. For formatting see the documentation of [`search_url`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.search_url "searx.engines.xpath.search_url"):
```
search={query}&page={pageno}{time_range}{safe_search}

```

**engines.xpath.paging** = `False`
Engine supports paging [True or False]. 

**engines.xpath.page_size** = `1`
Number of results on each page. Only needed if the site requires not a page number, but an offset. 

**engines.xpath.first_page_num** = `1`
Number of the first page (usually 0 or 1). 

**engines.xpath.time_range_support** = `False`
Engine supports search time range. 

**engines.xpath.time_range_url** = `'&hours={time_range_val}'`
Time range URL parameter in the in [`search_url`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.search_url "searx.engines.xpath.search_url"). If no time range is requested by the user, the URL parameter is an empty string. The `{time_range_val}` replacement is taken from the [`time_range_map`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.time_range_map "searx.engines.xpath.time_range_map").
```
time_range_url : '&days={time_range_val}'

```

**engines.xpath.time_range_map** = `{'day': 24, 'month': 720, 'week': 168, 'year': 8760}`
Maps time range value from user to `{time_range_val}` in [`time_range_url`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.time_range_url "searx.engines.xpath.time_range_url").
```
time_range_map:
  day: 1
  week: 7
  month: 30
  year: 365

```

**engines.xpath.safe_search_support** = `False`
Engine supports safe-search. 

**engines.xpath.safe_search_map** = `{0: '&filter=none', 1: '&filter=moderate', 2: '&filter=strict'}`
Maps safe-search value to `{safe_search}` in [`search_url`](https://docs.searxng.org/dev/engines/xpath.html#searx.engines.xpath.search_url "searx.engines.xpath.search_url").
```
safesearch: true
safes_search_map:
  0: '&filter=none'
  1: '&filter=moderate'
  2: '&filter=strict'

```

**engines.xpath.request(_query_ , _params_)**
Build request parameters (see [Making a Request](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request)). 

searx.engines.xpath.response(_resp_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Scrap _results_ from the response (see [Result Types](https://docs.searxng.org/dev/result_types/index.html#result-types)).
