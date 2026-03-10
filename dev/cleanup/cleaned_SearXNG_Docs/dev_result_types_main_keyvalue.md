<!-- source: https://docs.searxng.org/dev/result_types/main/keyvalue.html -->

# Key-Value Results
Typification of the _keyvalue_ results. Results of this type are rendered in the [keyvalue.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/keyvalue.html) template.
* * * 

_class_ searx.result_types.keyvalue.KeyValue(_title: str = '', content: str = '', img_src: str = '', iframe_src: str = '', audio_src: str = '', thumbnail: str = '', publishedDate: ~datetime.datetime | None = None, pubdate: str = '', length: ~datetime.timedelta | None = None, views: str = '', author: str = '', metadata: str = '', priority: ~typing.Literal['', 'high', 'low'] = '', engines: set[str] = <factory>, open_group: bool = False, close_group: bool = False, positions: list[int] = <factory>, score: float = 0, category: str = '', *, template: str = 'keyvalue.html', url: str | None = None, engine: str | None = '', parsed_url: ~urllib.parse.ParseResult | None = None, kvmap: dict[str, ~typing.Any] | ~collections.OrderedDict[str, ~typing.Any], caption: str = '', key_title: str = '', value_title: str = ''_) 
    
Bases: [`MainResult`](https://docs.searxng.org/dev/result_types/main/mainresult.html#searx.result_types._base.MainResult "searx.result_types._base.MainResult")
Simple table view which maps _key_ names (first col) to _values_ (second col). 

kvmap _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]|[OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_ 
    
Dictionary with keys and values. To sort keys, use `OrderedDict`. 

caption _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Optional caption for this result. 

key_title _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Optional title for the _key column_. 

value_title _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Optional title for the _value column_.
