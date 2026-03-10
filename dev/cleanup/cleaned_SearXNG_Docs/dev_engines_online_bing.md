<!-- source: https://docs.searxng.org/dev/engines/online/bing.html -->

# Bing Engines
## Bing WEB
This is the implementation of the Bing-WEB engine. Some of this implementations are shared by other engines:
On the [preference page](https://www.bing.com/account/general) Bing offers a lot of languages an regions (see section LANGUAGE and COUNTRY/REGION). The Language is the language of the UI, we need in SearXNG to get the translations of data such as _“published last week”_.
There is a description of the official [search-APIs](https://learn.microsoft.com/en-us/bing/search-apis/), unfortunately this is not the API we can use or that bing itself would use. You can look up some things in the API to get a better picture of bing, but the value specifications like the market codes are usually outdated or at least no longer used by bing itself.
The market codes have been harmonized and are identical for web, video and images. The news area has also been harmonized with the other categories. Only political adjustments still seem to be made – for example, there is no news category for the Chinese market. 

**engines.bing.max_page** = `200`
200 pages maximum (`&first=1991`) 

**engines.bing.safesearch** = `True`
Bing results are always SFW. To get NSFW links from bing some age verification by a cookie is needed / thats not possible in SearXNG. 

**engines.bing.base_url** = `'https://www.bing.com/search'`
Bing (Web) search URL 

**engines.bing.request(_query_ , _params_)**
Assemble a Bing-Web request. 

searx.engines.bing.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch languages and regions from Bing-Web.
## Bing Images
Bing-Images: description see [`searx.engines.bing`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing "searx.engines.bing"). 

**engines.bing_images.base_url** = `'https://www.bing.com/images/async'`
Bing (Images) search URL 

**engines.bing_images.request(_query_ , _params_)**
Assemble a Bing-Image request. 

**engines.bing_images.response(_resp_)**
Get response from Bing-Images
## Bing Videos
Bing-Videos: description see [`searx.engines.bing`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing "searx.engines.bing"). 

**engines.bing_videos.base_url** = `'https://www.bing.com/videos/asyncv2'`
Bing (Videos) async search URL. 

**engines.bing_videos.request(_query_ , _params_)**
Assemble a Bing-Video request. 

**engines.bing_videos.response(_resp_)**
Get response from Bing-Video
## Bing News
Bing-News: description see [`searx.engines.bing`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing "searx.engines.bing").
Hint
Bing News is _different_ in some ways! 

**engines.bing_news.paging** = `True`
If go through the pages and there are actually no new results for another page, then bing returns the results from the last page again. 

**engines.bing_news.time_map** = `{'day': 'interval="4"', 'month': 'interval="9"', 'week': 'interval="7"'}`
A string ‘4’ means _last hour_. We use _last hour_ for `day` here since the difference of _last day_ and _last week_ in the result list is just marginally. Bing does not have news range `year` / we use `month` instead. 

**engines.bing_news.base_url** = `'https://www.bing.com/news/infinitescrollajax'`
Bing (News) search URL 

**engines.bing_news.request(_query_ , _params_)**
Assemble a Bing-News request. 

**engines.bing_news.response(_resp_)**
Get response from Bing-Video 

searx.engines.bing_news.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch languages and regions from Bing-News.
