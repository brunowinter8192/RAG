<!-- source: https://docs.searxng.org/dev/engines/online/annas_archive.html -->

# Anna’s Archive
[Anna’s Archive](https://annas-archive.gl/) is a free non-profit online shadow library metasearch engine providing access to a variety of book resources (also via IPFS), created by a team of anonymous archivists ([AnnaArchivist](https://software.annas-archive.gl/AnnaArchivist/annas-archive)).
## Configuration
The engine has the following additional settings:
With this options a SearXNG maintainer is able to configure **additional** engines for specific searches in Anna’s Archive. For example a engine to search for _newest_ articles and journals (PDF) / by shortcut `!aaa <search-term>`.
```
- name: annas articles
  engine: annas_archive
  categories = ["general", "articles"]
  shortcut: aaa
  aa_content: "magazine"
  aa_ext: "pdf"
  aa_sort: "newest"

```

## Implementations
**engines.annas_archive.base_url** = `[]`
List of Anna’s archive domains or a single domain (as string). 

**engines.annas_archive.aa_content** = `''`
Anan’s search form field **Content** / possible values:
```
book_fiction, book_unknown, book_nonfiction,
book_comic, magazine, standards_document

```

To not filter use an empty string (default). 

**engines.annas_archive.aa_sort** = `''`
Sort Anna’s results, possible values:
```
newest, oldest, largest, smallest, newest_added, oldest_added, random

```

To sort by _most relevant_ use an empty string (default). 

**engines.annas_archive.aa_ext** = `''`
Filter Anna’s results by a file ending. Common filters for example are `pdf` and `epub`.
Note
Anna’s Archive is a beta release: Filter results by file extension does not really work on Anna’s Archive. 

searx.engines.annas_archive.setup(__engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Check of engine’s settings. 

searx.engines.annas_archive.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Fetch languages and other search arguments from Anna’s search form.
