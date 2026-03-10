<!-- source: https://docs.searxng.org/dev/engines/online/peertube.html -->

# Peertube Engines
## Peertube Video
Peertube and [`SepiaSearch`](https://docs.searxng.org/dev/engines/online/peertube.html#module-searx.engines.sepiasearch "searx.engines.sepiasearch") do share (more or less) the same REST API and the schema of the JSON result is identical. 

**engines.peertube.base_url** = `'https://peer.tube'`
Base URL of the Peertube instance. A list of instances is available at:
  * <https://instances.joinpeertube.org/instances>

**engines.peertube.request(_query_ , _params_)**
Assemble request for the Peertube API 

**engines.peertube.video_response(_resp_)**
Parse video response from SepiaSearch and Peertube instances. 

searx.engines.peertube.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch languages from peertube’s search-index source code.
See [videoLanguages](https://framagit.org/framasoft/peertube/search-index/-/commit/8ed5c729#3d8747f9a60695c367c70bb64efba8f403721fad_0_291) in commit [8ed5c729 - Refactor and redesign client](https://framagit.org/framasoft/peertube/search-index/-/commit/8ed5c729)
## SepiaSearch
SepiaSearch uses the same languages as [`Peertube`](https://docs.searxng.org/dev/engines/online/peertube.html#module-searx.engines.peertube "searx.engines.peertube") and the response is identical to the response from the peertube engines. 

**engines.sepiasearch.request(_query_ , _params_)**
Assemble request for the SepiaSearch API
