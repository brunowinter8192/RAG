<!-- source: https://docs.searxng.org/dev/engines/online/archlinux.html -->

# Arch Linux
  * [Arch Linux Wiki](https://docs.searxng.org/dev/engines/online/archlinux.html#arch-linux-wiki)

## Arch Linux Wiki
This implementation does not use a official API: Mediawiki provides API, but Arch Wiki blocks access to it. 

searx.engines.archlinux.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch languages from Archlinux-Wiki. The location of the Wiki address of a language is mapped in a [`custom field`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits.custom "searx.enginelib.traits.EngineTraits.custom") (`wiki_netloc`). Depending on the location, the `title` argument in the request is translated.
```
"custom": {
  "wiki_netloc": {
    "de": "wiki.archlinux.de",
     # ...
    "zh": "wiki.archlinuxcn.org"
  }
  "title": {
    "de": "Spezial:Suche",
     # ...
    "zh": "Special:搜索"
  },
},

```
