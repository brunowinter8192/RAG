<!-- source: https://docs.searxng.org/dev/engines/online/recoll.html -->

# Recoll Engine
> **Info:**
  * [Recoll](https://www.lesbonscomptes.com/recoll/)
  * [recoll-webui](https://framagit.org/medoc92/recollwebui.git)
  * [git://searx/engines/recoll.py](https://github.com/searxng/searxng/blob/master/searx/engines/recoll.py)

[Recoll](https://www.lesbonscomptes.com/recoll/) is a desktop full-text search tool based on Xapian. By itself [Recoll](https://www.lesbonscomptes.com/recoll/) does not offer WEB or API access, this can be achieved using [recoll-webui](https://framagit.org/medoc92/recollwebui.git)
## Configuration
You must configure the following settings:
Example scenario:
  1. Recoll indexes a local filesystem mounted in `/export/documents/reference`,
  2. the Recoll search interface can be reached at <https://recoll.example.org/> and
  3. the contents of this filesystem can be reached though <https://download.example.org/reference>

```
base_url: https://recoll.example.org
mount_prefix: /export/documents
dl_prefix: https://download.example.org
search_dir: ""

```

## Implementations
**engines.recoll.base_url** = `''`
Location where recoll-webui can be reached. 

**engines.recoll.mount_prefix** = `''`
Location where the file hierarchy is mounted on your _local_ filesystem. 

**engines.recoll.dl_prefix** = `''`
Location where the file hierarchy as indexed by recoll can be reached. 

**engines.recoll.search_dir** = `''`
Part of the indexed file hierarchy to be search, if empty the full domain is searched. 

searx.engines.recoll.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the Recoll engine, checks if the mandatory values are configured.
