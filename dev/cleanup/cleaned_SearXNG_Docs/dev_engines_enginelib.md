<!-- source: https://docs.searxng.org/dev/engines/enginelib.html -->

# Engine Library
Implementations of the framework for the SearXNG engines.
There is a command line for developer purposes and for deeper analysis. Here is an example in which the command line is called in the development environment:
```
$ ./manage pyenv.cmd bash --norc --noprofile
(py3) python -m searx.enginelib --help

```

Hint
The long term goal is to modularize all implementations of the engine framework here in this Python package. ToDo:
  * move implementations of the [SearXNG’s engines loader](https://docs.searxng.org/dev/engines/engines.html#searx-engines-loader) to a new module in the [`searx.enginelib`](https://docs.searxng.org/dev/engines/enginelib.html#module-searx.enginelib "searx.enginelib") namespace.

* * * 

_class_ searx.enginelib.EngineCache(_engine_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _expire :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
Persistent (SQLite) key/value cache that deletes its values again after `expire` seconds (default/max: [`MAXHOLD_TIME`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.MAXHOLD_TIME "searx.cache.ExpireCacheCfg.MAXHOLD_TIME")). This class is a wrapper around [`ENGINES_CACHE`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.ENGINES_CACHE "searx.enginelib.ENGINES_CACHE") ([`ExpireCacheSQLite`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheSQLite "searx.cache.ExpireCacheSQLite")).
In the [git://searx/engines/demo_offline.py](https://github.com/searxng/searxng/blob/master/searx/engines/demo_offline.py) engine you can find an exemplary implementation of such a cache other examples are implemented in:
  * [git://searx/engines/radio_browser.py](https://github.com/searxng/searxng/blob/master/searx/engines/radio_browser.py)
  * [git://searx/engines/soundcloud.py](https://github.com/searxng/searxng/blob/master/searx/engines/soundcloud.py)
  * [git://searx/engines/startpage.py](https://github.com/searxng/searxng/blob/master/searx/engines/startpage.py)

For introspection of the DB, jump into developer environment and run command to show cache state:
```
$ ./manage pyenv.cmd bash --norc --noprofile
(py3) python -m searx.enginelib cache state

cache tables and key/values
===========================
[demo_offline        ] 2025-04-22 11:32:50 count        --> (int) 4
[startpage           ] 2025-04-22 12:32:30 SC_CODE      --> (str) fSOBnhEMlDfE20
[duckduckgo          ] 2025-04-22 12:32:31 4dff493e.... --> (str) 4-128634958369380006627592672385352473325
[duckduckgo          ] 2025-04-22 12:40:06 3e2583e2.... --> (str) 4-263126175288871260472289814259666848451
[radio_browser       ] 2025-04-23 11:33:08 servers      --> (list) ['https://de2.api.radio-browser.info',  ...]
[soundcloud          ] 2025-04-29 11:40:06 guest_client_id --> (str) EjkRJG0BLNEZquRiPZYdNtJdyGtTuHdp
[wolframalpha        ] 2025-04-22 12:40:06 code         --> (str) 5aa79f86205ad26188e0e26e28fb7ae7
number of tables: 6
number of key/value pairs: 7

```

In the “cache tables and key/values” section, the table name (engine name) is at first position on the second there is the calculated expire date and on the third and fourth position the key/value is shown.
About duckduckgo: The _vqd coode_ of ddg depends on the query term and therefore the key is a hash value of the query term (to not to store the raw query term).
In the “properties of ENGINES_CACHE” section all properties of the SQLiteAppl / ExpireCache and their last modification date are shown:
```
properties of ENGINES_CACHE
===========================
[last modified: 2025-04-22 11:32:27] DB_SCHEMA           : 1
[last modified: 2025-04-22 11:32:27] LAST_MAINTENANCE    :
[last modified: 2025-04-22 11:32:27] crypt_hash          : ca612e3566fdfd7cf7efe...
[last modified: 2025-04-22 11:32:30] CACHE-TABLE--demo_offline: demo_offline
[last modified: 2025-04-22 11:32:30] CACHE-TABLE--startpage: startpage
[last modified: 2025-04-22 11:32:31] CACHE-TABLE--duckduckgo: duckduckgo
[last modified: 2025-04-22 11:33:08] CACHE-TABLE--radio_browser: radio_browser
[last modified: 2025-04-22 11:40:06] CACHE-TABLE--soundcloud: soundcloud
[last modified: 2025-04-22 11:40:06] CACHE-TABLE--wolframalpha: wolframalpha

```

These properties provide information about the state of the ExpireCache and control the behavior. For example, the maintenance intervals are controlled by the last modification date of the LAST_MAINTENANCE property and the hash value of the password can be used to detect whether the password has been changed (in this case the DB entries can no longer be decrypted and the entire cache must be discarded). 

_class_ searx.enginelib.Engine 
    
Class of engine instances build from YAML settings.
Further documentation see [General Engine Configuration](https://docs.searxng.org/dev/engines/engine_overview.html#general-engine-configuration).
Hint
This class is currently never initialized and only used for type hinting. 

engine_type _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Type of the engine ([Search processors](https://docs.searxng.org/src/searx.search.processors.html#searx-search-processors)) 

paging _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Engine supports multiple pages. 

max_page _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ _= 0_ 
    
If the engine supports paging, then this is the value for the last page that is still supported. `0` means unlimited numbers of pages. 

time_range_support _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Engine supports search time range. 

safesearch _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Engine supports SafeSearch 

language_support _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Engine supports languages (locales) search. 

language _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
For an engine, when there is `language: ...` in the YAML settings the engine does support only this one language:
```
- name: google french
  engine: google
  language: fr

```

region _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
For an engine, when there is `region: ...` in the YAML settings the engine does support only this one region:
```
.. code:: yaml

```

>   * name: google belgium engine: google region: fr-BE
> 

fetch_traits _: Callable[[[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits"),[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")],[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]_ 
    
Function to to fetch engine’s traits from origin. 

traits _:[ traits.EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_ 
    
Traits of the engine. 

categories _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Specifies to which [categories](https://docs.searxng.org/admin/settings/settings_engines.html#engine-categories) the engine should be added. 

name _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name that will be used across SearXNG to define this engine. In settings, on the result page .. 

engine _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the python file used to handle requests and responses to and from this search engine (file name from [git://searx/engines](https://github.com/searxng/searxng/blob/master/searx/engines) without `.py`). 

enable_http _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Enable HTTP (by default only HTTPS is enabled). 

shortcut _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Code used to execute bang requests (`!foo`) 

timeout _:[ float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ 
    
Specific timeout for search-engine. 

display_error_messages _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Display error messages on the web UI. 

proxies _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]]_ 
    
Set proxies for a specific engine (YAML):
```
proxies :
  http:  socks5://proxy:port
  https: socks5://proxy:port

```

disabled _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
To disable by default the engine, but not deleting it. It will allow the user to manually activate it in the settings. 

inactive _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Remove the engine from the settings (_disabled & removed_). 

about _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]]_ 
    
Additional fields describing the engine.
```
about:
   website: https://example.com
   wikidata_id: Q306656
   official_api_documentation: https://example.com/api-doc
   use_official_api: true
   require_api_key: true
   results: HTML

```

using_tor_proxy _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
Using tor proxy (`true`) or not (`false`) for this engine. 

send_accept_language_header _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ 
    
When this option is activated (default), the language (locale) that is selected by the user is used to build and send a `Accept-Language` header in the request to the origin search engine. 

tokens _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
A list of secret tokens to make this engine _private_ , more details see [Private Engines (tokens)](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines). 

weight _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Weighting of the results of this engine ([weight](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines)). 

setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Dynamic setup of the engine settings.
With this method, the engine’s setup is carried out. For example, to check or dynamically adapt the values handed over in the parameter `engine_settings`. The return value (True/False) indicates whether the setup was successful and the engine can be built or rejected.
The method is optional and is called synchronously as part of the initialization of the service and is therefore only suitable for simple (local) exams/changes at the engine setting. The [`Engine.init`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.init "searx.enginelib.Engine.init") method must be used for longer tasks in which values of a remote must be determined, for example. 

init(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Initialization of the engine.
The method is optional and asynchronous (in a thread). It is suitable, for example, for setting up a cache (for the engine) or for querying values (required by the engine) from a remote.
Whether the initialization was successful can be indicated by the return value `True` or even `False`.
  * If no return value is given from this init method (`None`), this is equivalent to `True`.
  * If an exception is thrown as part of the initialization, this is equivalent to `False`.

_abstractmethod_ search(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :OfflineParamTypes_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Search method of the `offline` engines 

_abstractmethod_ request(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :OnlineParamTypes_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Method to build the parameters for the request of an `online` engine. 

_abstractmethod_ response(_resp :[SXNG_Response](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Method to parse the response of an `online` engine. 

**enginelib.ENGINES_CACHE** = `<searx.cache.ExpireCacheSQLite object>`
Global [`searx.cache.ExpireCacheSQLite`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheSQLite "searx.cache.ExpireCacheSQLite") instance where the cached values from all engines are stored. The MAXHOLD_TIME is 7 days and the MAINTENANCE_PERIOD is set to two hours.
## Engine traits
Engine’s traits are fetched from the origin engines and stored in a JSON file in the _data folder_. Most often traits are languages and region codes and their mapping from SearXNG’s representation to the representation in the origin search engine. For new traits new properties can be added to the class [`EngineTraits`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits").
To load traits from the persistence [`EngineTraitsMap.from_data`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap.from_data "searx.enginelib.traits.EngineTraitsMap.from_data") can be used. 

_class_ searx.enginelib.traits.EngineTraitsEncoder(_*_ , _skipkeys =False_, _ensure_ascii =True_, _check_circular =True_, _allow_nan =True_, _sort_keys =False_, _indent =None_, _separators =None_, _default =None_) 
    
Encodes [`EngineTraits`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits") to a serializable object, see [`json.JSONEncoder`](https://docs.python.org/3/library/json.html#json.JSONEncoder "\(in Python v3.14\)"). 

default(_o :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Return dictionary of a [`EngineTraits`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits") object. 

_class_ searx.enginelib.traits.EngineTraits(_regions: dict[str_, _str] = <factory>_, _languages: dict[str_, _str] = <factory>_, _all_locale: str | None = None_, _data_type: ~typing.Literal['traits_v1'] = 'traits_v1'_, _custom: dict[str_, _~typing.Any] = <factory>_) 
    
The class is intended to be instantiated for each engine. 

regions _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Maps SearXNG’s internal representation of a region to the one of the engine.
SearXNG’s internal representation can be parsed by babel and the value is send to the engine:
```
regions ={
    'fr-BE' : <engine's region name>,
}

for key, egnine_region regions.items():
   searxng_region = babel.Locale.parse(key, sep='-')
   ...

```

languages _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Maps SearXNG’s internal representation of a language to the one of the engine.
SearXNG’s internal representation can be parsed by babel and the value is send to the engine:
```
languages = {
    'ca' : <engine's language name>,
}

for key, egnine_lang in languages.items():
   searxng_lang = babel.Locale.parse(key)
   ...

```

all_locale _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ _= None_ 
    
To which locale value SearXNG’s `all` language is mapped (shown a “Default language”). 

data_type _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['traits_v1']__= 'traits_v1'_ 
    
Data type, default is ‘traits_v1’. 

custom _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_ 
    
A place to store engine’s custom traits, not related to the SearXNG core. 

get_language(_searxng_locale :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _default :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Return engine’s language string that _best fits_ to SearXNG’s locale. 

Parameters: 
    
  * **searxng_locale** – SearXNG’s internal representation of locale selected by the user.
  * **default** – engine’s default language

The _best fits_ rules are implemented in [`searx.locales.get_engine_locale`](https://docs.searxng.org/src/searx.locales.html#searx.locales.get_engine_locale "searx.locales.get_engine_locale"). Except for the special value `all` which is determined from [`EngineTraits.all_locale`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits.all_locale "searx.enginelib.traits.EngineTraits.all_locale"). 

get_region(_searxng_locale :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _default :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Return engine’s region string that best fits to SearXNG’s locale. 

Parameters: 
    
  * **searxng_locale** – SearXNG’s internal representation of locale selected by the user.
  * **default** – engine’s default region

The _best fits_ rules are implemented in [`searx.locales.get_engine_locale`](https://docs.searxng.org/src/searx.locales.html#searx.locales.get_engine_locale "searx.locales.get_engine_locale"). Except for the special value `all` which is determined from [`EngineTraits.all_locale`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits.all_locale "searx.enginelib.traits.EngineTraits.all_locale"). 

is_locale_supported(_searxng_locale :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
A _locale_ (SearXNG’s internal representation) is considered to be supported by the engine if the _region_ or the _language_ is supported by the engine.
For verification the functions [`EngineTraits.get_region()`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits.get_region "searx.enginelib.traits.EngineTraits.get_region") and [`EngineTraits.get_language()`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits.get_language "searx.enginelib.traits.EngineTraits.get_language") are used. 

copy() 
    
Create a copy of the dataclass object. 

_classmethod_ fetch_traits(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) → [EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Call a function `fetch_traits(engine_traits)` from engines namespace to fetch and set properties from the origin engine in the object `engine_traits`. If function does not exists, `None` is returned. 

set_traits(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Set traits from self object in a [`Engine`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine") namespace. 

Parameters: 
    
**engine** – engine instance build by [`searx.engines.load_engine()`](https://docs.searxng.org/dev/engines/engines.html#searx.engines.load_engine "searx.engines.load_engine") 

_class_ searx.enginelib.traits.EngineTraitsMap 
    
A python dictionary to map [`EngineTraits`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits") by engine name. 

ENGINE_TRAITS_FILE _:[ Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)")_ _= PosixPath('/home/runner/work/searxng/searxng/searx/data/engine_traits.json')_ 
    
File with persistence of the [`EngineTraitsMap`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap "searx.enginelib.traits.EngineTraitsMap"). 

save_data() 
    
Store EngineTraitsMap in in file `self.ENGINE_TRAITS_FILE` 

_classmethod_ from_data() → [EngineTraitsMap](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap "searx.enginelib.traits.EngineTraitsMap") 
    
Instantiate [`EngineTraitsMap`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraitsMap "searx.enginelib.traits.EngineTraitsMap") object from `ENGINE_TRAITS` 

set_traits(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Set traits in a `Engine` namespace. 

Parameters: 
    
**engine** – engine instance build by [`searx.engines.load_engine()`](https://docs.searxng.org/dev/engines/engines.html#searx.engines.load_engine "searx.engines.load_engine")
