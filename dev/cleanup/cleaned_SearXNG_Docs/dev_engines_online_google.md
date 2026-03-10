<!-- source: https://docs.searxng.org/dev/engines/online/google.html -->

# Google Engines
## Google API
SearXNG’s implementation of the Google API is mainly done in [`get_google_info`](https://docs.searxng.org/dev/engines/online/google.html#searx.engines.google.get_google_info "searx.engines.google.get_google_info").
For detailed description of the _REST-full_ API see: [Query Parameter Definitions](https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions). The linked API documentation can sometimes be helpful during reverse engineering. However, we cannot use it in the freely accessible WEB services; not all parameters can be applied and some engines are more _special_ than other (e.g. [Google News](https://docs.searxng.org/dev/engines/online/google.html#google-news-engine)).
## Google WEB
This is the implementation of the Google WEB engine. Some of this implementations (manly the [`get_google_info`](https://docs.searxng.org/dev/engines/online/google.html#searx.engines.google.get_google_info "searx.engines.google.get_google_info")) are shared by other engines:
**engines.google.max_page** = `50`
[Google max 50 pages](https://github.com/searxng/searxng/issues/2982) 

searx.engines.google.ui_async(_start :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Format of the response from UI’s async request.
  * `arc_id:<...>,use_ac:true,_fmt:prog`

The arc_id is random generated every hour. 

searx.engines.google.get_google_info(_params :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_, _eng_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) → [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] 
    
Composing various (language) properties for the google engines ([Google API](https://docs.searxng.org/dev/engines/online/google.html#google-api)).
This function is called by the various google engines ([Google WEB](https://docs.searxng.org/dev/engines/online/google.html#google-web-engine), [Google Images](https://docs.searxng.org/dev/engines/online/google.html#google-images-engine), [Google News](https://docs.searxng.org/dev/engines/online/google.html#google-news-engine) and [Google Videos](https://docs.searxng.org/dev/engines/online/google.html#google-videos-engine)). 

Parameters: 
    
  * **param** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")) – Request parameters of the engine. At least a `searxng_locale` key should be in the dictionary.
  * **eng_traits** – Engine’s traits fetched from google preferences ([`searx.enginelib.traits.EngineTraits`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits"))

Return type: 
    
[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)") 

Returns: 
    
Py-Dictionary with the key/value pairs: 

language:
    
The language code that is used by google (e.g. `lang_en` or `lang_zh-TW`) 

country:
    
The country code that is used by google (e.g. `US` or `TW`) 

locale:
    
A instance of [`babel.core.Locale`](https://babel.readthedocs.io/en/latest/api/core.html#babel.core.Locale "\(in Babel v2.2\)") build from the `searxng_locale` value. 

subdomain:
    
Google subdomain `google_domains` that fits to the country code. 

params:
    
Py-Dictionary with additional request arguments (can be passed to [`urllib.parse.urlencode()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode "\(in Python v3.14\)")).
  * `hl` parameter: specifies the interface language of user interface.
  * `lr` parameter: restricts search results to documents written in a particular language.
  * `cr` parameter: restricts search results to documents originating in a particular country.
  * `ie` parameter: sets the character encoding scheme that should be used to interpret the query string (‘utf8’).
  * `oe` parameter: sets the character encoding scheme that should be used to decode the XML result (‘utf8’).

headers:
    
Py-Dictionary with additional HTTP headers (can be passed to request’s headers)
  * `Accept: '*/*`

searx.engines.google.request(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Google search request 

searx.engines.google.response(_resp :[SXNG_Response](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")_) 
    
Get response from google’s search request 

searx.engines.google.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_, _add_domains :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=True_) 
    
Fetch languages from Google.
## Google Autocomplete
searx.autocomplete.google_complete(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _sxng_locale :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Autocomplete from Google. Supports Google’s languages and subdomains ([`searx.engines.google.get_google_info`](https://docs.searxng.org/dev/engines/online/google.html#searx.engines.google.get_google_info "searx.engines.google.get_google_info")) by using the async REST API:
```
https://{subdomain}/complete/search?{args}

```

## Google Images
This is the implementation of the Google Images engine using the internal Google API used by the Google Go Android app.
This internal API offer results in
  * JSON (`_fmt:json`)
  * [Protobuf](https://en.wikipedia.org/wiki/Protocol_Buffers) (`_fmt:pb`)
  * [Protobuf](https://en.wikipedia.org/wiki/Protocol_Buffers) compressed? (`_fmt:pc`)
  * HTML (`_fmt:html`)
  * [Protobuf](https://en.wikipedia.org/wiki/Protocol_Buffers) encoded in JSON (`_fmt:jspb`).

**engines.google_images.max_page** = `50`
[Google max 50 pages](https://github.com/searxng/searxng/issues/2982) 

**engines.google_images.request(_query_ , _params_)**
Google-Image search request 

**engines.google_images.response(_resp_)**
Get response from google’s search request
## Google Videos
This is the implementation of the Google Videos engine.
Content-Security-Policy (CSP)
This engine needs to allow images from the [data URLs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs) (prefixed with the `data:` scheme):
```
Header set Content-Security-Policy "img-src 'self' data: ;"

```

**engines.google_videos.request(_query_ , _params_)**
Google-Video search request 

**engines.google_videos.response(_resp_)**
Get response from google’s search request
## Google News
This is the implementation of the Google News engine.
Google News has a different region handling compared to Google WEB.
  * the `ceid` argument has to be set ([`ceid_list`](https://docs.searxng.org/dev/engines/online/google.html#searx.engines.google_news.ceid_list "searx.engines.google_news.ceid_list"))
  * the [hl](https://developers.google.com/custom-search/docs/xml_results#hlsp) argument has to be set correctly (and different to Google WEB)
  * the [gl](https://developers.google.com/custom-search/docs/xml_results#glsp) argument is mandatory

If one of this argument is not set correctly, the request is redirected to CONSENT dialog:
```
https://consent.google.com/m?continue=

```

The google news API ignores some parameters from the common [Google API](https://docs.searxng.org/dev/engines/online/google.html#google-api):
  * [num](https://developers.google.com/custom-search/docs/xml_results#numsp) : the number of search results is ignored / there is no paging all results for a query term are in the first response.
  * [save](https://developers.google.com/custom-search/docs/xml_results#safesp) : is ignored / Google-News results are always _SafeSearch_

**engines.google_news.request(_query_ , _params_)**
Google-News search request 

**engines.google_news.response(_resp_)**
Get response from google’s search request 

**engines.google_news.ceid_list** = `['AE:ar', 'AR:es-419', 'AT:de', 'AU:en', 'BD:bn', 'BE:fr', 'BE:nl', 'BG:bg', 'BR:pt-419', 'BW:en', 'CA:en', 'CA:fr', 'CH:de', 'CH:fr', 'CL:es-419', 'CN:zh-Hans', 'CO:es-419', 'CU:es-419', 'CZ:cs', 'DE:de', 'EG:ar', 'ES:es', 'ET:en', 'FR:fr', 'GB:en', 'GH:en', 'GR:el', 'HK:zh-Hant', 'HU:hu', 'ID:en', 'ID:id', 'IE:en', 'IL:en', 'IL:he', 'IN:bn', 'IN:en', 'IN:hi', 'IN:ml', 'IN:mr', 'IN:ta', 'IN:te', 'IT:it', 'JP:ja', 'KE:en', 'KR:ko', 'LB:ar', 'LT:lt', 'LV:en', 'LV:lv', 'MA:fr', 'MX:es-419', 'MY:en', 'NA:en', 'NG:en', 'NL:nl', 'NO:no', 'NZ:en', 'PE:es-419', 'PH:en', 'PK:en', 'PL:pl', 'PT:pt-150', 'RO:ro', 'RS:sr', 'RU:ru', 'SA:ar', 'SE:sv', 'SG:en', 'SI:sl', 'SK:sk', 'SN:fr', 'TH:th', 'TR:tr', 'TW:zh-Hant', 'TZ:en', 'UA:ru', 'UA:uk', 'UG:en', 'US:en', 'US:es-419', 'VE:es-419', 'VN:vi', 'ZA:en', 'ZW:en']`
List of region/language combinations supported by Google News. Values of the `ceid` argument of the Google News REST API.
## Google Scholar
Google Scholar is a freely accessible web search engine that indexes the full text or metadata of scholarly literature across an array of publishing formats and disciplines.
Compared to other Google services the Scholar engine has a simple GET REST-API and there does not exists `async` API. Even though the API slightly vintage we can make use of the [Google API](https://docs.searxng.org/dev/engines/online/google.html#google-api) to assemble the arguments of the GET request.
### Configuration
```
- name: google scholar
  engine: google_scholar
  shortcut: gos

```

### Implementations
**engines.google_scholar.max_page** = `50`
[Google max 50 pages](https://github.com/searxng/searxng/issues/2982) 

searx.engines.google_scholar.request(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Google-Scholar search request 

searx.engines.google_scholar.response(_resp :[SXNG_Response](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Parse response from Google Scholar 

searx.engines.google_scholar.time_range_args(_params :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_) → [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")] 
    
Returns a dictionary with a time range arguments based on `params["time_range"]`.
Google Scholar supports a detailed search by year. Searching by _last month_ or _last week_ (as offered by SearXNG) is uncommon for scientific publications and is not supported by Google Scholar.
To limit the result list when the users selects a range, all the SearXNG ranges (_day_ , _week_ , _month_ , _year_) are mapped to _year_. If no range is set an empty dictionary of arguments is returned.
Example; when user selects a time range and we find ourselves in the year 2025 (current year minus one):
```
{ "as_ylo" : 2024 }

```

searx.engines.google_scholar.detect_google_captcha(_dom :[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")_) 
    
In case of CAPTCHA Google Scholar open its own _not a Robot_ dialog and is not redirected to `sorry.google.com`. 

searx.engines.google_scholar.parse_gs_a(_text :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")],[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")] 
    
Parse the text written in green.
Possible formats: * “{authors} - {journal}, {year} - {publisher}” * “{authors} - {year} - {publisher}” * “{authors} - {publisher}”
