<!-- source: https://docs.searxng.org/src/searx.search.processors.html -->

# Search processors
## Abstract processor class
Abstract base classes for all engine processors. 

_class_ searx.search.processors.abstract.RequestParams 
    
Basic quantity of the Request parameters of all engine types. 

query _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Search term, stripped of search syntax arguments. 

category _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Current category, like `general`.
Hint
This field is deprecated, don’t use it in further implementations.
This field is currently _arbitrarily_ filled with the name of “one”” category (the name of the first category of the engine). In practice, however, it is not clear what this “one” category should be; in principle, multiple categories can also be activated in a search. 

pageno _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Current page number, where the first page is `1`. 

safesearch _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")[0,1,2]_ 
    
Safe-Search filter (0:normal, 1:moderate, 2:strict). 

time_range _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['day','week','month','year']|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Time-range filter. 

engine_data _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Allows the transfer of (engine specific) data to the next request of the client. In the case of the `online` engines, this data is delivered to the client via the HTML `<form>` in response.
If the client then sends this form back to the server with the next request, this data will be available.
This makes it possible to carry data from one request to the next without a session context, but this feature (is fragile) and should only be used in exceptional cases. See also [engine_data_form](https://docs.searxng.org/dev/templates.html#engine-data). 

searxng_locale _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Language / locale filter from the search request, a string like ‘all’, ‘en’, ‘en-US’, ‘zh-HK’ .. and others, for more details see [`searx.locales`](https://docs.searxng.org/src/searx.locales.html#module-searx.locales "searx.locales"). 

_class_ searx.search.processors.abstract.SuspendedStatus 
    
Class to handle suspend state. 

_class_ searx.search.processors.abstract.EngineProcessor(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Base classes used for all types of request processors. 

initialize(_callback :[Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")[[[EngineProcessor](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.abstract.EngineProcessor "searx.search.processors.abstract.EngineProcessor"),[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")],[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")]_) 
    
Initialization of _this_ [`EngineProcessor`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.abstract.EngineProcessor "searx.search.processors.abstract.EngineProcessor").
If processor’s engine has an `init` method, it is called first. Engine’s `init` method is executed in a thread, meaning that the _registration_ (the `callback`) may occur later and is not already established by the return from this registration method.
Registration only takes place if the `init` method is not available or is successfully run through. 

get_params(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_, _engine_category :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [RequestParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.abstract.RequestParams "searx.search.processors.abstract.RequestParams")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns a dictionary with the [request parameters](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-arguments) ([`RequestParams`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.abstract.RequestParams "searx.search.processors.abstract.RequestParams")), if the search condition is not supported by the engine, `None` is returned:
  * 

_time range_ filter in search conditions, but the engine does not have
    
a corresponding filter
  * page number > 1 when engine does not support paging
  * page number > `max_page`

## Offline processor
Processors for engine-type: `offline` 

_class_ searx.search.processors.offline.OfflineProcessor(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Processor class used by `offline` engines.
## Online processor
Processor used for `online` engines. 

_class_ searx.search.processors.online.OnlineProcessor(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Processor class for `online` engines. 

init_engine() → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
This method is called in a thread, and before the base method is called, the network must be set up for the `online` engines. 

get_params(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_, _engine_category :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns a dictionary with the [request params](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online) ([`OnlineParams`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")), if the search condition is not supported by the engine, `None` is returned. 

_class_ searx.search.processors.online.OnlineParams 
    
Request parameters of a `online` engine.
## Online currency processor
Processor used for `online_currency` engines. 

**search.processors.online_currency.search_syntax** = `re.compile('.*?(\\\d+(?:\\\\.\\\d+)?) ([^.0-9]+) (?:in|to) ([^.0-9]+)', re.IGNORECASE)`
Search syntax used for from/to currency (e.g. `10 usd to eur`) 

_class_ searx.search.processors.online_currency.CurrenciesParams 
    
Currencies request parameters. 

amount _:[ float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ 
    
Currency amount to be converted 

to_iso4217 _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
[ISO_4217](https://en.wikipedia.org/wiki/ISO_4217) alpha code of the currency used as the basis for conversion. 

from_iso4217 _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
[ISO_4217](https://en.wikipedia.org/wiki/ISO_4217) alpha code of the currency to be converted. 

from_name _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the currency used as the basis for conversion. 

to_name _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the currency of the currency to be converted. 

_class_ searx.search.processors.online_currency.OnlineCurrenciesParams 
    
Request parameters of a `online_currency` engine. 

_class_ searx.search.processors.online_currency.OnlineCurrencyProcessor(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Processor class used by `online_currency` engines. 

get_params(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_, _engine_category :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [OnlineCurrenciesParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_currency.OnlineCurrenciesParams "searx.search.processors.online_currency.OnlineCurrenciesParams")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns a dictionary with the [request params](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online-currency) ([`OnlineCurrenciesParams`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_currency.OnlineCurrenciesParams "searx.search.processors.online_currency.OnlineCurrenciesParams")). `None` is returned if the search query does not match [`search_syntax`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_currency.search_syntax "searx.search.processors.online_currency.search_syntax").
## Online dictionary processor
Processor used for `online_dictionary` engines. 

**search.processors.online_dictionary.search_syntax** = `re.compile('.*?([a-z]+)-([a-z]+) (.+)$', re.IGNORECASE)`
Search syntax used for from/to language (e.g. `en-de`) 

searx.search.processors.online_dictionary.FromToType 
    
Type of a language descriptions in the context of a `online_dictionary`.
alias of [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[`bool`](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)"), [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 

_class_ searx.search.processors.online_dictionary.DictParams 
    
Dictionary request parameters. 

from_lang _:[ tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Language from which is to be translated. 

to_lang _:[ tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Language to translate into. 

query _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Search term, cleaned of search syntax (_from-to_ has been removed). 

_class_ searx.search.processors.online_dictionary.OnlineDictParams 
    
Request parameters of a `online_dictionary` engine. 

_class_ searx.search.processors.online_dictionary.OnlineDictionaryProcessor(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Processor class for `online_dictionary` engines. 

get_params(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_, _engine_category :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [OnlineDictParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_dictionary.OnlineDictParams "searx.search.processors.online_dictionary.OnlineDictParams")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns a dictionary with the [request params](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online-dictionary) ([`OnlineDictParams`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_dictionary.OnlineDictParams "searx.search.processors.online_dictionary.OnlineDictParams")). `None` is returned if the search query does not match [`search_syntax`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_dictionary.search_syntax "searx.search.processors.online_dictionary.search_syntax").
## Online URL search processor
Processor used for `online_url_search` engines. 

**search.processors.online_url_search.search_syntax** = `{'data:image': re.compile('data:image/[^; ]*;base64,[^ ]*'), 'ftp': re.compile('ftps?:\\\/\\\/[^ ]*'), 'http': re.compile('https?:\\\/\\\/[^ ]*')}`
Search syntax used for a URL search. 

_class_ searx.search.processors.online_url_search.UrlParams 
    
URL request parameters. 

_class_ searx.search.processors.online_url_search.OnlineUrlSearchParams 
    
Request parameters of a `online_url_search` engine. 

_class_ searx.search.processors.online_url_search.OnlineUrlSearchProcessor(_engine :[Engine](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine "searx.enginelib.Engine")|[types.ModuleType](https://docs.python.org/3/library/types.html#types.ModuleType "\(in Python v3.14\)")_) 
    
Processor class used by `online_url_search` engines. 

get_params(_search_query :[SearchQuery](https://docs.searxng.org/src/searx.search.html#searx.search.models.SearchQuery "searx.search.models.SearchQuery")_, _engine_category :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [OnlineUrlSearchParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_url_search.OnlineUrlSearchParams "searx.search.processors.online_url_search.OnlineUrlSearchParams")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns a dictionary with the [request params](https://docs.searxng.org/dev/engines/engine_overview.html#engine-request-online-currency) ([`OnlineUrlSearchParams`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_url_search.OnlineUrlSearchParams "searx.search.processors.online_url_search.OnlineUrlSearchParams")). `None` is returned if the search query does not match [`search_syntax`](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online_url_search.search_syntax "searx.search.processors.online_url_search.search_syntax").
