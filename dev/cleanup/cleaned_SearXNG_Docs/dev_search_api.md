<!-- source: https://docs.searxng.org/dev/search_api.html -->

# Search API
SearXNG supports querying via a simple HTTP API. Two endpoints, `/` and `/search`, are supported for both GET and POST methods. The GET method expects parameters as URL query parameters, while the POST method expects parameters as form data.
If you want to consume the results as JSON, CSV, or RSS, you need to set the `format` parameter accordingly. Supported formats are defined in `settings.yml`, under the `search` section. Requesting an unset format will return a 403 Forbidden error. Be aware that many public instances have these formats disabled.
Endpoints:
`GET /` `GET /search`
`POST /` `POST /search`
example cURL calls:
```
curl 'https://searx.example.org/search?q=searxng&format=json'

curl -X POST 'https://searx.example.org/search' -d 'q=searxng&format=csv'

curl -L -X POST -d 'q=searxng&format=json' 'https://searx.example.org/'

```

## Parameters
Further reading ..
`q`required 
    
The search query. This string is passed to external search services. Thus, SearXNG supports syntax of each search service. For example, `site:github.com SearXNG` is a valid query for Google. However, if simply the query above is passed to any search engine which does not filter its results based on this syntax, you might not get the results you wanted.
See more at [Search syntax](https://docs.searxng.org/user/search-syntax.html#search-syntax) 

`categories`optional 
    
Comma separated list, specifies the active search categories (see [Configured Engines](https://docs.searxng.org/user/configured_engines.html#configured-engines)) 

`engines`optional 
    
Comma separated list, specifies the active search engines (see [Configured Engines](https://docs.searxng.org/user/configured_engines.html#configured-engines)). 

`language`default from [search:](https://docs.searxng.org/admin/settings/settings_search.html#settings-search) 
    
Code of the language. 

`pageno`default `1` 
    
Search page number. 

`time_range`optional 
    
[ `day`, `month`, `year` ]
Time range of search for engines which support it. See if an engine supports time range search in the preferences page of an instance. 

`format`optional 
    
[ `json`, `csv`, `rss` ]
Output format of results. Format needs to be activated in [search:](https://docs.searxng.org/admin/settings/settings_search.html#settings-search). 

`results_on_new_tab`default `0` 
    
[ `0`, `1` ]
Open search results on new tab. 

`image_proxy`default from [server:](https://docs.searxng.org/admin/settings/settings_server.html#settings-server) 
    
[ `True`, `False` ]
Proxy image results through SearXNG. 

`autocomplete`default from [search:](https://docs.searxng.org/admin/settings/settings_search.html#settings-search) 
    
[ `google`, `dbpedia`, `duckduckgo`, `mwmbl`, `startpage`, `wikipedia`, `swisscows`, `qwant` ]
Service which completes words as you type. 

`safesearch`default from [search:](https://docs.searxng.org/admin/settings/settings_search.html#settings-search) 
    
[ `0`, `1`, `2` ]
Filter search results of engines which support safe search. See if an engine supports safe search in the preferences page of an instance. 

`theme`default `simple` 
    
[ `simple` ]
Theme of instance.
Please note, available themes depend on an instance. It is possible that an instance administrator deleted, created or renamed themes on their instance. See the available options in the preferences page of the instance. 

`enabled_plugins`optional 
    
List of enabled plugins. 

default: 
    
`Hash_plugin`, `Self_Information`, `Tracker_URL_remover`, `Ahmia_blacklist` 

values: 
    
`Hash_plugin`, `Self_Information`, `Tracker_URL_remover`, `Ahmia_blacklist`,
`Hostnames_plugin`, `Open_Access_DOI_rewrite`, `Vim-like_hotkeys`, `Tor_check_plugin` 

`disabled_plugins`: optional
    
List of disabled plugins. 

default: 
    
`Hostnames_plugin`, `Open_Access_DOI_rewrite`, `Vim-like_hotkeys`, `Tor_check_plugin` 

values: 
    
see values from `enabled_plugins` 

`enabled_engines`optional _all_ [engines](https://github.com/searxng/searxng/blob/master/searx/engines) 
    
List of enabled engines. 

`disabled_engines`optional _all_ [engines](https://github.com/searxng/searxng/blob/master/searx/engines) 
    
List of disabled engines.
