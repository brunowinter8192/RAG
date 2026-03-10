<!-- source: https://docs.searxng.org/dev/extended_types.html -->

# Extended Types
This module implements the type extensions applied by SearXNG.
  * [`flask.request`](https://flask.palletsprojects.com/en/stable/api/#flask.request "\(in Flask v3.1.x\)") is replaced by [`sxng_request`](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.sxng_request "searx.extended_types.sxng_request")
  * [`flask.Request`](https://flask.palletsprojects.com/en/stable/api/#flask.Request "\(in Flask v3.1.x\)") is replaced by [`SXNG_Request`](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")
  * `httpx.response` is replaced by [`SXNG_Response`](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")

* * * 

searx.extended_types.sxng_request _:[ SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_ 
    
A replacement for [`flask.request`](https://flask.palletsprojects.com/en/stable/api/#flask.request "\(in Flask v3.1.x\)") with type cast [`SXNG_Request`](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request"). 

_class_ searx.extended_types.SXNG_Request(_environ :WSGIEnvironment_, _populate_request :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=True_, _shallow :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
SearXNG extends the class [`flask.Request`](https://flask.palletsprojects.com/en/stable/api/#flask.Request "\(in Flask v3.1.x\)") with properties from _this_ class definition, see type cast [`sxng_request`](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.sxng_request "searx.extended_types.sxng_request"). 

user_plugins _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
list of searx.plugins.Plugin.id (the id of the plugins) 

preferences _: searx.preferences.Preferences_ 
    
The preferences of the request. 

errors _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
A list of errors (translated text) added by `searx.webapp` in case of errors. 

start_time _:[ float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ 
    
Start time of the request, [`timeit.default_timer`](https://docs.python.org/3/library/timeit.html#timeit.default_timer "\(in Python v3.14\)") added by `searx.webapp` to calculate the total time of the request. 

render_time _:[ float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ 
    
Duration of the rendering, calculated and added by `searx.webapp`. 

timings _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[searx.results.Timing]_ 
    
A list of `searx.results.Timing` of the engines, calculatid in and hold by `searx.results.ResultContainer.timings`. 

remote_addr _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
The address of the client sending the request. 

_class_ searx.extended_types.SXNG_Response(_status_code :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_, _*_ , _headers :Headers|[Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]|[Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")]|[Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]]|[Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple "\(in Python v3.14\)")[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)"),[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")]]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _content :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")|[Iterable](https://docs.python.org/3/library/typing.html#typing.Iterable "\(in Python v3.14\)")[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")]|[AsyncIterable](https://docs.python.org/3/library/typing.html#typing.AsyncIterable "\(in Python v3.14\)")[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _text :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _html :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _json :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")=None_, _stream :SyncByteStream|AsyncByteStream|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _request :Request|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _extensions :[Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _history :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[Response]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _default_encoding :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")[[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")],[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]='utf-8'_) 
    
SearXNG extends the class `httpx.Response` with properties from _this_ class (type cast of `httpx.Response`).
```
response = httpx.get("https://example.org")
response = typing.cast(SXNG_Response, response)
if response.ok:
   ...
query_was = search_params["query"]

```
