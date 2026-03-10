<!-- source: https://docs.searxng.org/dev/engines/online/gitlab.html -->

# GitLab
Engine to search in collaborative software platforms based on [GitLab](https://about.gitlab.com/install/) with the [GitLab REST API](https://docs.gitlab.com/ee/api/).
## Configuration
The engine has the following mandatory setting:
  * [`base_url`](https://docs.searxng.org/dev/engines/online/gitlab.html#searx.engines.gitlab.base_url "searx.engines.gitlab.base_url")

Optional settings are:
  * [`api_path`](https://docs.searxng.org/dev/engines/online/gitlab.html#searx.engines.gitlab.api_path "searx.engines.gitlab.api_path")

```
- name: gitlab
  engine: gitlab
  base_url: https://gitlab.com
  shortcut: gl
  about:
    website: https://gitlab.com/
    wikidata_id: Q16639197

- name: gnome
  engine: gitlab
  base_url: https://gitlab.gnome.org
  shortcut: gn
  about:
    website: https://gitlab.gnome.org
    wikidata_id: Q44316

```

## Implementations 

**engines.gitlab.base_url** = `''`
Base URL of the GitLab host. 

**engines.gitlab.api_path** = `'api/v4/projects'`
The path the [project API](https://docs.gitlab.com/ee/api/projects.html).
The default path should work fine usually.
