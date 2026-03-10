<!-- source: https://docs.searxng.org/dev/engines/online/gitea.html -->

# Gitea
Engine to search in collaborative software platforms based on [Gitea](https://about.gitea.com/) or [Forgejo](https://forgejo.org/).
## Configuration
The engine has the following mandatory setting:
  * [`base_url`](https://docs.searxng.org/dev/engines/online/gitea.html#searx.engines.gitea.base_url "searx.engines.gitea.base_url")

Optional settings are:
```
- name: gitea.com
  engine: gitea
  base_url: https://gitea.com
  shortcut: gitea

- name: forgejo.com
  engine: gitea
  base_url: https://code.forgejo.org
  shortcut: forgejo

```

If you would like to use additional instances, just configure new engines in the [settings](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines) and set the `base_url`.
## Implementation 

**engines.gitea.base_url** = `''`
URL of the [Gitea](https://about.gitea.com/) instance. 

**engines.gitea.sort** = `'updated'`
Sort criteria, possible values:
  * `updated` (default)
  * `alpha`
  * `created`
  * `size`
  * `id`

**engines.gitea.order** = `'desc'`
Sort order, possible values:
  * `desc` (default)
  * `asc`

**engines.gitea.page_size** = `10`
Maximum number of results per page (default 10).
