<!-- source: https://docs.searxng.org/dev/engines/online/semantic_scholar.html -->

# Semantic Scholar
[Semantic Scholar](https://www.semanticscholar.org/about) provides free, AI-driven search and discovery tools, and open resources for the global research community. [Semantic Scholar](https://www.semanticscholar.org/about) index over 200 million academic papers sourced from publisher partnerships, data providers, and web crawls.
## Configuration
To get in use of this engine add the following entry to your engines list in `settings.yml`:
```
- name: semantic scholar
  engine: semantic_scholar
  shortcut: se

```

## Implementations 

searx.engines.semantic_scholar.CACHE _:[ EngineCache](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.EngineCache "searx.enginelib.EngineCache")_ 
    
Persistent (SQLite) key/value cache that deletes its values after `expire` seconds.
