<!-- source: https://docs.searxng.org/dev/engines/demo/demo_offline.html -->

# Demo Offline Engine
Within this module we implement a _demo offline engine_. Do not look to close to the implementation, its just a simple example.
## Configuration
To get in use of this _demo_ engine add the following entry to your engines list in `settings.yml`:
```
- name: my offline engine
  engine: demo_offline
  shortcut: demo
  disabled: false

```

## Implementations
searx.engines.demo_offline.CACHE _:[ EngineCache](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.EngineCache "searx.enginelib.EngineCache")_ 
    
Persistent (SQLite) key/value cache that deletes its values after `expire` seconds. 

searx.engines.demo_offline.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Dynamic setup of the engine settings.
The origin of this demo engine is a simple json string which is loaded in this example while the engine is initialized.
For more details see [`searx.enginelib.Engine.setup`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.setup "searx.enginelib.Engine.setup"). 

searx.engines.demo_offline.init(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the engine.
For more details see [`searx.enginelib.Engine.init`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.init "searx.enginelib.Engine.init"). 

searx.engines.demo_offline.search(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :[RequestParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.abstract.RequestParams "searx.search.processors.abstract.RequestParams")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Query (offline) engine and return results. Assemble the list of results from your local engine.
In this demo engine we ignore the ‘query’ term, usual you would pass the ‘query’ term to your local engine to filter out the results.
