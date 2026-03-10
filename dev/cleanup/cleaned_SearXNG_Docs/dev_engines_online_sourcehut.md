<!-- source: https://docs.searxng.org/dev/engines/online/sourcehut.html -->

# Sourcehut
Engine to search in the collaborative software platform [SourceHut](https://sourcehut.org/).
## Configuration
You can configure the following setting:
  * [`sourcehut_sort_order`](https://docs.searxng.org/dev/engines/online/sourcehut.html#searx.engines.sourcehut.sourcehut_sort_order "searx.engines.sourcehut.sourcehut_sort_order")

```
- name: sourcehut
  shortcut: srht
  engine: sourcehut
  # sourcehut_sort_order: longest-active

```

## Implementations 

**engines.sourcehut.base_url** = `'https://sr.ht/projects'`
Browse public projects. 

**engines.sourcehut.sourcehut_sort_order** = `'recently-updated'`
The sort order of the results. Possible values:
  * `recently-updated`
  * `longest-active`
