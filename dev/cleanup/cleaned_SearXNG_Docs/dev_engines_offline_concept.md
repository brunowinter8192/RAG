<!-- source: https://docs.searxng.org/dev/engines/offline_concept.html -->

# Offline Concept
offline engines
To extend the functionality of SearXNG, offline engines are going to be introduced. An offline engine is an engine which does not need Internet connection to perform a search and does not use HTTP to communicate.
Offline engines can be configured, by adding those to the engines list of [settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml). An example skeleton for offline engines can be found in [Demo Offline Engine](https://docs.searxng.org/dev/engines/demo/demo_offline.html#demo-offline-engine) ([demo_offline.py](https://github.com/searxng/searxng/blob/master/searx/engines/demo_offline.py)).
## Programming Interface 

[`init(engine_settings=None)`](https://docs.searxng.org/dev/engines/demo/demo_offline.html#searx.engines.demo_offline.init "searx.engines.demo_offline.init")
    
All offline engines can have their own init function to setup the engine before accepting requests. The function gets the settings from settings.yml as a parameter. This function can be omitted, if there is no need to setup anything in advance. 

[`search(query, params)`](https://docs.searxng.org/dev/engines/demo/demo_offline.html#searx.engines.demo_offline.search "searx.engines.demo_offline.search")
    
Each offline engine has a function named `search`. This function is responsible to perform a search and return the results in a presentable format. (Where _presentable_ means presentable by the selected result template.)
The return value is a list of results retrieved by the engine. 

Engine representation in `/config` 
    
If an engine is offline, the attribute `offline` is set to `True`.
## Extra Dependencies
If an offline engine depends on an external tool, SearXNG does not install it by default. When an administrator configures such engine and starts the instance, the process returns an error with the list of missing dependencies. Also, required dependencies will be added to the comment/description of the engine, so admins can install packages in advance.
If there is a need to install additional packages in _Python’s Virtual Environment_ of your SearXNG instance you need to switch into the environment ([Install SearXNG & dependencies](https://docs.searxng.org/admin/installation-searxng.html#searxng-src)) first, for this you can use [utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh):
```
$ sudo utils/searxng.sh instance cmd bash
(searxng-pyenv)$ pip install ...

```

## Private engines (Security)
To limit the access to offline engines, if an instance is available publicly, administrators can set token(s) for each of the [Private Engines (tokens)](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines). If a query contains a valid token, then SearXNG performs the requested private search. If not, requests from an offline engines return errors.
