<!-- source: https://docs.searxng.org/dev/engines/online/bt4g.html -->

# BT4G
Contents
[BT4G](https://bt4g.com/) (bt4g.com) is not a tracker and doesn’t store any content and only collects torrent metadata (such as file names and file sizes) and a magnet link (torrent identifier).
This engine does not parse the HTML page because there is an API in XML (RSS). The RSS feed provides fewer data like amount of seeders/leechers and the files in the torrent file. It’s a tradeoff for a “stable” engine as the XML from RSS content will change way less than the HTML page.
## Configuration
The engine has the following additional settings:
With this options a SearXNG maintainer is able to configure **additional** engines for specific torrent searches. For example a engine to search only for Movies and sort the result list by the count of seeders.
```
- name: bt4g.movie
  engine: bt4g
  shortcut: bt4gv
  categories: video
  bt4g_order_by: seeders
  bt4g_category: 'movie'

```

## Implementations
**engines.bt4g.bt4g_order_by** = `'relevance'`
Result list can be ordered by `relevance` (default), `size`, `seeders` or `time`.
Hint
When _time_range_ is activate, the results always ordered by `time`. 

**engines.bt4g.bt4g_category** = `'all'`
BT$G offers categories: `all` (default), `audio`, `movie`, `doc`, `app` and `` other``.
