<!-- source: https://docs.searxng.org/dev/engines/demo/demo_online.html -->

# Demo Online Engine
Within this module we implement a _demo online engine_. Do not look to close to the implementation, its just a simple example which queries [The Art Institute of Chicago](https://www.artic.edu)
## Configuration
To get in use of this _demo_ engine add the following entry to your engines list in `settings.yml`:
```
- name: my online engine
  engine: demo_online
  shortcut: demo
  disabled: false

```

## Implementations
searx.engines.demo_online.setup(_engine_settings :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Dynamic setup of the engine settings.
For more details see [`searx.enginelib.Engine.setup`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.setup "searx.enginelib.Engine.setup"). 

searx.engines.demo_online.init(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the engine.
For more details see [`searx.enginelib.Engine.init`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.init "searx.enginelib.Engine.init"). 

searx.engines.demo_online.request(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _params :[OnlineParams](https://docs.searxng.org/src/searx.search.processors.html#searx.search.processors.online.OnlineParams "searx.search.processors.online.OnlineParams")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Build up the `params` for the online request. In this example we build a URL to fetch images from [artic.edu](https://artic.edu). 

searx.engines.demo_online.response(_resp :[SXNG_Response](https://docs.searxng.org/dev/extended_types.html#searx.extended_types.SXNG_Response "searx.extended_types.SXNG_Response")_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Parse out the result items from the response. In this example we parse the response from [api.artic.edu](https://artic.edu) and filter out all images.
