<!-- source: https://docs.searxng.org/dev/engines/online/chinaso.html -->

# ChinaSo
[ChinaSo](https://www.chinaso.com/), a search engine for the chinese language area.
Attention
ChinaSo engine does not return real URL, the links from these search engines violate the privacy of the users!!
We try to find a solution for this problem, please follow [issue #4694](https://github.com/searxng/searxng/issues/4694).
As long as the problem has not been resolved, these engines are not active in a standard setup (`inactive: true`).
## Configuration
The engine has the following additional settings:
  * [`chinaso_category`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.chinaso_category "searx.engines.chinaso.chinaso_category") ([`ChinasoCategoryType`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.ChinasoCategoryType "searx.engines.chinaso.ChinasoCategoryType"))
  * [`chinaso_news_source`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.chinaso_news_source "searx.engines.chinaso.chinaso_news_source") ([`ChinasoNewsSourceType`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.ChinasoNewsSourceType "searx.engines.chinaso.ChinasoNewsSourceType"))

In the example below, all three ChinaSO engines are using the [network](https://docs.searxng.org/admin/settings/settings_engines.html#engine-network) from the `chinaso news` engine.
```
- name: chinaso news
  engine: chinaso
  shortcut: chinaso
  categories: [news]
  chinaso_category: news
  chinaso_news_source: all

- name: chinaso images
  engine: chinaso
  network: chinaso news
  shortcut: chinasoi
  categories: [images]
  chinaso_category: images

- name: chinaso videos
  engine: chinaso
  network: chinaso news
  shortcut: chinasov
  categories: [videos]
  chinaso_category: videos

```

## Implementations 

searx.engines.chinaso.ChinasoCategoryType 
    
ChinaSo supports news, videos, images search.
  * `news`: search for news
  * `videos`: search for videos
  * `images`: search for images

In the category `news` you can additionally filter by option [`chinaso_news_source`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.chinaso_news_source "searx.engines.chinaso.chinaso_news_source").
alias of [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")[‘news’, ‘videos’, ‘images’] 

**engines.chinaso.chinaso_category** = `'news'`
Configure ChinaSo category ([`ChinasoCategoryType`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.ChinasoCategoryType "searx.engines.chinaso.ChinasoCategoryType")). 

searx.engines.chinaso.ChinasoNewsSourceType 
    
Filtering ChinaSo-News results by source:
  * `CENTRAL`: central publication
  * `LOCAL`: local publication
  * `BUSINESS`: business publication
  * `EPAPER`: E-Paper
  * `all`: all sources

alias of [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")[‘CENTRAL’, ‘LOCAL’, ‘BUSINESS’, ‘EPAPER’, ‘all’] 

**engines.chinaso.chinaso_news_source** = `'all'`
Configure ChinaSo-News type ([`ChinasoNewsSourceType`](https://docs.searxng.org/dev/engines/online/chinaso.html#searx.engines.chinaso.ChinasoNewsSourceType "searx.engines.chinaso.ChinasoNewsSourceType")).
