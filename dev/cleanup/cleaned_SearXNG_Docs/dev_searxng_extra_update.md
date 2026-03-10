<!-- source: https://docs.searxng.org/dev/searxng_extra/update.html -->

#  `searxng_extra/update/`

Scripts to update static data in [git://searx/data/](https://github.com/searxng/searxng/blob/master/searx/data/)
##  `update_ahmia_blacklist.py`

This script saves [Ahmia’s blacklist](https://ahmia.fi/blacklist/) for onion sites.
Output file: [git://searx/data/ahmia_blacklist.txt](https://github.com/searxng/searxng/blob/master/searx/data/ahmia_blacklist.txt) ([CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml)).
##  `update_currencies.py`

Fetch currencies from [git://searx/engines/wikidata.py](https://github.com/searxng/searxng/blob/master/searx/engines/wikidata.py) engine.
Output file: [git://searx/data/currencies.json](https://github.com/searxng/searxng/blob/master/searx/data/currencies.json) ([CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml)).
##  `update_engine_descriptions.py`

Fetch website description from websites and from [git://searx/engines/wikidata.py](https://github.com/searxng/searxng/blob/master/searx/engines/wikidata.py) engine.
Output file: [git://searx/data/engine_descriptions.json](https://github.com/searxng/searxng/blob/master/searx/data/engine_descriptions.json). 

searxng_extra.update.update_engine_descriptions.get_output() 
    
From descriptions[engine][language] = [description, source] To
  * output[language][engine] = description_and_source
  * 

description_and_source can be:
    
    * [description, source]
    * description (if source = “wikipedia”)
    * [f”engine:lang”, “ref”] (reference to another existing description)

##  `update_external_bangs.py`

Update [git://searx/data/external_bangs.json](https://github.com/searxng/searxng/blob/master/searx/data/external_bangs.json) using the duckduckgo bangs from [`BANGS_URL`](https://docs.searxng.org/dev/searxng_extra/update.html#searxng_extra.update.update_external_bangs.BANGS_URL "searxng_extra.update.update_external_bangs.BANGS_URL").
  * [CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml)

searxng_extra.update.update_external_bangs.BANGS_URL _= 'https://duckduckgo.com/bang.js'_ 
    
JSON file which contains the bangs. 

searxng_extra.update.update_external_bangs.merge_when_no_leaf(_node_) 
    
Minimize the number of nodes
`A -> B -> C`
  * `B` is child of `A`
  * `C` is child of `B`

If there are no `C` equals to `<LEAF_KEY>`, then each `C` are merged into `A`. For example (5 nodes):
```
d -> d -> g -> <LEAF_KEY> (ddg)
  -> i -> g -> <LEAF_KEY> (dig)

```

becomes (3 nodes):
```
d -> dg -> <LEAF_KEY>
  -> ig -> <LEAF_KEY>

```

##  `update_firefox_version.py`

Fetch firefox useragent signatures
Output file: [git://searx/data/useragents.json](https://github.com/searxng/searxng/blob/master/searx/data/useragents.json) ([CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml)).
##  `update_engine_traits.py`

Update [`searx.enginelib.traits.EngineTraitsMap`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap "searx.enginelib.traits.EngineTraitsMap") and [git://searx/languages.py](https://github.com/searxng/searxng/blob/master/searx/languages.py) 

[`searx.enginelib.traits.EngineTraitsMap.ENGINE_TRAITS_FILE`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap.ENGINE_TRAITS_FILE "searx.enginelib.traits.EngineTraitsMap.ENGINE_TRAITS_FILE"):
    
Persistence of engines traits, fetched from the engines. 

[git://searx/languages.py](https://github.com/searxng/searxng/blob/master/searx/languages.py)
    
Is generated from intersecting each engine’s supported traits.
The script [git://searxng_extra/update/update_engine_traits.py](https://github.com/searxng/searxng/blob/master/searxng_extra/update/update_engine_traits.py) is called in the [CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml) 

searxng_extra.update.update_engine_traits.fetch_traits_map() 
    
Fetches supported languages for each engine and writes json file with those. 

searxng_extra.update.update_engine_traits.filter_locales(_traits_map :[EngineTraitsMap](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap "searx.enginelib.traits.EngineTraitsMap")_) 
    
Filter language & region tags by a threshold. 

_class_ searxng_extra.update.update_engine_traits.UnicodeEscape 
    
Escape unicode string in [`pprint.pformat`](https://docs.python.org/3/library/pprint.html#pprint.pformat "\(in Python v3.14\)") 

searxng_extra.update.update_engine_traits.get_unicode_flag(_locale :[Locale](https://babel.readthedocs.io/en/latest/api/core.html#babel.core.Locale "\(in Babel v2.2\)")_) 
    
Determine a unicode flag (emoji) that fits to the `locale`
##  `update_osm_keys_tags.py`

Fetch OSM keys and tags.
To get the i18n names, the scripts uses [Wikidata Query Service](https://query.wikidata.org/) instead of for example [OSM tags API](https://taginfo.openstreetmap.org/taginfo/apidoc) (side note: the actual change log from [map.atownsend.org.uk](https://map.atownsend.org.uk/maps/map/changelog.html) might be useful to normalize OSM tags).
Output file: [git://searx/data/osm_keys_tags](https://github.com/searxng/searxng/blob/master/searx/data/osm_keys_tags) ([CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml)). 

`SPARQL_TAGS_REQUEST` :
    
Wikidata SPARQL query that returns _type-categories_ and _types_. The returned tag is `Tag:{category}={type}` (see `get_tags()`). Example:
  * <https://taginfo.openstreetmap.org/tags/building=house#overview>
  * <https://wiki.openstreetmap.org/wiki/Tag:building%3Dhouse> at the bottom of the infobox (right side), there is a link to wikidata: <https://www.wikidata.org/wiki/Q3947> see property “OpenStreetMap tag or key” (P1282)
  * <https://wiki.openstreetmap.org/wiki/Tag%3Abuilding%3Dbungalow> <https://www.wikidata.org/wiki/Q850107>

`SPARQL_KEYS_REQUEST` :
    
Wikidata SPARQL query that returns _keys_. Example with “payment”:
  * <https://wiki.openstreetmap.org/wiki/Key%3Apayment> at the bottom of infobox (right side), there is a link to wikidata: <https://www.wikidata.org/wiki/Q1148747> link made using the “OpenStreetMap tag or key” property (P1282) to be confirm: there is a one wiki page per key ?
  * <https://taginfo.openstreetmap.org/keys/payment#values>
  * <https://taginfo.openstreetmap.org/keys/payment:cash#values>

`rdfs:label` get all the labels without language selection (as opposed to SERVICE `wikibase:label`).
##  `update_pygments.py`

Update pygments style
Call this script after each upgrade of pygments 

_class_ searxng_extra.update.update_pygments.Formatter(_** options_) 

##  `update_locales.py`

Update locale names in [git://searx/data/locales.json](https://github.com/searxng/searxng/blob/master/searx/data/locales.json) used by [Locales](https://docs.searxng.org/src/searx.locales.html#searx-locales)
searxng_extra.update.update_locales.get_locale_descr(_locale :[Locale](https://babel.readthedocs.io/en/latest/api/core.html#babel.core.Locale "\(in Babel v2.2\)")_, _tr_locale_) 
    
Get locale name e.g. ‘Français - fr’ or ‘Português (Brasil) - pt-BR’ 

Parameters: 
    
  * **locale** – instance of `Locale`
  * **tr_locale** – name e.g. ‘fr’ or ‘pt_BR’ (delimiter is _underscore_)

##  `update_wikidata_units.py`

Fetch units from [git://searx/engines/wikidata.py](https://github.com/searxng/searxng/blob/master/searx/engines/wikidata.py) engine.
Output file: [git://searx/data/wikidata_units.json](https://github.com/searxng/searxng/blob/master/searx/data/wikidata_units.json) ([CI Update data …](https://github.com/searxng/searxng/blob/master/.github/workflows/data-update.yml)).
