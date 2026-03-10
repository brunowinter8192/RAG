<!-- source: https://docs.searxng.org/dev/engines/online/presearch.html -->

# Presearch Engine
Presearch supports the search types listed in [`search_type`](https://docs.searxng.org/dev/engines/online/presearch.html#searx.engines.presearch.search_type "searx.engines.presearch.search_type") (general, images, videos, news).
Configured `presarch` engines:
```
- name: presearch
  engine: presearch
  search_type: search
  categories: [general, web]

- name: presearch images
  ...
  search_type: images
  categories: [images, web]

- name: presearch videos
  ...
  search_type: videos
  categories: [general, web]

- name: presearch news
  ...
  search_type: news
  categories: [news, web]

```

Hint
By default Presearch’s video category is intentionally placed into:
```
categories: [general, web]

```

## Search type `video`
The results in the video category are most often links to pages that contain a video, for instance many links from Preasearch’s video category link content from facebook (aka Meta) or Twitter (aka X). Since these are not real links to video streams SearXNG can’t use the video template for this and if SearXNG can’t use this template, then the user doesn’t want to see these hits in the videos category.
## Languages & Regions
In Presearch there are languages for the UI and regions for narrowing down the search. If we set “auto” for the region in the WEB-UI of Presearch and cookie `use_local_search_results=false`, then the defaults are set for both (the language and the region) from the `Accept-Language` header.
Since the region is already “auto” by default, we only need to set the `use_local_search_results` cookie and send the `Accept-Language` header. We have to set these values in both requests we send to Presearch; in the first request to get the request-ID from Presearch and in the final request to get the result list.
The time format returned by Presearch varies depending on the language set. Multiple different formats can be supported by using `dateutil` parser, but it doesn’t support formats such as “N time ago”, “vor N time” (German), “Hace N time” (Spanish). Because of this, the dates are simply joined together with the rest of other metadata.
## Implementations
**engines.presearch.search_type** = `'search'`
must be any of `search`, `images`, `videos`, `news`
