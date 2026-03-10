<!-- source: https://docs.searxng.org/dev/result_types/main/code.html -->

# Code Results
Typification of the _code_ results. Results of this type are rendered in the [code.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/code.html) template. For highlighting the code passages, [Pygments](https://pygments.org) is used.
* * * 

_final class_searx.result_types.code.Code(_title: str = ''_, _content: str = ''_, _img_src: str = ''_, _iframe_src: str = ''_, _audio_src: str = ''_, _thumbnail: str = ''_, _publishedDate: ~datetime.datetime | None = None_, _pubdate: str = ''_, _length: ~datetime.timedelta | None = None_, _views: str = ''_, _author: str = ''_, _metadata: str = ''_, _priority: ~typing.Literal[''_, _'high'_ , _'low'] = ''_, _engines: set[str] = <factory>_, _open_group: bool = False_, _close_group: bool = False_, _positions: list[int] = <factory>_, _score: float = 0_, _category: str = ''_, _*_ , _template: str = 'code.html'_, _url: str | None = None_, _engine: str | None = ''_, _parsed_url: ~urllib.parse.ParseResult | None = None_, _repository: str | None = None_, _codelines: list[tuple[int_, _str]] = <factory>_, _hl_lines: set[int] = <factory>_, _code_language: str = '<guess>'_, _filename: str | None = None_, _strip_new_lines: bool = True_, _strip_whitespace: bool = False_) 
    
Bases: [`MainResult`](https://docs.searxng.org/dev/result_types/main/mainresult.html#searx.result_types._base.MainResult "searx.result_types._base.MainResult")
Result type suitable for displaying code passages. 

repository _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
A link related to a repository related to the _result_. 

codelines _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]]_ 
    
A list of two digit tuples where the first item is the line number and the second item is the code line. 

hl_lines _:[ set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")]_ 
    
A list of line numbers to highlight. 

code_language _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Pygment’s short name of the lexer, e.g. `text` for the [`pygments.lexers.special.TextLexer`](https://pygments.org/docs/lexers/#pygments.lexers.special.TextLexer "\(in Pygments v2.19.2\)"). For a list of available languages consult: [Pygments languages](https://pygments.org/languages/). If the language is not in this list, a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") is raised.
The default is `<guess>` which has a special meaning;
  * If [`Code.filename`](https://docs.searxng.org/dev/result_types/main/code.html#searx.result_types.code.Code.filename "searx.result_types.code.Code.filename") is set, Pygment’s factory method [`pygments.lexers.guess_lexer_for_filename`](https://pygments.org/docs/api/#pygments.lexers.guess_lexer_for_filename "\(in Pygments v2.19.2\)") is used to determine the language of the `codelines`.
  * else Pygment’s [`pygments.lexers.guess_lexer`](https://pygments.org/docs/api/#pygments.lexers.guess_lexer "\(in Pygments v2.19.2\)") factory is used.

In case the language can’t be detected, the fallback is `text`. 

filename _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Optional file name, can help to `<guess>` the language of the code (in case of ambiguous short code examples). If `Code.title` is not set, its default is the filename. 

strip_new_lines _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Strip leading and trailing newlines for each returned fragment (default: `True`). Single file might return multiple code fragments. 

strip_whitespace _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Strip all leading and trailing whitespace for each returned fragment (default: `False`). Single file might return multiple code fragments. Enabling this might break code indentation. 

HTML(_** options_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Rendered HTML, additional options are accepted, for more details have a look at [HtmlFormatter](https://pygments.org/docs/formatters/#HtmlFormatter).
