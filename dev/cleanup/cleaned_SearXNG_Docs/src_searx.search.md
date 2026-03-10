<!-- source: https://docs.searxng.org/src/searx.search.html -->

# Search 

_class_ searx.search.models.EngineRef(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _category :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Reference by names to an engine and category 

_final class_searx.search.models.SearchQuery(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _engineref_list :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[EngineRef](https://docs.searxng.org/src/searx.search.html#searx.search.models.EngineRef "searx.search.models.EngineRef")]_, _lang :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='all'_, _safesearch :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")[0,1,2]=0_, _pageno :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=1_, _time_range :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['day','week','month','year']|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _timeout_limit :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _external_bang :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _engine_data :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _redirect_to_first_result :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
container for all the search parameters (query, language, etc…) 

_class_ searx.search.Search(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_) 
    
Search information container 

search_query _: searx.search.SearchQuery_ 

result_container _: searx.results.ResultContainer_ 

search() → searx.results.ResultContainer 

_class_ searx.search.SearchWithPlugins(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_, _request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _user_plugins :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) 
    
Inherit from the Search class, add calls to the plugins. 

search_query _: searx.search.SearchQuery_ 

result_container _: searx.results.ResultContainer_ 

ordered_plugin_list _:[ List](https://docs.python.org/3/library/typing.html#typing.List "\(in Python v3.14\)")_ 

request _: flask.request_ 

search() → searx.results.ResultContainer 
