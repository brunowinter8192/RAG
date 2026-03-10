<!-- source: https://docs.searxng.org/dev/result_types/base_result.html -->

# Result
Basic types for the typification of results.
  * [`Result`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result") base class
  * [`LegacyResult`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.LegacyResult "searx.result_types._base.LegacyResult") for internal use only

* * * 

_class_ searx.result_types._base.Result(_*_ , _url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _engine :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=''_, _parsed_url :[ParseResult](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
Base class of all result types [Result Types](https://docs.searxng.org/dev/result_types/index.html#result-types). 

url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
A link related to this _result_ 

engine _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Name of the engine _this_ result comes from. In case of _plugins_ a prefix `plugin:` is set, in case of _answerer_ prefix `answerer:` is set.
The field is optional and is initialized from the context if necessary. 

parsed_url _:[ ParseResult](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
[`urllib.parse.ParseResult`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult "\(in Python v3.14\)") of [`Result.url`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.url "searx.result_types._base.Result.url").
The field is optional and is initialized from the context if necessary. 

normalize_result_fields() 
    
Normalize fields `url` and `parse_sql`.
  * If field `url` is set and field `parse_url` is unset, init `parse_url` from field `url`. The `url` field is initialized with the resulting value in `parse_url`, if `url` and `parse_url` are not equal.

filter_urls(_filter_func :[Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable "\(in Python v3.14\)")[[[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")|[LegacyResult](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.LegacyResult "searx.result_types._base.LegacyResult"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")],[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")]_) 
    
A filter function is passed in the `filter_func` argument to filter and/or modify the URLs.
The filter function receives the [`result object`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result") as the first argument and the field name (`str`) in the second argument. In the third argument the URL string value is passed to the filter function.
The filter function is applied to all fields that contain a URL, in addition to the familiar `url` field, these include fields such as:
```
["url", "iframe_src", "audio_src", "img_src", "thumbnail_src", "thumbnail"]

```

and the `urls` list of items of the infobox.
For each field, the filter function is called and returns a bool or a string value:
  * `True`: leave URL in field unchanged
  * `False`: remove URL field from result (or remove entire result)
  * `str`: modified URL to be used instead

See [Filter URLs example](https://docs.searxng.org/dev/plugins/development.html#filter-urls-example). 

defaults_from(_other :[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")_) 
    
Fields not set in _self_ will be updated from the field values of the _other_. 

_class_ searx.result_types._base.LegacyResult(_* args:[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_, _** kwargs:[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_) 
    
A wrapper around a legacy result item. The SearXNG core uses this class for untyped dictionaries / to be downward compatible.
This class is needed until we have implemented an [`Result`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result") class for each result type and the old usages in the codebase have been fully migrated.
There is only one place where this class is used, in the `searx.results.ResultContainer`.
Attention
Do not use this class in your own implementations! 

filter_urls(_filter_func :[Callable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable "\(in Python v3.14\)")[[[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")|[LegacyResult](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.LegacyResult "searx.result_types._base.LegacyResult"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")],[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")]_) 
    
See [`Result.filter_urls`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.filter_urls "searx.result_types._base.Result.filter_urls")
