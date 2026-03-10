<!-- source: https://docs.searxng.org/dev/result_types/main/paper.html -->

# Paper Results
Typification of the _paper_ results.
Results of this type are rendered in the [paper.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/paper.html) template.
Related topics:
  * [BibTeX field types](https://en.wikipedia.org/wiki/BibTeX#Field_types)
  * [BibTeX format](https://www.bibtex.com/g/bibtex-format/)

* * * 

_final class_searx.result_types.paper.Paper(_title: str = ''_, _img_src: str = ''_, _iframe_src: str = ''_, _audio_src: str = ''_, _thumbnail: str = ''_, _publishedDate: ~datetime.datetime | None = None_, _pubdate: str = ''_, _length: ~datetime.timedelta | None = None_, _views: str = ''_, _author: str = ''_, _metadata: str = ''_, _priority: ~typing.Literal[''_, _'high'_ , _'low'] = ''_, _engines: set[str] = <factory>_, _open_group: bool = False_, _close_group: bool = False_, _positions: list[int] = <factory>_, _score: float = 0_, _category: str = ''_, _*_ , _template: str = 'paper.html'_, _content: str = ''_, _url: str | None = None_, _engine: str | None = ''_, _parsed_url: ~urllib.parse.ParseResult | None = None_, _date_of_publication: ~searx.weather.DateTime | None = None_, _comments: str = ''_, _tags: list[str] = <factory>_, _type: str = ''_, _authors: list[str] | set[str] = <factory>_, _editor: str = ''_, _publisher: str = ''_, _journal: str = ''_, _volume: str | int = ''_, _pages: str = ''_, _number: str = ''_, _doi: str = ''_, _issn: list[str] = <factory>_, _isbn: list[str] = <factory>_, _pdf_url: str = ''_, _html_url: str = ''_) 
    
Bases: [`MainResult`](https://docs.searxng.org/dev/result_types/main/mainresult.html#searx.result_types._base.MainResult "searx.result_types._base.MainResult")
Result type suitable for displaying scientific papers and other documents. 

date_of_publication _:[ DateTime](https://docs.searxng.org/src/searx.weather.html#searx.weather.DateTime "searx.weather.DateTime")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Date the document was published. 

comments _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Free text display in italic below the content. 

tags _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Free tag list. 

type _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Short description of medium type, e.g. _book_ , _pdf_ or _html_ … 

authors _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]|[set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of authors of the work (authors with a “s” suffix, the “author” is in the `MainResult.author`). 

editor _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Editor of the book/paper. 

publisher _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the publisher. 

journal _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the journal or magazine the article was published in. 

volume _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Volume number. 

pages _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Page range where the article is. 

number _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Number of the report or the issue number for a journal article. 

doi _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
DOI number (like `10.1038/d41586-018-07848-2`). 

issn _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of ISSN numbers like `1476-4687` 

isbn _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of ISBN numbers like `9780201896831` 

pdf_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL to the full article, the PDF version 

html_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL to full article, HTML version
