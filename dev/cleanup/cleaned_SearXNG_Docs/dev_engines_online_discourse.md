<!-- source: https://docs.searxng.org/dev/engines/online/discourse.html -->

# Discourse Forums
> **Info:**
  * [builtwith.com Discourse](https://trends.builtwith.com/websitelist/Discourse)

Discourse is an open source Internet forum system. To search in a forum this engine offers some additional settings:
## Example
To search in your favorite Discourse forum, add a configuration like shown here for the `paddling.com` forum:
```
- name: paddling
  engine: discourse
  shortcut: paddle
  base_url: 'https://forums.paddling.com/'
  api_order: views
  categories: ['social media', 'sports']
  show_avatar: true

```

If the forum is private, you need to add an API key and username for the search:
```
- name: paddling
  engine: discourse
  shortcut: paddle
  base_url: 'https://forums.paddling.com/'
  api_order: views
  categories: ['social media', 'sports']
  show_avatar: true
  api_key: '<KEY>'
  api_username: 'system'

```

## Implementations 

**engines.discourse.base_url** = `None`
URL of the Discourse forum. 

**engines.discourse.search_endpoint** = `'/search.json'`
URL path of the [search endpoint](https://docs.discourse.org/#tag/Search). 

**engines.discourse.api_order** = `'likes'`
Order method, valid values are: `latest`, `likes`, `views`, `latest_topic` 

**engines.discourse.show_avatar** = `False`
Show avatar of the user who send the post. 

**engines.discourse.api_key** = `''`
API key of the Discourse forum. 

**engines.discourse.api_username** = `''`
API username of the Discourse forum.
