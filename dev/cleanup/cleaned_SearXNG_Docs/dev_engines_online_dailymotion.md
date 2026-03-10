<!-- source: https://docs.searxng.org/dev/engines/online/dailymotion.html -->

# Dailymotion
  * [Dailymotion (Videos)](https://docs.searxng.org/dev/engines/online/dailymotion.html#dailymotion-videos)

## Dailymotion (Videos)
**engines.dailymotion.safesearch_params** = `{0: {}, 1: {'is_created_for_kids': 'true'}, 2: {'is_created_for_kids': 'true'}}`
True if this video is “Created for Kids” / intends to target an audience under the age of 16 (`is_created_for_kids` in [Video filters API](https://developers.dailymotion.com/api/#video-filters) ) 

**engines.dailymotion.family_filter_map** = `{0: 'false', 1: 'true', 2: 'true'}`
By default, the family filter is turned on. Setting this parameter to `false` will stop filtering-out explicit content from searches and global contexts (`family_filter` in [Global API Parameters](https://developers.dailymotion.com/api/#global-parameters) ). 

**engines.dailymotion.result_fields** = `['allow_embed', 'description', 'title', 'created_time', 'duration', 'url', 'thumbnail_360_url', 'id']`
[Fields selection](https://developers.dailymotion.com/api/#fields-selection), by default, a few fields are returned. To request more specific fields, the `fields` parameter is used with the list of fields SearXNG needs in the response to build a video result list. 

**engines.dailymotion.search_url** = `'https://api.dailymotion.com/videos?'`
URL to retrieve a list of videos.
  * [REST GET](https://developers.dailymotion.com/tools/)
  * [Global API Parameters](https://developers.dailymotion.com/api/#global-parameters)
  * [Video filters API](https://developers.dailymotion.com/api/#video-filters)

**engines.dailymotion.iframe_src** = `'https://www.dailymotion.com/embed/video/{video_id}'`
URL template to embed video in SearXNG’s result list. 

searx.engines.dailymotion.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch locales & languages from dailymotion.
Locales fetched from [api/locales](https://api.dailymotion.com/locales). There are duplications in the locale codes returned from Dailymotion which can be ignored:
```
en_EN --> en_GB, en_US
ar_AA --> ar_EG, ar_AE, ar_SA

```

The language list [api/languages](https://api.dailymotion.com/languages) contains over 7000 _languages_ codes (see [PR1071](https://github.com/searxng/searxng/pull/1071)). We use only those language codes that are used in the locales.
