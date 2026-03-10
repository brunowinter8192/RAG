<!-- source: https://docs.searxng.org/dev/plugins/development.html -->

# Plugin Development
Further reading ..
Plugins can extend or replace functionality of various components of SearXNG.
Entry points (hooks) define when a plugin runs. Right now only three hooks are implemented. So feel free to implement a hook if it fits the behaviour of your plugin / a plugin doesn’t need to implement all the hooks.
  * pre search: [`Plugin.pre_search`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin.pre_search "searx.plugins.Plugin.pre_search")
  * post search: [`Plugin.post_search`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin.post_search "searx.plugins.Plugin.post_search")
  * on each result item: [`Plugin.on_result`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin.on_result "searx.plugins.Plugin.on_result")

Below you will find some examples, for more coding examples have a look at the built-in plugins [git://searx/plugins/](https://github.com/searxng/searxng/blob/master/searx/plugins/) or [Only show green hosted results](https://github.com/return42/tgwf-searx-plugins/).
## Add Answer example
Here is an example of a very simple plugin that adds a “Hello World” into the answer area:
```
from flask_babel import gettext as _
from searx.plugins import Plugin
from searx.result_types import Answer

class MyPlugin(Plugin):

    id = "hello world"

    def __init__(self, plg_cfg):
        super().__init__(plg_cfg)
        self.info = PluginInfo(id=self.id, name=_("Hello"), description=_("demo plugin"))

    def post_search(self, request, search):
        return [ Answer(answer="Hello World") ]

```

## Filter URLs example
Further reading ..
  * [`Result.filter_urls(..)`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.filter_urls "searx.result_types._base.Result.filter_urls")

The [`Result.filter_urls(..)`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.filter_urls "searx.result_types._base.Result.filter_urls") can be used to filter and/or modify URL fields. In the following example, the filter function `my_url_filter`:
```
def my_url_filter(result, field_name, url_src) -> bool | str:
    if "google" in url_src:
        return False              # remove URL field from result
    if "facebook" in url_src:
        new_url = url_src.replace("facebook", "fb-dummy")
        return new_url            # return modified URL
    return True                   # leave URL in field unchanged

```

is applied to all URL fields in the [`Plugin.on_result`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin.on_result "searx.plugins.Plugin.on_result") hook:
```
class MyUrlFilter(Plugin):
    ...
    def on_result(self, request, search, result) -> bool:
        result.filter_urls(my_url_filter)
        return True

```

## Implementation 

_class_ searx.plugins.Plugin(_plg_cfg :[PluginCfg](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins._core.PluginCfg")_) 
    
Abstract base class of all Plugins. 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= ''_ 
    
The ID (suffix) in the HTML form. 

active _:[ ClassVar](https://docs.python.org/3/library/typing.html#typing.ClassVar "\(in Python v3.14\)")[[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")]_ 
    
Plugin is enabled/disabled by default ([`PluginCfg.active`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg.active "searx.plugins.PluginCfg.active")). 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__=[]_ 
    
Keywords in the search query that activate the plugin. The _keyword_ is the first word in a search query. If a plugin should be executed regardless of the search query, the list of keywords should be empty (which is also the default in the base class for Plugins). 

info _:[ PluginInfo](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginInfo "searx.plugins._core.PluginInfo")_ 
    
Information about the _plugin_ , see [`PluginInfo`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginInfo "searx.plugins.PluginInfo"). 

log _:[ Logger](https://docs.python.org/3/library/logging.html#logging.Logger "\(in Python v3.14\)")_ 
    
A logger object, is automatically initialized when calling the constructor (if not already set in the subclass). 

init(_app :[flask.Flask](https://flask.palletsprojects.com/en/stable/api/#flask.Flask "\(in Flask v3.1.x\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the plugin, the return value decides whether this plugin is active or not. Initialization only takes place once, at the time the WEB application is set up. The base method always returns `True`, the method can be overwritten in the inheritances,
  * `True` plugin is active
  * `False` plugin is inactive

pre_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Runs BEFORE the search request and returns a boolean:
  * `True` to continue the search
  * `False` to stop the search

on_result(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_, _result :[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Runs for each result of each engine and returns a boolean:
  * `True` to keep the result
  * `False` to remove the result from the result list

The `result` can be modified to the needs.
Hint
If [`Result.url`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.url "searx.result_types._base.Result.url") is modified, [`Result.parsed_url`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result.parsed_url "searx.result_types._base.Result.parsed_url") must be changed accordingly:
```
result["parsed_url"] = urlparse(result["url"])

```

post_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")|[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[Result](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")|[LegacyResult](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.LegacyResult "searx.result_types._base.LegacyResult")]|[EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Runs AFTER the search request. Can return a list of [`Result`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result") objects to be added to the final result list. 

_class_ searx.plugins.PluginInfo(_id: str_, _name: str_, _description: str_, _preference_section: ~typing.Literal['general'_, _'ui'_ , _'privacy'_ , _'query'] | None = 'general'_, _examples: list[str] = <factory>_, _keywords: list[str] = <factory>_) 
    
Object that holds information about a _plugin_ , these infos are shown to the user in the Preferences menu.
To be able to translate the information into other languages, the text must be written in English and translated with [`flask_babel.gettext`](https://python-babel.github.io/flask-babel/index.html#flask_babel.gettext "\(in Flask-Babel\)"). 

id _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
The ID-selector in HTML/CSS #<id>. 

name _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the _plugin_. 

description _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Short description of the _answerer_. 

preference_section _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['general','ui','privacy','query']|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ _= 'general'_ 
    
Section (tab/group) in the preferences where this plugin is shown to the user.
The value `query` is reserved for plugins that are activated via a _keyword_ as part of a search query, see:
Those plugins are shown in the preferences in tab _Special Queries_. 

examples _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of short examples of the usage / of query terms. 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
See [`Plugin.keywords`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin.keywords "searx.plugins.Plugin.keywords") 

_class_ searx.plugins.PluginStorage 
    
A storage for managing the _plugins_ of SearXNG. 

plugin_list _:[ set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[Plugin](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin "searx.plugins._core.Plugin")]_ 
    
The list of `Plugins` in this storage. 

load_settings(_cfg :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]]_) 
    
Load plugins configured in SearXNG’s settings [plugins:](https://docs.searxng.org/admin/settings/settings_plugins.html#settings-plugins). 

register(_plugin :[Plugin](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin "searx.plugins._core.Plugin")_) 
    
Register a [`Plugin`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin "searx.plugins.Plugin"). In case of name collision (if two plugins have same ID) a [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError "\(in Python v3.14\)") exception is raised. 

init(_app :[flask.Flask](https://flask.palletsprojects.com/en/stable/api/#flask.Flask "\(in Flask v3.1.x\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Calls the method [`Plugin.init`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.Plugin.init "searx.plugins.Plugin.init") of each plugin in this storage. Depending on its return value, the plugin is removed from _this_ storage or not. 

post_search(_request :[SXNG_Request](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Request "searx.extended_types.SXNG_Request")_, _search :[SearchWithPlugins](https://docs.searxng.org/src/searx.search.html#searx.search.SearchWithPlugins "searx.search.SearchWithPlugins")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Extend `search.result_container <searx.results.ResultContainer`> with result items from plugins listed in `search.user_plugins`. 

_class_ searx.plugins.PluginCfg(_active :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) 
    
Settings of a plugin.
```
mypackage.mymodule.MyPlugin:
  active: true

```

active _:[ bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ _= False_ 
    
Plugin is active by default and the user can _opt-out_ in the preferences.
