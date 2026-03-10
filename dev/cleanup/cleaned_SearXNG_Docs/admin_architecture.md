<!-- source: https://docs.searxng.org/admin/architecture.html -->

# Architecture
Further reading
  * Reverse Proxy: [Apache](https://docs.searxng.org/admin/installation-apache.html#apache-searxng-site) & [nginx](https://docs.searxng.org/admin/installation-nginx.html#nginx-searxng-site)
  * uWSGI: [uWSGI](https://docs.searxng.org/admin/installation-uwsgi.html#searxng-uwsgi)
  * SearXNG: [Step by step installation](https://docs.searxng.org/admin/installation-searxng.html#installation-basic)

Herein you will find some hints and suggestions about typical architectures of SearXNG infrastructures.
## uWSGI Setup
We start with a _reference_ setup for public SearXNG instances which can be build up and maintained by the scripts from our [DevOps tooling box](https://docs.searxng.org/utils/index.html#toolboxing).
```
digraph G {

  node [style=filled, shape=box, fillcolor="#ffffcc", fontname=Sans];
  edge [fontname="Sans"];

  browser [label="browser", shape=tab, fillcolor=aliceblue];
  rp      [label="reverse proxy"];
  static  [label="static files", shape=folder, href="url to configure static files", fillcolor=lightgray];
  uwsgi   [label="uwsgi", shape=parallelogram href="https://docs.searxng.org/utils/searxng.sh.html"]
  valkey  [label="valkey DB", shape=cylinder];

  searxng1  [label="SearXNG #1", fontcolor=blue3];
  searxng2  [label="SearXNG #2", fontcolor=blue3];
  searxng3  [label="SearXNG #3", fontcolor=blue3];
  searxng4  [label="SearXNG #4", fontcolor=blue3];

  browser -> rp [label="HTTPS"]

  subgraph cluster_searxng {
      label = "SearXNG instance" fontname=Sans;
      bgcolor="#fafafa";
      { rank=same; static rp };
      rp -> static  [label="optional: reverse proxy serves static files", fillcolor=slategray, fontcolor=slategray];
      rp -> uwsgi [label="http:// (tcp) or unix:// (socket)"];
      uwsgi -> searxng1 -> valkey;
      uwsgi -> searxng2 -> valkey;
      uwsgi -> searxng3 -> valkey;
      uwsgi -> searxng4 -> valkey;
  }

}

```

Fig. 2 Reference architecture of a public SearXNG setup.
The reference installation activates `server.limiter` and `server.image_proxy` ([/etc/searxng/settings.yml](https://github.com/searxng/searxng/blob/master/utils/templates/etc/searxng/settings.yml))
```
# SearXNG settings

use_default_settings: true

general:
  debug: false
  instance_name: "SearXNG"

search:
  safe_search: 2
  autocomplete: 'duckduckgo'
  formats:
    - html

server:
  # Is overwritten by ${SEARXNG_SECRET}
  secret_key: "ultrasecretkey"
  limiter: true
  image_proxy: true
  # public URL of the instance, to ensure correct inbound links. Is overwritten
  # by ${SEARXNG_BASE_URL}.
  # base_url: http://example.com/location

valkey:
  # URL to connect valkey database. Is overwritten by ${SEARXNG_VALKEY_URL}.
  url: valkey://localhost:6379/0

```
