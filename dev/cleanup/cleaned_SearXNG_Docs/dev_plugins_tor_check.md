<!-- source: https://docs.searxng.org/dev/plugins/tor_check.html -->

# Tor check
A plugin to check if the ip address of the request is a Tor exit-node if the user searches for `tor-check`. It fetches the tor exit node list from [`url_exit_list`](https://docs.searxng.org/dev/plugins/tor_check.html#searx.plugins.tor_check.url_exit_list "searx.plugins.tor_check.url_exit_list") and parses all the IPs into a list, then checks if the user’s IP address is in it. 

**plugins.tor_check.url_exit_list** = `'https://check.torproject.org/exit-addresses'`
URL to load Tor exit list from. 

_class_ searx.plugins.tor_check.SXNGPlugin(_plg_cfg :[PluginCfg](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins.PluginCfg")_) 
    
Rewrite hostnames, remove results or prioritize them. 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'tor_check'_ 
    
The ID (suffix) in the HTML form. 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__=['tor-check', 'tor_check', 'torcheck', 'tor', 'tor check']_ 
    
Keywords in the search query that activate the plugin. The _keyword_ is the first word in a search query. If a plugin should be executed regardless of the search query, the list of keywords should be empty (which is also the default in the base class for Plugins). 

post_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Runs AFTER the search request. Can return a list of [`Result`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result") objects to be added to the final result list.
