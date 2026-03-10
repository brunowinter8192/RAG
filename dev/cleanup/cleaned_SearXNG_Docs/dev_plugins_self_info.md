<!-- source: https://docs.searxng.org/dev/plugins/self_info.html -->

# Self-Info 

_class_ searx.plugins.self_info.SXNGPlugin(_plg_cfg :[PluginCfg](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins.PluginCfg")_) 
    
Simple plugin that displays information about user’s request, including the IP or HTTP User-Agent. The information is displayed in area for the “answers”. 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'self_info'_ 
    
The ID (suffix) in the HTML form. 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__=['ip', 'user-agent']_ 
    
Keywords in the search query that activate the plugin. The _keyword_ is the first word in a search query. If a plugin should be executed regardless of the search query, the list of keywords should be empty (which is also the default in the base class for Plugins). 

post_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Returns a result list only for the first page.
