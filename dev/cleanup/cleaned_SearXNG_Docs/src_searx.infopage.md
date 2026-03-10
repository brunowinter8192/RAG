<!-- source: https://docs.searxng.org/src/searx.infopage.html -->

# Online `/info`
Render SearXNG instance documentation.
Usage in a Flask app route:
```
from searx import infopage
from searx.extended_types import sxng_request

_INFO_PAGES = infopage.InfoPageSet(infopage.MistletoePage)

@app.route('/info/<pagename>', methods=['GET'])
def info(pagename):

    locale = sxng_request.preferences.get_value('locale')
    page = _INFO_PAGES.get_page(pagename, locale)

```

_class_ searx.infopage.InfoPage(_fname :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
A page of the [`online documentation`](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPageSet "searx.infopage.InfoPageSet"). 

_property_ raw_content 
    
Raw content of the page (without any jinja rendering) 

_property_ content 
    
Content of the page (rendered in a Jinja context) 

_property_ title 
    
Title of the content (without any markup) 

_property_ html _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Render Markdown ([CommonMark](https://commonmark.org/)) to HTML by using [markdown-it-py](https://github.com/executablebooks/markdown-it-py). 

get_ctx() → [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Jinja context to render [`InfoPage.content`](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPage.content "searx.infopage.InfoPage.content") 

_class_ searx.infopage.InfoPageSet(_page_class :[type](https://docs.python.org/3/library/functions.html#type "\(in Python v3.14\)")[[InfoPage](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPage "searx.infopage.InfoPage")]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _info_folder :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
Cached rendering of the online documentation a SearXNG instance has. 

Parameters: 
    
  * **page_class** ([`InfoPage`](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPage "searx.infopage.InfoPage")) – render online documentation by [`InfoPage`](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPage "searx.infopage.InfoPage") parser.
  * **info_folder** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – information directory

folder _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
location of the Markdown files 

locale_default _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
default language 

locales _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
list of supported languages (aka locales) 

toc _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
list of articles in the online documentation 

get_page(_pagename :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _locale :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
Return `pagename` instance of [`InfoPage`](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPage "searx.infopage.InfoPage") 

Parameters: 
    
  * **pagename** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – name of the page, a value from [`InfoPageSet.toc`](https://docs.searxng.org/src/searx.infopage.html#searx.infopage.InfoPageSet.toc "searx.infopage.InfoPageSet.toc")
  * **locale** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – language of the page, e.g. `en`, `zh_Hans_CN` (default: `InfoPageSet.i18n_origin`)

iter_pages(_locale :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _fallback_to_default :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Iterate over all pages of the TOC
