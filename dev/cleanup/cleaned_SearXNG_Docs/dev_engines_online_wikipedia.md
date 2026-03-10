<!-- source: https://docs.searxng.org/dev/engines/online/wikipedia.html -->

# Wikimedia
## Wikipedia
This module implements the Wikipedia engine. Some of this implementations are shared by other engines:
  * [Wikidata](https://docs.searxng.org/dev/engines/online/wikipedia.html#wikidata-engine)

The list of supported languages is [`fetched`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.fetch_wikimedia_traits "searx.engines.wikipedia.fetch_wikimedia_traits") from the article linked by [`list_of_wikipedias`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.list_of_wikipedias "searx.engines.wikipedia.list_of_wikipedias").
Unlike traditional search engines, wikipedia does not support one Wikipedia for all languages, but there is one Wikipedia for each supported language. Some of these Wikipedias have a [LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter) enabled ([`rest_v1_summary_url`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.rest_v1_summary_url "searx.engines.wikipedia.rest_v1_summary_url")).
A [LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter) (LC) is a system based on language variants that automatically converts the content of a page into a different variant. A variant is mostly the same language in a different script.
  * [Wikipedias in multiple writing systems](https://meta.wikimedia.org/wiki/Wikipedias_in_multiple_writing_systems)
  * [Automatic conversion between traditional and simplified Chinese characters](https://en.wikipedia.org/wiki/Chinese_Wikipedia#Automatic_conversion_between_traditional_and_simplified_Chinese_characters)

[PR-2554](https://github.com/searx/searx/pull/2554):
    
The Wikipedia link returned by the API is still the same in all cases ([https://zh.wikipedia.org/wiki/出租車](https://zh.wikipedia.org/wiki/%E5%87%BA%E7%A7%9F%E8%BB%8A)) but if your browser’s `Accept-Language` is set to any of `zh`, `zh-CN`, `zh-TW`, `zh-HK` or .. Wikipedia’s LC automatically returns the desired script in their web-page.
  * You can test the API here: <https://reqbin.com/gesg2kvx>

To support Wikipedia’s [LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter), a SearXNG request to Wikipedia uses [`get_wiki_params`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.get_wiki_params "searx.engines.wikipedia.get_wiki_params") and `wiki_lc_locale_variants' in the :py:obj:`fetch_wikimedia_traits` function.
To test in SearXNG, query for `!wp 出租車` with each of the available Chinese options:
  * `!wp 出租車 :zh` should show 出租車
  * `!wp 出租車 :zh-CN` should show 出租车
  * `!wp 出租車 :zh-TW` should show 計程車
  * `!wp 出租車 :zh-HK` should show 的士
  * `!wp 出租車 :zh-SG` should show 德士

**engines.wikipedia.display_type** = `['infobox']`
A list of display types composed from `infobox` and `list`. The latter one will add a hit to the result list. The first one will show a hit in the info box. Both values can be set, or one of the two can be set. 

**engines.wikipedia.list_of_wikipedias** = `'https://meta.wikimedia.org/wiki/List_of_Wikipedias'`
[List of all wikipedias](https://meta.wikimedia.org/wiki/List_of_Wikipedias) 

**engines.wikipedia.wikipedia_article_depth** = `'https://meta.wikimedia.org/wiki/Wikipedia_article_depth'`
The _editing depth_ of Wikipedia is one of several possible rough indicators of the encyclopedia’s collaborative quality, showing how frequently its articles are updated. The measurement of depth was introduced after some limitations of the classic measurement of article count were realized. 

**engines.wikipedia.rest_v1_summary_url** = `'https://{wiki_netloc}/api/rest_v1/page/summary/{title}'`
[wikipedia rest_v1 summary API](https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_summary__title_):
    
The summary response includes an extract of the first paragraph of the page in plain text and HTML as well as the type of page. This is useful for page previews (fka. Hovercards, aka. Popups) on the web and link previews in the apps. 

HTTP `Accept-Language` header (`send_accept_language_header`):
    
The desired language variant code for wikis where [LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter) is enabled. 

**engines.wikipedia.wiki_lc_locale_variants** = `{'zh': ('zh-CN', 'zh-HK', 'zh-MO', 'zh-MY', 'zh-SG', 'zh-TW'), 'zh-classical': ('zh-classical',)}`
Mapping rule of the [LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter) to map a language and its variants to a Locale (used in the HTTP `Accept-Language` header). For example see [LC Chinese](https://meta.wikimedia.org/wiki/Wikipedias_in_multiple_writing_systems#Chinese). 

**engines.wikipedia.get_wiki_params(_sxng_locale_ , _eng_traits_)**
Returns the Wikipedia language tag and the netloc that fits to the `sxng_locale`. To support [LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems#LanguageConverter) this function rates a locale (region) higher than a language (compare [`wiki_lc_locale_variants`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.wiki_lc_locale_variants "searx.engines.wikipedia.wiki_lc_locale_variants")). 

**engines.wikipedia.request(_query_ , _params_)**
Assemble a request ([wikipedia rest_v1 summary API](https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_summary__title_)). 

searx.engines.wikipedia.fetch_wikimedia_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch languages from Wikipedia. Not all languages from the [`list_of_wikipedias`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.list_of_wikipedias "searx.engines.wikipedia.list_of_wikipedias") are supported by SearXNG locales, only those known from [`searx.locales.LOCALE_NAMES`](https://docs.searxng.org/src/searx.locales.html#searx.locales.LOCALE_NAMES "searx.locales.LOCALE_NAMES") or those with a minimal [`editing depth`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.wikipedia_article_depth "searx.engines.wikipedia.wikipedia_article_depth").
The location of the Wikipedia address of a language is mapped in a [`custom field`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits.custom "searx.enginelib.traits.EngineTraits.custom") (`wiki_netloc`). Here is a reduced example:
```
traits.custom['wiki_netloc'] = {
    "en": "en.wikipedia.org",
    ..
    "gsw": "als.wikipedia.org",
    ..
    "zh": "zh.wikipedia.org",
    "zh-classical": "zh-classical.wikipedia.org"
}

```

## Wikidata
This module implements the Wikidata engine. Some implementations are shared from [Wikipedia](https://docs.searxng.org/dev/engines/online/wikipedia.html#wikipedia-engine). 

**engines.wikidata.display_type** = `['infobox']`
A list of display types composed from `infobox` and `list`. The latter one will add a hit to the result list. The first one will show a hit in the info box. Both values can be set, or one of the two can be set. 

**engines.wikidata.get_thumbnail(_img_src_)**
Get Thumbnail image from wikimedia commons
Images from commons.wikimedia.org are (HTTP) redirected to upload.wikimedia.org. The redirected URL can be calculated by this function.
  * <https://stackoverflow.com/a/33691240>

searx.engines.wikidata.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Uses languages evaluated from [`wikipedia.fetch_wikimedia_traits`](https://docs.searxng.org/dev/engines/online/wikipedia.html#searx.engines.wikipedia.fetch_wikimedia_traits "searx.engines.wikipedia.fetch_wikimedia_traits") and removes
  * `traits.custom['wiki_netloc']`: wikidata does not have net-locations for the languages and the list of all
  * `traits.custom['WIKIPEDIA_LANGUAGES']`: not used in the wikipedia engine
