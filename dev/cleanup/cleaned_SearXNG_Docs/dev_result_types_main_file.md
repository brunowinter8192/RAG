<!-- source: https://docs.searxng.org/dev/result_types/main/file.html -->

# File Results
Typification of the _file_ results. Results of this type are rendered in the [file.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/file.html) template.
* * * 

_final class_searx.result_types.file.File(_title: str = ''_, _content: str = ''_, _img_src: str = ''_, _iframe_src: str = ''_, _audio_src: str = ''_, _thumbnail: str = ''_, _publishedDate: ~datetime.datetime | None = None_, _pubdate: str = ''_, _length: ~datetime.timedelta | None = None_, _views: str = ''_, _metadata: str = ''_, _priority: ~typing.Literal[''_, _'high'_ , _'low'] = ''_, _engines: set[str] = <factory>_, _open_group: bool = False_, _close_group: bool = False_, _positions: list[int] = <factory>_, _score: float = 0_, _category: str = ''_, _*_ , _template: str = 'file.html'_, _author: str = ''_, _url: str | None = None_, _engine: str | None = ''_, _parsed_url: ~urllib.parse.ParseResult | None = None_, _filename: str = ''_, _size: str = ''_, _time: str = ''_, _mimetype: str = ''_, _abstract: str = ''_, _embedded: str = ''_, _mtype: str = ''_, _subtype: str = ''_) 
    
Bases: [`MainResult`](https://docs.searxng.org/dev/result_types/main/mainresult.html#searx.result_types._base.MainResult "searx.result_types._base.MainResult")
Class for results of type _file_ 

filename _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the file. 

size _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Size of bytes in human readable notation (`MB` for 1024 * 1024 Bytes file size.) 

time _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Indication of a time, such as the date of the last modification or the date of creation. This is a simple string, the _date_ of which can be freely chosen according to the context. 

mimetype _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Mimetype/Subtype of the file. For `audio` and `video`, a URL can be passed in the [`File.embedded`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File.embedded "searx.result_types.file.File.embedded") field to embed the referenced media in the result. If no value is specified, the MIME type is determined from `self.filename` or, alternatively, from `self.embedded` (if either of the two values is set). 

abstract _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Abstract of the file. 

embedded _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of an embedded media type (audio or video) / is collapsible. 

mtype _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Used for displaying [`File.embedded`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File.embedded "searx.result_types.file.File.embedded"). Its value is automatically populated from the base type of [`File.mimetype`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File.mimetype "searx.result_types.file.File.mimetype"), and can be explicitly set to enforce e.g. `audio` or `video` when mimetype is something like “application/ogg” but its know the content is for example a video. 

subtype _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Used for displaying [`File.embedded`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File.embedded "searx.result_types.file.File.embedded"). Its value is automatically populated from the subtype type of [`File.mimetype`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File.mimetype "searx.result_types.file.File.mimetype"), and can be explicitly set to enforce a subtype for the [`File.embedded`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File.embedded "searx.result_types.file.File.embedded") element.
