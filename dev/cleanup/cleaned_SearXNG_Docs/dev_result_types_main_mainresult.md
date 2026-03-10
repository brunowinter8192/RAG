<!-- source: https://docs.searxng.org/dev/result_types/main/mainresult.html -->

### Navigation
  * [index](https://docs.searxng.org/genindex.html "General Index")
  * [modules](https://docs.searxng.org/py-modindex.html "Python Module Index") |
  * [next](https://docs.searxng.org/dev/result_types/main/keyvalue.html "Key-Value Results") |
  * [previous](https://docs.searxng.org/dev/result_types/main_result.html "Main Search Results") |
  * [SearXNG Documentation (2026.3.9+d4954a064)](https://docs.searxng.org/index.html) »
  * [Developer documentation](https://docs.searxng.org/dev/index.html) »
  * [Result Types](https://docs.searxng.org/dev/result_types/index.html) »
  * [Main Search Results](https://docs.searxng.org/dev/result_types/main_result.html) »
  * [<no title>](https://docs.searxng.org/dev/result_types/main/mainresult.html)

_class_ searx.result_types._base.MainResult(_template: str = 'default.html'_, _title: str = ''_, _content: str = ''_, _img_src: str = ''_, _iframe_src: str = ''_, _audio_src: str = ''_, _thumbnail: str = ''_, _publishedDate: ~datetime.datetime | None = None_, _pubdate: str = ''_, _length: ~datetime.timedelta | None = None_, _views: str = ''_, _author: str = ''_, _metadata: str = ''_, _priority: ~typing.Literal[''_, _'high'_ , _'low'] = ''_, _engines: set[str] = <factory>_, _open_group: bool = False_, _close_group: bool = False_, _positions: list[int] = <factory>_, _score: float = 0_, _category: str = ''_, _*_ , _url: str | None = None_, _engine: str | None = ''_, _parsed_url: ~urllib.parse.ParseResult | None = None_) 
    
Base class of all result types displayed in [area main results](https://docs.searxng.org/dev/result_types/index.html#area-main-results). 

template _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the template used to render the result.
By default [result_templates/default.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/default.html) is used. 

title _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Link title of the result item. 

content _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Extract or description of the result item 

img_src _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of a image that is displayed in the result item. 

iframe_src _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of an embedded `<iframe>` / the frame is collapsible. 

audio_src _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of an embedded `<audio controls>`. 

thumbnail _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of a thumbnail that is displayed in the result item. 

publishedDate _:[ datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
The date on which the object was published. 

pubdate _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
String representation of [`MainResult.publishedDate`](https://docs.searxng.org/dev/result_types/main/mainresult.html#searx.result_types._base.MainResult.publishedDate "searx.result_types._base.MainResult.publishedDate")
Deprecated: it is still partially used in the templates, but will one day be completely eliminated. 

length _:[ timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Playing duration in seconds. 

views _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
View count in humanized number format. 

author _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Author of the title. 

metadata _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Miscellaneous metadata. 

priority _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['','high','low']_ 
    
The priority can be set via [Hostnames](https://docs.searxng.org/dev/plugins/hostnames.html#hostnames-plugin), for example. 

engines _:[ set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
In a merged results list, the names of the engines that found this result are listed in this field. 

normalize_result_fields() 
    
Normalize fields `url` and `parse_sql`.
  * If field `url` is set and field `parse_url` is unset, init `parse_url` from field `url`. The `url` field is initialized with the resulting value in `parse_url`, if `url` and `parse_url` are not equal.
