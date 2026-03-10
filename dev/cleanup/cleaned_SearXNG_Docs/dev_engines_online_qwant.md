<!-- source: https://docs.searxng.org/dev/engines/online/qwant.html -->

# Qwant
Contents
This engine uses the Qwant API (<https://api.qwant.com/v3>) to implement Qwant -Web, -News, -Images and -Videos. The API is undocumented but can be reverse engineered by reading the network log of <https://www.qwant.com/> queries.
For Qwant’s _web-search_ two alternatives are implemented:
  * `web`: uses the [`api_url`](https://docs.searxng.org/dev/engines/online/qwant.html#searx.engines.qwant.api_url "searx.engines.qwant.api_url") which returns a JSON structure
  * `web-lite`: uses the [`web_lite_url`](https://docs.searxng.org/dev/engines/online/qwant.html#searx.engines.qwant.web_lite_url "searx.engines.qwant.web_lite_url") which returns a HTML page

## Configuration
The engine has the following additional settings:
  * [`qwant_categ`](https://docs.searxng.org/dev/engines/online/qwant.html#searx.engines.qwant.qwant_categ "searx.engines.qwant.qwant_categ")

This implementation is used by different qwant engines in the [settings.yml](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines):
```
- name: qwant
  qwant_categ: web-lite  # alternatively use 'web'
  ...
- name: qwant news
  qwant_categ: news
  ...
- name: qwant images
  qwant_categ: images
  ...
- name: qwant videos
  qwant_categ: videos
  ...

```

## Implementations
**engines.qwant.max_page** = `5`
5 pages maximum (`&p=5`): Trying to do more just results in an improper redirect 

**engines.qwant.qwant_categ** = `None`
One of `web-lite` (or `web`), `news`, `images` or `videos` 

**engines.qwant.api_url** = `'https://api.qwant.com/v3/search/'`
URL of Qwant’s API (JSON) 

**engines.qwant.web_lite_url** = `'https://lite.qwant.com/'`
URL of Qwant-Lite (HTML) 

**engines.qwant.request(_query_ , _params_)**
Qwant search request 

**engines.qwant.parse_web_lite(_resp_)**
Parse results from Qwant-Lite 

**engines.qwant.parse_web_api(_resp_)**
Parse results from Qwant’s API
