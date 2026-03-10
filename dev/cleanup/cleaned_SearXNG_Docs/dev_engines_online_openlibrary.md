<!-- source: https://docs.searxng.org/dev/engines/online/openlibrary.html -->

# Open Library
[Open Library](https://openlibrary.org) is an open, editable library catalog, building towards a web page for every book ever published.
## Configuration
The service sometimes takes a very long time to respond, the `timeout` may need to be adjusted.
```
- name: openlibrary
  engine: openlibrary
  shortcut: ol
  timeout: 10

```

## Implementations 

**engines.openlibrary.search_api** = `'https://openlibrary.org/search.json'`
The engine uses the API at the endpoint [search.json](https://openlibrary.org/dev/docs/api/search).
