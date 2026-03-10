<!-- source: https://docs.searxng.org/src/searx.utils.html -->

# Utility functions for the engines
Utility functions for the engines 

**utils.XPathSpecType** = `str | lxml.etree.XPath`
Type alias used by [`searx.utils.get_xpath`](https://docs.searxng.org/src/searx.utils.html#searx.utils.get_xpath "searx.utils.get_xpath"), [`searx.utils.eval_xpath`](https://docs.searxng.org/src/searx.utils.html#searx.utils.eval_xpath "searx.utils.eval_xpath") and other XPath selectors. 

searx.utils.searxng_useragent() → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Return the SearXNG User Agent 

searx.utils.gen_useragent(_os_string :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Return a random browser User Agent
See searx/data/useragents.json 

searx.utils.gen_gsa_useragent() → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Return a random GSA User Agent suitable for Google
See searx/data/gsa_useragents.txt 

_class_ searx.utils.HTMLTextExtractor 
    
Internal class to extract text from HTML 

searx.utils.html_to_text(_html_str :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Extract text from a HTML string 

Args:
    
  * html_str (str): string HTML

Returns:
    
  * str: extracted text

Examples:
    
```
>>> html_to_text('Example <span id="42">#2</span>')
'Example #2'

```

```
>>> html_to_text('<style>.span { color: red; }</style><span>Example</span>')
'Example'

```

```
>>> html_to_text(r'regexp: (?&lt;![a-zA-Z]')
'regexp: (?<![a-zA-Z]'

```

```
>>> html_to_text(r'<p><b>Lorem ipsum </i>dolor sit amet</p>')
'Lorem ipsum </i>dolor sit amet</p>'

```

```
>>> html_to_text(r'&#x3e &#x3c &#97')
'> < a'

```

searx.utils.markdown_to_text(_markdown_str :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Extract text from a Markdown string 

Args:
    
  * markdown_str (str): string Markdown

Returns:
    
  * str: extracted text

Examples:
    
```
>>> markdown_to_text('[example](https://example.com)')
'example'

```

```
>>> markdown_to_text('## Headline')
'Headline'

```

searx.utils.extract_text(_xpath_results :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")]|[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[Number](https://docs.python.org/3/library/numbers.html#numbers.Number "\(in Python v3.14\)")|[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _allow_none :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Extract text from a lxml result
  * If `xpath_results` is a list of `ElementType` objects, extract the text from each result and concatenate the list in a string.
  * If `xpath_results` is a `ElementType` object, extract all the text node from it ( [`lxml.html.tostring`](https://lxml.de/apidoc/lxml.html.html#lxml.html.tostring "\(in lxml v6.0.0\)"), `method="text"` )
  * If `xpath_results` is of type [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") or `Number`, [`bool`](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") the string value is returned.
  * If `xpath_results` is of type `None` a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") is raised, except `allow_none` is `True` where `None` is returned.

searx.utils.normalize_url(_url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _base_url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Normalize URL: add protocol, join URL with base_url, add trailing slash if there is no path 

Args:
    
  * url (str): Relative URL
  * base_url (str): Base URL, it must be an absolute URL.

Example:
    
```
>>> normalize_url('https://example.com', 'http://example.com/')
'https://example.com/'
>>> normalize_url('//example.com', 'http://example.com/')
'http://example.com/'
>>> normalize_url('//example.com', 'https://example.com/')
'https://example.com/'
>>> normalize_url('/path?a=1', 'https://example.com')
'https://example.com/path?a=1'
>>> normalize_url('', 'https://example.com')
'https://example.com/'
>>> normalize_url('/test', '/path')
raise ValueError

```

Raises:
    
  * lxml.etree.ParserError

Returns:
    
  * str: normalized URL

searx.utils.extract_url(_xpath_results :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")]|[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[Number](https://docs.python.org/3/library/numbers.html#numbers.Number "\(in Python v3.14\)")|[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _base_url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Extract and normalize URL from lxml Element 

Example:
    
```
>>> def f(s, search_url):
>>>    return searx.utils.extract_url(html.fromstring(s), search_url)
>>> f('<span id="42">https://example.com</span>', 'http://example.com/')
'https://example.com/'
>>> f('https://example.com', 'http://example.com/')
'https://example.com/'
>>> f('//example.com', 'http://example.com/')
'http://example.com/'
>>> f('//example.com', 'https://example.com/')
'https://example.com/'
>>> f('/path?a=1', 'https://example.com')
'https://example.com/path?a=1'
>>> f('', 'https://example.com')
raise lxml.etree.ParserError
>>> searx.utils.extract_url([], 'https://example.com')
raise ValueError

```

Raises:
    
  * ValueError
  * lxml.etree.ParserError

Returns:
    
  * str: normalized URL

searx.utils.dict_subset(_dictionary :[MutableMapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_, _properties :[set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) → [MutableMapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] 
    
Extract a subset of a dict 

Examples:
    
```
>>> dict_subset({'A': 'a', 'B': 'b', 'C': 'c'}, ['A', 'C'])
{'A': 'a', 'C': 'c'}
>>> >> dict_subset({'A': 'a', 'B': 'b', 'C': 'c'}, ['A', 'D'])
{'A': 'a'}

```

searx.utils.humanize_bytes(_size :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _precision :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=2_) 
    
Determine the _human readable_ value of bytes on 1024 base (1KB=1024B). 

searx.utils.humanize_number(_size :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _precision :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=0_) 
    
Determine the _human readable_ value of a decimal number. 

searx.utils.convert_str_to_int(_number_str :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") 
    
Convert number_str to int or 0 if number_str is not a number. 

searx.utils.extr(_txt :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _begin :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _end :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _default :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")=''_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Extract the string between `begin` and `end` from `txt` 

Parameters: 
    
  * **txt** – String to search in
  * **begin** – First string to be searched for
  * **end** – Second string to be searched for after `begin`
  * **default** – Default value if one of `begin` or `end` is not found. Defaults to an empty string.

Returns: 
    
The string between the two search-strings `begin` and `end`. If at least one of `begin` or `end` is not found, the value of `default` is returned. 

Examples:
    
```
>>> extr("abcde", "a", "e")
"bcd"
>>> extr("abcde", "a", "z", deafult="nothing")
"nothing"

```

searx.utils.int_or_zero(_num :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") 
    
Convert num to int or 0. num can be either a str or a list. If num is a list, the first element is converted to int (or return 0 if the list is empty). If num is a str, see convert_str_to_int 

searx.utils.to_string(_obj :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Convert obj to its string representation. 

searx.utils.ecma_unescape(_string :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Python implementation of the unescape javascript function
<https://www.ecma-international.org/ecma-262/6.0/#sec-unescape-string> <https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/unescape> 

Examples:
    
```
>>> ecma_unescape('%u5409')
'吉'
>>> ecma_unescape('%20')
' '
>>> ecma_unescape('%F3')
'ó'

```

searx.utils.remove_pua_from_str(_string :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Removes unicode’s “PRIVATE USE CHARACTER”s ([PUA](https://en.wikipedia.org/wiki/Private_Use_Areas)) from a string. 

searx.utils.get_engine_from_settings(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]] 
    
Return engine configuration from settings.yml of a given engine name 

searx.utils.get_xpath(_xpath_spec :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[XPath](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)")_) → [XPath](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)") 
    
Return cached compiled [`lxml.etree.XPath`](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)") object. 

`TypeError`:
    
Raised when `xpath_spec` is neither a [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") nor a [`lxml.etree.XPath`](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)"). 

`SearxXPathSyntaxException`:
    
Raised when there is a syntax error in the _XPath_ selector (`str`). 

searx.utils.eval_xpath(_element :[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")_, _xpath_spec :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[XPath](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)")_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Equivalent of `element.xpath(xpath_str)` but compile `xpath_str` into a [`lxml.etree.XPath`](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)") object once for all. The return value of `xpath(..)` is complex, read [XPath return values](https://lxml.de/xpathxslt.html#xpath-return-values) for more details. 

`TypeError`:
    
Raised when `xpath_spec` is neither a [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") nor a [`lxml.etree.XPath`](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)"). 

`SearxXPathSyntaxException`:
    
Raised when there is a syntax error in the _XPath_ selector (`str`). 

`SearxEngineXPathException:`
    
Raised when the XPath can’t be evaluated (masked `lxml.etree..XPathError`). 

searx.utils.eval_xpath_list(_element :[ElementBase](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase "\(in lxml v6.0.0\)")|[_Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element "\(in lxml v6.0.0\)")_, _xpath_spec :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[XPath](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.XPath "\(in lxml v6.0.0\)")_, _min_len :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] 
    
Same as [`searx.utils.eval_xpath`](https://docs.searxng.org/src/searx.utils.html#searx.utils.eval_xpath "searx.utils.eval_xpath"), but additionally ensures the return value is a [`list`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)"). The minimum length of the list is also checked (if `min_len` is set). 

searx.utils.eval_xpath_getindex(_element: ~lxml.etree.ElementBase | ~lxml.etree._Element_, _xpath_spec: str | ~lxml.etree.XPath_, _index: int_, _default: ~typing.Any = <searx.utils._NotSetClass object>_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Same as [`searx.utils.eval_xpath_list`](https://docs.searxng.org/src/searx.utils.html#searx.utils.eval_xpath_list "searx.utils.eval_xpath_list"), but returns item on position `index` from the list (index starts with `0`).
The exceptions known from [`searx.utils.eval_xpath`](https://docs.searxng.org/src/searx.utils.html#searx.utils.eval_xpath "searx.utils.eval_xpath") are thrown. If a default is specified, this is returned if an element at position `index` could not be determined. 

searx.utils.get_embeded_stream_url(_url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Converts a standard video URL into its embed format. Supported services include Youtube, Facebook, Instagram, TikTok, Dailymotion, and Bilibili. 

searx.utils.js_obj_str_to_python(_js_obj_str :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Convert a javascript variable into JSON and then load the value
It does not deal with all cases, but it is good enough for now. chompjs has a better implementation. 

searx.utils.parse_duration_string(_duration_str :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Parse a time string in format MM:SS or HH:MM:SS and convert it to a timedelta object.
Returns None if the provided string doesn’t match any of the formats.
