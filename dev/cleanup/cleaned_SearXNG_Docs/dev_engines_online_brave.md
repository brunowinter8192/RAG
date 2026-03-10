<!-- source: https://docs.searxng.org/dev/engines/online/brave.html -->

# Brave Engines
Contents
Brave offers two different engines for SearXNG:
  1. The standard engine (`brave`) uses the web interface.
  2. The API engine (`braveapi`) uses the official REST API.

## Brave Standard Engine
Brave supports the categories listed in [`brave_category`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.brave.brave_category "searx.engines.brave.brave_category") (General, news, videos, images). The support of [`paging`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.brave.paging "searx.engines.brave.paging") and [`time range`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.brave.time_range_support "searx.engines.brave.time_range_support") is limited (see remarks).
Configured `brave` engines:
```
- name: brave
  engine: brave
  ...
  brave_category: search
  time_range_support: true
  paging: true

- name: brave.images
  engine: brave
  ...
  brave_category: images

- name: brave.videos
  engine: brave
  ...
  brave_category: videos

- name: brave.news
  engine: brave
  ...
  brave_category: news

- name: brave.goggles
  time_range_support: true
  paging: true
  ...
  brave_category: goggles

```

### Brave regions
Brave uses two-digit tags for the regions like `ca` while SearXNG deals with locales. To get a mapping, all _officiat de-facto_ languages of the Brave region are mapped to regions in SearXNG (see [`babel`](https://babel.readthedocs.io/en/latest/api/languages.html#babel.languages.get_official_languages "\(in Babel v2.2\)")):
```
"regions": {
  ..
  "en-CA": "ca",
  "fr-CA": "ca",
  ..
 }

```

Note
The language (aka region) support of Brave’s index is limited to very basic languages. The search results for languages like Chinese or Arabic are of low quality.
### Brave Goggles
Goggles allow you to choose, alter, or extend the ranking of Brave Search results ([Goggles Whitepaper](https://brave.com/static-assets/files/goggles.pdf)). Goggles are openly developed by the community of Brave Search users.
Select from the [list of Goggles](https://search.brave.com/goggles/discover) people have published, or create your own ([Goggles Quickstart](https://github.com/brave/goggles-quickstart)).
### Brave languages
Brave’s language support is limited to the UI (menus, area local notations, etc). Brave’s index only seems to support a locale, but it does not seem to support any languages in its index. The choice of available languages is very small (and its not clear to me where the difference in UI is when switching from en-us to en-ca or en-gb).
In the [`EngineTraits object`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits") the UI languages are stored in a custom field named `ui_lang`:
```
"custom": {
  "ui_lang": {
    "ca": "ca",
    "de-DE": "de-de",
    "en-CA": "en-ca",
    "en-GB": "en-gb",
    "en-US": "en-us",
    "es": "es",
    "fr-CA": "fr-ca",
    "fr-FR": "fr-fr",
    "ja-JP": "ja-jp",
    "pt-BR": "pt-br",
    "sq-AL": "sq-al"
  }
},

```

### Implementations
**engines.brave.brave_category** = `'search'`
Brave supports common web-search, videos, images, news, and goggles search.
  * `search`: Common WEB search
  * `videos`: search for videos
  * `images`: search for images
  * `news`: search for news
  * `goggles`: Common WEB search with custom rules, requires a [`Goggles`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.brave.Goggles "searx.engines.brave.Goggles") URL.

**engines.brave.Goggles** = `''`
This should be a URL ending in `.goggle` 

**engines.brave.brave_spellcheck** = `False`
Brave supports some kind of spell checking. When activated, Brave tries to fix typos, e.g. it searches for `food` when the user queries for `fooh`. In the UI of Brave the user gets warned about this, since we can not warn the user in SearXNG, the spellchecking is disabled by default. 

**engines.brave.paging** = `False`
Brave only supports paging in [`brave_category`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.brave.brave_category "searx.engines.brave.brave_category") `search` (UI category All) and in the goggles category. 

**engines.brave.max_page** = `10`
Tested 9 pages maximum (`&offset=8`), to be save max is set to 10. Trying to do more won’t return any result and you will most likely be flagged as a bot. 

**engines.brave.time_range_support** = `False`
Brave only supports time-range in [`brave_category`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.brave.brave_category "searx.engines.brave.brave_category") `search` (UI category All) and in the goggles category. 

searx.engines.brave.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch [languages](https://docs.searxng.org/dev/engines/online/brave.html#brave-languages) and [regions](https://docs.searxng.org/dev/engines/online/brave.html#brave-regions) from Brave.
## Brave API Engine
Engine to search using the Brave (WEB) Search API.
### Configuration
The engine has the following mandatory setting:
  * [`api_key`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.braveapi.api_key "searx.engines.braveapi.api_key")

Optional settings are:
  * [`results_per_page`](https://docs.searxng.org/dev/engines/online/brave.html#searx.engines.braveapi.results_per_page "searx.engines.braveapi.results_per_page")

```
- name: braveapi
  engine: braveapi
  api_key: 'YOUR-API-KEY'  # required
  results_per_page: 20     # optional

```

The API supports paging and time filters. 

**engines.braveapi.api_key** = `''`
API key for Brave Search API (required). 

**engines.braveapi.results_per_page** = `20`
Maximum number of results per page (default 20). 

**engines.braveapi.base_url** = `'https://api.search.brave.com/res/v1/web/search'`
Base URL for the Brave Search API. 

**engines.braveapi.time_range_map** = `{'day': 'past_day', 'month': 'past_month', 'week': 'past_week', 'year': 'past_year'}`
Mapping of SearXNG time ranges to Brave API time ranges. 

**engines.braveapi.init(___)**
Initialize the engine. 

searx.engines.braveapi.request(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Create the API request. 

searx.engines.braveapi.response(_resp :[SXNG_Response](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Process the API response and return results.
The API engine requires an API key from Brave. This can be obtained from the [API Dashboard](https://api-dashboard.search.brave.com/).
