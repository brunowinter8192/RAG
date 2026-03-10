<!-- source: https://docs.searxng.org/dev/plugins/time_zone.html -->

# Time Zone 

_final class_searx.plugins.time_zone.SXNGPlugin(_plg_cfg :[PluginCfg](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins.PluginCfg")_) 
    
Plugin to display the current time at different timezones (usually the query city). 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'time_zone'_ 
    
The ID (suffix) in the HTML form. 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__=['time', 'timezone', 'now', 'clock', 'timezones']_ 
    
Keywords in the search query that activate the plugin. The _keyword_ is the first word in a search query. If a plugin should be executed regardless of the search query, the list of keywords should be empty (which is also the default in the base class for Plugins). 

post_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
The plugin uses the [`searx.weather.GeoLocation`](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation") class, which is already implemented in the context of weather forecasts, to determine the time zone. The [`searx.weather.DateTime`](https://docs.searxng.org/src/searx.weather.html#searx.weather.DateTime "searx.weather.DateTime") class is used for the localized display of date and time.
