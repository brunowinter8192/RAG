<!-- source: https://docs.searxng.org/dev/engines/mediawiki.html -->

# MediaWiki Engine
The MediaWiki engine is a _generic_ engine to **query** Wikimedia wikis by the [MediaWiki Action API](https://www.mediawiki.org/wiki/API:Main_page). For a [query action](https://www.mediawiki.org/w/api.php?action=help&modules=query) all Wikimedia wikis have endpoints that follow this pattern:
```
https://{base_url}/w/api.php?action=query&list=search&format=json

```

Note
In its actual state, this engine is implemented to parse JSON result ([format=json](https://www.mediawiki.org/w/api.php?action=help&modules=json)) from a search query ([list=search](https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsearch)). If you need other `action` and `list` types ask SearXNG developers to extend the implementation according to your needs.
## Configuration
Request:
## Implementations
**engines.mediawiki.search_type** = `'nearmatch'`
Which type of search to perform. One of the following values: `nearmatch`, `text` or `title`.
See `srwhat` argument in [list=search](https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsearch) documentation. 

**engines.mediawiki.srenablerewrites** = `True`
Enable internal query rewriting (Type: boolean). Some search backends can rewrite the query into another which is thought to provide better results, for instance by correcting spelling errors.
See `srenablerewrites` argument in [list=search](https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsearch) documentation. 

**engines.mediawiki.srsort** = `'relevance'`
Set the sort order of returned results. One of the following values: `create_timestamp_asc`, `create_timestamp_desc`, `incoming_links_asc`, `incoming_links_desc`, `just_match`, `last_edit_asc`, `last_edit_desc`, `none`, `random`, `relevance`, `user_random`.
See `srenablerewrites` argument in [list=search](https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsearch) documentation. 

**engines.mediawiki.srprop** = `'sectiontitle|snippet|timestamp|categorysnippet'`
Which properties to return.
See `srprop` argument in [list=search](https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsearch) documentation. 

**engines.mediawiki.base_url** = `'https://{language}.wikipedia.org/'`
Base URL of the Wikimedia wiki. 

`{language}`:
    
ISO 639-1 language code (en, de, fr ..) of the search language. 

**engines.mediawiki.api_path** = `'w/api.php'`
The path the PHP api is listening on.
The default path should work fine usually. 

**engines.mediawiki.timestamp_format** = `'%Y-%m-%dT%H:%M:%SZ'`
The longhand version of MediaWiki time strings.
