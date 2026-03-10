<!-- source: https://docs.searxng.org/dev/engines/online/zlibrary.html -->

# Z-Library
Contents
[Z-Library](https://zlibrary-global.se/) (abbreviated as z-lib, formerly BookFinder) is a shadow library project for file-sharing access to scholarly journal articles, academic texts and general-interest books. It began as a mirror of Library Genesis, from which most of its books originate.
## Configuration
The engine has the following additional settings:
With this options a SearXNG maintainer is able to configure **additional** engines for specific searches in Z-Library. For example a engine to search only for EPUB from 2010 to 2020.
```
- name: z-library 2010s epub
  engine: zlibrary
  shortcut: zlib2010s
  zlib_year_from: '2010'
  zlib_year_to: '2020'
  zlib_ext: 'EPUB'

```

## Implementations
**engines.zlibrary.zlib_year_from** = `''`
Filter z-library’s results by year from. E.g ‘2010’. 

**engines.zlibrary.zlib_year_to** = `''`
Filter z-library’s results by year to. E.g. ‘2010’. 

**engines.zlibrary.zlib_ext** = `''`
Filter z-library’s results by a file ending. Common filters for example are `PDF` and `EPUB`. 

searx.engines.zlibrary.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Check of engine’s settings. 

searx.engines.zlibrary.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Fetch languages and other search arguments from zlibrary’s search form.
