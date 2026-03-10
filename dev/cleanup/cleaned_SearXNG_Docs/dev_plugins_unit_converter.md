<!-- source: https://docs.searxng.org/dev/plugins/unit_converter.html -->

# Unit Converter
A plugin for converting measured values from one unit to another unit (a unit converter).
The plugin looks up the symbols (given in the query term) in a list of converters, each converter is one item in the list (compare `ADDITIONAL_UNITS`). If the symbols are ambiguous, the matching units of measurement are evaluated. The weighting in the evaluation results from the sorting of the `list of unit converters`. 

_class_ searx.plugins.unit_converter.SXNGPlugin(_plg_cfg :[PluginCfg](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins.PluginCfg")_) 
    
Convert between units. The result is displayed in area for the “answers”. 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'unit_converter'_ 
    
The ID (suffix) in the HTML form. 

post_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Runs AFTER the search request. Can return a list of [`Result`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result") objects to be added to the final result list.
