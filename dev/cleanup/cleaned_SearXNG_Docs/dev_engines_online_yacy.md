<!-- source: https://docs.searxng.org/dev/engines/online/yacy.html -->

# Yacy
Contents
[YaCy](https://yacy.net/) is a free distributed search engine, built on the principles of peer-to-peer (P2P) networks.
API: [Dev:APIyacysearch](https://wiki.yacy.net/index.php/Dev:APIyacysearch)
Releases:
  * <https://github.com/yacy/yacy_search_server/tags>
  * <https://download.yacy.net/>

## Configuration
The engine has the following (additional) settings:
The [`base_url`](https://docs.searxng.org/dev/engines/online/yacy.html#searx.engines.yacy.base_url "searx.engines.yacy.base_url") has to be set in the engine named yacy and is used by all yacy engines (unless an individual value for `base_url` is configured for the engine).
```
- name: yacy
  engine: yacy
  categories: general
  search_type: text
  shortcut: ya
  base_url:
    - https://yacy.searchlab.eu
    - https://search.lomig.me
    - https://yacy.ecosys.eu
    - https://search.webproject.link

- name: yacy images
  engine: yacy
  categories: images
  search_type: image
  shortcut: yai
  disabled: true

```

## Implementations
**engines.yacy.http_digest_auth_user** = `''`
HTTP digest user for the local YACY instance 

**engines.yacy.http_digest_auth_pass** = `''`
HTTP digest password for the local YACY instance 

**engines.yacy.search_mode** = `'global'`
Yacy search mode `global` or `local`. By default, Yacy operates in `global` mode. 

`global`
    
Peer-to-Peer search 

`local`
    
Privacy or Stealth mode, restricts the search to local yacy instance. 

**engines.yacy.search_type** = `'text'`
One of `text`, `image` / The search-types `app`, `audio` and `video` are not yet implemented (Pull-Requests are welcome). 

**engines.yacy.base_url** = `[]`
The value is an URL or a list of URLs. In the latter case instance will be selected randomly.
