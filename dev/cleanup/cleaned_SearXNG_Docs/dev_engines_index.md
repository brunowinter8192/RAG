<!-- source: https://docs.searxng.org/dev/engines/index.html -->

# Engine Implementations
Framework Components
  * [Engine Library](https://docs.searxng.org/dev/engines/enginelib.html)
  * [SearXNG’s engines loader](https://docs.searxng.org/dev/engines/engines.html)
  * [Engine Overview](https://docs.searxng.org/dev/engines/engine_overview.html)
## ResultList and engines
_class_ searx.result_types.ResultList 
    
Base class of all result lists (abstract). 

_class_ searx.result_types.EngineResults 
    
Result list that should be used by engine developers. For convenience, engine developers don’t need to import types / see `ResultList.types`.
```
from searx.result_types import EngineResults
...
def response(resp) -> EngineResults:
    res = EngineResults()
    ...
    res.add( res.types.Answer(answer="lorem ipsum ..", url="https://example.org") )
    ...
    return res

```

## Engine Types
The [`engine_type`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.engine_type "searx.enginelib.Engine.engine_type") of an engine determines which [search processor](https://docs.searxng.org/src/searx.search.processors.html#searx-search-processors) is used by the engine.
In this section a list of the engines that are documented is given, a complete list of the engines can be found in the source under: [git://searx/engines](https://github.com/searxng/searxng/blob/master/searx/engines).
### Online Engines
> **Info:**
  * [`processors.online`](https://docs.searxng.org/src/searx.search.processors.html#module-searx.search.processors.online "searx.search.processors.online")

  * [Demo Online Engine](https://docs.searxng.org/dev/engines/demo/demo_online.html)
  * [XPath Engine](https://docs.searxng.org/dev/engines/xpath.html)
  * [MediaWiki Engine](https://docs.searxng.org/dev/engines/mediawiki.html)
  * [JSON Engine](https://docs.searxng.org/dev/engines/json_engine.html)

  * [Adobe Stock](https://docs.searxng.org/dev/engines/online/adobe_stock.html)
  * [Alpine Linux Packages](https://docs.searxng.org/dev/engines/online/alpinelinux.html)
  * [Anna’s Archive](https://docs.searxng.org/dev/engines/online/annas_archive.html)
  * [Arch Linux](https://docs.searxng.org/dev/engines/online/archlinux.html)
  * [arXiv](https://docs.searxng.org/dev/engines/online/arxiv.html)
  * [Astrophysics Data System (ADS)](https://docs.searxng.org/dev/engines/online/astrophysics_data_system.html)
  * [Azure Resources](https://docs.searxng.org/dev/engines/online/azure.html)
  * [Bing Engines](https://docs.searxng.org/dev/engines/online/bing.html)
  * [Bpb](https://docs.searxng.org/dev/engines/online/bpb.html)
  * [Brave Engines](https://docs.searxng.org/dev/engines/online/brave.html)
  * [BT4G](https://docs.searxng.org/dev/engines/online/bt4g.html)
  * [ChinaSo](https://docs.searxng.org/dev/engines/online/chinaso.html)
  * [CORE](https://docs.searxng.org/dev/engines/online/core.html)
  * [Crossref](https://docs.searxng.org/dev/engines/online/crossref.html)
  * [Dailymotion](https://docs.searxng.org/dev/engines/online/dailymotion.html)
  * [Discourse Forums](https://docs.searxng.org/dev/engines/online/discourse.html)
  * [DuckDuckGo Engines](https://docs.searxng.org/dev/engines/online/duckduckgo.html)
  * [Geizhals](https://docs.searxng.org/dev/engines/online/geizhals.html)
  * [Gitea](https://docs.searxng.org/dev/engines/online/gitea.html)
  * [Github Code](https://docs.searxng.org/dev/engines/online/github_code.html)
  * [GitLab](https://docs.searxng.org/dev/engines/online/gitlab.html)
  * [Google Engines](https://docs.searxng.org/dev/engines/online/google.html)
  * [Hugging Face](https://docs.searxng.org/dev/engines/online/huggingface.html)
  * [Lemmy](https://docs.searxng.org/dev/engines/online/lemmy.html)
  * [Library of Congress](https://docs.searxng.org/dev/engines/online/loc.html)
  * [Marginalia Search](https://docs.searxng.org/dev/engines/online/marginalia.html)
  * [Mastodon](https://docs.searxng.org/dev/engines/online/mastodon.html)
  * [Moviepilot](https://docs.searxng.org/dev/engines/online/moviepilot.html)
  * [Matrix Rooms Search (MRS)](https://docs.searxng.org/dev/engines/online/mrs.html)
  * [Mwmbl Engine](https://docs.searxng.org/dev/engines/online/mwmbl.html)
  * [Odysee](https://docs.searxng.org/dev/engines/online/odysee.html)
  * [OpenAlex](https://docs.searxng.org/dev/engines/online/openalex.html)
  * [Open Library](https://docs.searxng.org/dev/engines/online/openlibrary.html)
  * [Peertube Engines](https://docs.searxng.org/dev/engines/online/peertube.html)
  * [Piped](https://docs.searxng.org/dev/engines/online/piped.html)
  * [Presearch Engine](https://docs.searxng.org/dev/engines/online/presearch.html)
  * [PubMed](https://docs.searxng.org/dev/engines/online/pubmed.html)
  * [Qwant](https://docs.searxng.org/dev/engines/online/qwant.html)
  * [RadioBrowser](https://docs.searxng.org/dev/engines/online/radio_browser.html)
  * [Recoll Engine](https://docs.searxng.org/dev/engines/online/recoll.html)
  * [Repology](https://docs.searxng.org/dev/engines/online/repology.html)
  * [Reuters](https://docs.searxng.org/dev/engines/online/reuters.html)
  * [Semantic Scholar](https://docs.searxng.org/dev/engines/online/semantic_scholar.html)
  * [Soundcloud](https://docs.searxng.org/dev/engines/online/soundcloud.html)
  * [Sourcehut](https://docs.searxng.org/dev/engines/online/sourcehut.html)
  * [Springer Nature](https://docs.searxng.org/dev/engines/online/springer.html)
  * [Startpage Engines](https://docs.searxng.org/dev/engines/online/startpage.html)
  * [Tagesschau API](https://docs.searxng.org/dev/engines/online/tagesschau.html)
  * [Torznab WebAPI](https://docs.searxng.org/dev/engines/online/torznab.html)
  * [Tube Archivist](https://docs.searxng.org/dev/engines/online/tubearchivist.html)
  * [Void Linux binary packages](https://docs.searxng.org/dev/engines/online/void.html)
  * [Wallhaven](https://docs.searxng.org/dev/engines/online/wallhaven.html)
  * [Wikimedia](https://docs.searxng.org/dev/engines/online/wikipedia.html)
  * [Yacy](https://docs.searxng.org/dev/engines/online/yacy.html)
  * [Yahoo Engine](https://docs.searxng.org/dev/engines/online/yahoo.html)
  * [Z-Library](https://docs.searxng.org/dev/engines/online/zlibrary.html)

### Offline Engines
> **Info:**
  * [`processors.offline`](https://docs.searxng.org/src/searx.search.processors.html#module-searx.search.processors.offline "searx.search.processors.offline")

  * [Offline Concept](https://docs.searxng.org/dev/engines/offline_concept.html)
  * [Demo Offline Engine](https://docs.searxng.org/dev/engines/demo/demo_offline.html)
  * [Command Line Engines](https://docs.searxng.org/dev/engines/offline/command-line-engines.html)
  * [NoSQL databases](https://docs.searxng.org/dev/engines/offline/nosql-engines.html)
  * [Local Search APIs](https://docs.searxng.org/dev/engines/offline/search-indexer-engines.html)
  * [SQL Engines](https://docs.searxng.org/dev/engines/offline/sql-engines.html)

### Online URL Search
> **Info:**
  * [`processors.online_url_search`](https://docs.searxng.org/src/searx.search.processors.html#module-searx.search.processors.online_url_search "searx.search.processors.online_url_search")

  * [Tineye](https://docs.searxng.org/dev/engines/online_url_search/tineye.html)

### Online Currency
> **Info:**
  * [`processors.online_currency`](https://docs.searxng.org/src/searx.search.processors.html#module-searx.search.processors.online_currency "searx.search.processors.online_currency")

_no engine of this type is documented yet / coming soon_
### Online Dictionary
> **Info:**
  * [`processors.online_dictionary`](https://docs.searxng.org/src/searx.search.processors.html#module-searx.search.processors.online_dictionary "searx.search.processors.online_dictionary")

_no engine of this type is documented yet / coming soon_
