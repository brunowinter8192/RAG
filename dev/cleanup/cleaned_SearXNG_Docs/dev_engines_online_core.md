<!-- source: https://docs.searxng.org/dev/engines/online/core.html -->

# CORE
[CORE](https://core.ac.uk/about) (COnnecting REpositories) provides a comprehensive bibliographic database of the world’s scholarly literature, collecting and indexing research from repositories and journals.
Note
The CORE engine requires an [`API key`](https://docs.searxng.org/dev/engines/online/core.html#searx.engines.core.api_key "searx.engines.core.api_key").
## Configuration
The engine has the following additional settings:
  * [`api_key`](https://docs.searxng.org/dev/engines/online/core.html#searx.engines.core.api_key "searx.engines.core.api_key")

```
- name: core.ac.uk
  api_key: "..."
  inactive: false

```

## Implementations
**engines.core.api_key** = `''`
For an API key register at <https://core.ac.uk/services/api> and insert the API key in the engine [Configuration](https://docs.searxng.org/dev/engines/online/core.html#core-engine-config). 

searx.engines.core.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the [CORE](https://core.ac.uk/about) engine, checks whether the [`api_key`](https://docs.searxng.org/dev/engines/online/core.html#searx.engines.core.api_key "searx.engines.core.api_key") is set, otherwise the engine is inactive.
