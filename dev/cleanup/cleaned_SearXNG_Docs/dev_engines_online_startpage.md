<!-- source: https://docs.searxng.org/dev/engines/online/startpage.html -->

# Startpage Engines
Startpage’s language & region selectors are a mess ..
## Startpage regions
In the list of regions there are tags we need to map to common region tags:
```
pt-BR_BR --> pt_BR
zh-CN_CN --> zh_Hans_CN
zh-TW_TW --> zh_Hant_TW
zh-TW_HK --> zh_Hant_HK
en-GB_GB --> en_GB

```

and there is at least one tag with a three letter language tag (ISO 639-2):
```
fil_PH --> fil_PH

```

The locale code `no_NO` from Startpage does not exists and is mapped to `nb-NO`:
```
babel.core.UnknownLocaleError: unknown locale 'no_NO'

```

For reference see languages-subtag at iana; `no` is the macrolanguage [[1]](https://docs.searxng.org/dev/engines/online/startpage.html#id5) and W3C recommends subtag over macrolanguage [[2]](https://docs.searxng.org/dev/engines/online/startpage.html#id6).
[[1](https://docs.searxng.org/dev/engines/online/startpage.html#id3)]
[iana: language-subtag-registry](https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry)
```
type: language
Subtag: nb
Description: Norwegian Bokmål
Added: 2005-10-16
Suppress-Script: Latn
Macrolanguage: no

```

[[2](https://docs.searxng.org/dev/engines/online/startpage.html#id4)]
Use macrolanguages with care. Some language subtags have a Scope field set to macrolanguage, i.e. this primary language subtag encompasses a number of more specific primary language subtags in the registry. … As we recommended for the collection subtags mentioned above, in most cases you should try to use the more specific subtags … [W3: The primary language subtag](https://www.w3.org/International/questions/qa-choosing-language-tags#langsubtag)
## Startpage languages
HTTP `Accept-Language` header (`send_accept_language_header`):
    
The displayed name in Startpage’s settings page depend on the location of the IP when `Accept-Language` HTTP header is unset.
Startpage tries to guess user’s language and territory from the HTTP `Accept-Language`. Optional the user can select a search-language (can be different to the UI language) and a region filter.
In [`fetch_traits`](https://docs.searxng.org/dev/engines/online/startpage.html#searx.engines.startpage.fetch_traits "searx.engines.startpage.fetch_traits") we use:
```
'Accept-Language': "en-US,en;q=0.5",
..

```

to get uniform names independent from the IP).
## Startpage categories
Startpage’s category (for Web-search, News, Videos, ..) is set by [`startpage_categ`](https://docs.searxng.org/dev/engines/online/startpage.html#searx.engines.startpage.startpage_categ "searx.engines.startpage.startpage_categ") in settings.yml:
```
- name: startpage
  engine: startpage
  startpage_categ: web
  ...

```

Hint
Supported categories are `web`, `news` and `images`. 

**engines.startpage.startpage_categ** = `'web'`
Startpage’s category, visit [Startpage categories](https://docs.searxng.org/dev/engines/online/startpage.html#startpage-categories). 

**engines.startpage.max_page** = `18`
Tested 18 pages maximum (argument `page`), to be save max is set to 20. 

**engines.startpage.search_form_xpath** = `'//form[@id="search"]'`
XPath of Startpage’s origin search form 

searx.engines.startpage.CACHE _:[ EngineCache](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.EngineCache "searx.enginelib.EngineCache")_ 
    
Persistent (SQLite) key/value cache that deletes its values after `expire` seconds. 

**engines.startpage.sc_code_cache_sec** = `3600`
Time in seconds the sc-code is cached in memory [`get_sc_code`](https://docs.searxng.org/dev/engines/online/startpage.html#searx.engines.startpage.get_sc_code "searx.engines.startpage.get_sc_code"). 

**engines.startpage.get_sc_code(_params_)**
Get an actual `sc` argument from Startpage’s search form (HTML page).
Startpage puts a `sc` argument on every HTML [`search form`](https://docs.searxng.org/dev/engines/online/startpage.html#searx.engines.startpage.search_form_xpath "searx.engines.startpage.search_form_xpath"). Without this argument Startpage considers the request is from a bot. We do not know what is encoded in the value of the `sc` argument, but it seems to be a kind of a _timestamp_.
Startpage’s search form generates a new sc-code on each request. This function scrapes a new sc-code from Startpage’s home page every [`sc_code_cache_sec`](https://docs.searxng.org/dev/engines/online/startpage.html#searx.engines.startpage.sc_code_cache_sec "searx.engines.startpage.sc_code_cache_sec") seconds. 

**engines.startpage.request(_query_ , _params_)**
Assemble a Startpage request.
To avoid CAPTCHAs we need to send a well formed HTTP POST request with a cookie. We need to form a request that is identical to the request built by Startpage’s search form:
  * in the cookie the **region** is selected
  * in the HTTP POST data the **language** is selected

Additionally the arguments form Startpage’s search form needs to be set in HTML POST data / compare `<input>` elements: [`search_form_xpath`](https://docs.searxng.org/dev/engines/online/startpage.html#searx.engines.startpage.search_form_xpath "searx.engines.startpage.search_form_xpath"). 

searx.engines.startpage.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch [languages](https://docs.searxng.org/dev/engines/online/startpage.html#startpage-languages) and [regions](https://docs.searxng.org/dev/engines/online/startpage.html#startpage-regions) from Startpage.
