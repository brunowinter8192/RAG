<!-- source: https://docs.searxng.org/dev/engines/online/torznab.html -->

# Torznab WebAPI
[Torznab](https://torznab.github.io/spec-1.3-draft/index.html) is an API specification that provides a standardized way to query torrent site for content. It is used by a number of torrent applications, including [Prowlarr](https://github.com/Prowlarr/Prowlarr) and [Jackett](https://github.com/Jackett/Jackett).
Using this engine together with [Prowlarr](https://github.com/Prowlarr/Prowlarr) or [Jackett](https://github.com/Jackett/Jackett) allows you to search a huge number of torrent sites which are not directly supported.
## Configuration
The engine has the following settings: 

`base_url`:
    
Torznab endpoint URL. 

`api_key`:
    
The API key to use for authentication. 

`torznab_categories`:
    
The categories to use for searching. This is a list of category IDs. See [Prowlarr-categories](https://wiki.servarr.com/en/prowlarr/cardigann-yml-definition#categories) or [Jackett-categories](https://github.com/Jackett/Jackett/wiki/Jackett-Categories) for more information. 

`show_torrent_files`:
    
Whether to show the torrent file in the search results. Be careful as using this with [Prowlarr](https://github.com/Prowlarr/Prowlarr) or [Jackett](https://github.com/Jackett/Jackett) leaks the API key. This should be used only if you are querying a Torznab endpoint without authentication or if the instance is private. Be aware that private trackers may ban you if you share the torrent file. Defaults to `false`. 

`show_magnet_links`:
    
Whether to show the magnet link in the search results. Be aware that private trackers may ban you if you share the magnet link. Defaults to `true`.
## Implementations
**engines.torznab.init(_engine_settings =None_)**
Initialize the engine. 

searx.engines.torznab.request(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] 
    
Build the request params. 

searx.engines.torznab.response(_resp :[SXNG_Response](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]] 
    
Parse the XML response and return a list of results. 

searx.engines.torznab.build_result(_item :[Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.Element "\(in lxml v6.0.0\)")_) → [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] 
    
Build a result from a XML item. 

searx.engines.torznab.get_attribute(_item :[Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.Element "\(in lxml v6.0.0\)")_, _property_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Get attribute from item. 

searx.engines.torznab.get_torznab_attribute(_item :[Element](https://lxml.de/apidoc/lxml.etree.html#lxml.etree.Element "\(in lxml v6.0.0\)")_, _attribute_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Get torznab special attribute from item.
