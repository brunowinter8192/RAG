<!-- source: https://docs.searxng.org/admin/installation-searxng.html -->

# Step by step installation
In this section we show the setup of a SearXNG instance that will be installed by the [Installation Script](https://docs.searxng.org/admin/installation-scripts.html#installation-scripts).
## Install packages
Ubuntu / debianArch LinuxFedora / RHEL
```
$ sudo -H apt-get install -y \
    python3-dev python3-babel python3-venv python-is-python3 \
    uwsgi uwsgi-plugin-python3 \
    git build-essential libxslt-dev zlib1g-dev libffi-dev libssl-dev

```

```
$ sudo -H pacman -S --noconfirm \
    python python-pip python-lxml python-babel \
    uwsgi uwsgi-plugin-python \
    git base-devel libxml2

```

```
$ sudo -H dnf install -y \
    python python-pip python-lxml python-babel python3-devel \
    uwsgi uwsgi-plugin-python3 \
    git @development-tools libxml2 openssl

```

Hint
This installs also the packages needed by [uWSGI](https://docs.searxng.org/admin/installation-uwsgi.html#searxng-uwsgi)
## Create user
bash
```
$ sudo -H useradd --shell /bin/bash --system \
    --home-dir "/usr/local/searxng" \
    --comment 'Privacy-respecting metasearch engine' \
    searxng

$ sudo -H mkdir "/usr/local/searxng"
$ sudo -H chown -R "searxng:searxng" "/usr/local/searxng"

```

## Install SearXNG & dependencies
Start a interactive shell from new created user and clone SearXNG:
bash
```
$ sudo -H -u searxng -i
(searxng)$ git clone "https://github.com/searxng/searxng" \
                   "/usr/local/searxng/searxng-src"

```

In the same shell create _virtualenv_ :
bash
```
(searxng)$ python3 -m venv "/usr/local/searxng/searx-pyenv"
(searxng)$ echo ". /usr/local/searxng/searx-pyenv/bin/activate" \
                   >>  "/usr/local/searxng/.profile"

```

To install SearXNG’s dependencies, exit the SearXNG _bash_ session you opened above and start a new one. Before installing, check if your _virtualenv_ was sourced from the login (_~/.profile_):
bash
```
$ sudo -H -u searxng -i

(searxng)$ command -v python && python --version
/usr/local/searxng/searx-pyenv/bin/python
Python 3.11.10

# update pip's boilerplate ..
pip install -U pip
pip install -U setuptools
pip install -U wheel
pip install -U pyyaml
pip install -U msgspec

# jump to SearXNG's working tree and install SearXNG into virtualenv
(searxng)$ cd "/usr/local/searxng/searxng-src"
(searxng)$ pip install --use-pep517 --no-build-isolation -e .

```

Tip
Open a second terminal for the configuration tasks and leave the `(searx)$` terminal open for the tasks below.
## Configuration
`use_default_settings: True`
  * [/etc/searxng/settings.yml](https://github.com/searxng/searxng/blob/master/utils/templates/etc/searxng/settings.yml)

To create a initial `/etc/searxng/settings.yml` we recommend to start with a copy of the file [git://utils/templates/etc/searxng/settings.yml](https://github.com/searxng/searxng/blob/master/utils/templates/etc/searxng/settings.yml). This setup [use default settings](https://docs.searxng.org/admin/settings/settings.html#settings-use-default-settings) from [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml) and is shown in the tab _“Use default settings”_ below. This setup:
  * enables [limiter](https://docs.searxng.org/admin/searx.limiter.html#limiter) to protect against bots
  * enables [image proxy](https://docs.searxng.org/admin/settings/settings_server.html#image-proxy) for better privacy

Modify the `/etc/searxng/settings.yml` to your needs:
Use default settingssearx/settings.yml
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

To see the entire file jump to [git://utils/templates/etc/searxng/settings.yml](https://github.com/searxng/searxng/blob/master/utils/templates/etc/searxng/settings.yml)
```
general:
  # Debug mode, only for development. Is overwritten by ${SEARXNG_DEBUG}
  debug: false
  # displayed name
  instance_name: "SearXNG"
  # For example: https://example.com/privacy
  privacypolicy_url: false
  # use true to use your own donation page written in searx/info/en/donate.md
  # use false to disable the donation link
  donation_url: false
  # mailto:contact@example.com
  contact_url: false
  # record stats
  enable_metrics: true
  # expose stats in open metrics format at /metrics
  # leave empty to disable (no password set)
  # open_metrics: <password>
  open_metrics: ''

brand:
  new_issue_url: https://github.com/searxng/searxng/issues/new
  docs_url: https://docs.searxng.org/
  public_instances: https://searx.space
  wiki_url: https://github.com/searxng/searxng/wiki
  issue_url: https://github.com/searxng/searxng/issues
  # custom:
  #   # Custom entries in the footer: [title]: [link]
  #   links:
  #     Uptime: https://uptime.searxng.org/history/darmarit-org
  #     About: "https://searxng.org"

search:
  # Filter results. 0: None, 1: Moderate, 2: Strict
  safe_search: 0
  # Existing autocomplete backends: "360search", "baidu", "bing", "brave", "dbpedia", "duckduckgo", "google",
  # "yandex", "mwmbl", "naver", "seznam", "sogou", "startpage", "swisscows", "quark", "qwant", "wikipedia" -
  # leave blank to turn it off by default.
  autocomplete: ""
  # minimun characters to type before autocompleter starts
  autocomplete_min: 4
  # backend for the favicon near URL in search results.
  # Available resolvers: "allesedv", "duckduckgo", "google", "yandex" - leave blank to turn it off by default.
  favicon_resolver: ""
  # Default search language - leave blank to detect from browser information or
  # use codes from 'languages.py'
  default_lang: "auto"
  # max_page: 0  # if engine supports paging, 0 means unlimited numbers of pages
  # Available languages
  # languages:
  #   - all
  #   - en
  #   - en-US
  #   - de
  #   - it-IT
  #   - fr
  #   - fr-BE
  # ban time in seconds after engine errors
  ban_time_on_fail: 5
  # max ban time in seconds after engine errors
  max_ban_time_on_fail: 120
  suspended_times:
    # Engine suspension time after error (in seconds; set to 0 to disable)
    # For error "Access denied" and "HTTP error [402, 403]"
    SearxEngineAccessDenied: 180
    # For error "CAPTCHA"
    SearxEngineCaptcha: 3600
    # For error "Too many request" and "HTTP error 429"
    SearxEngineTooManyRequests: 180
    # Cloudflare CAPTCHA
    cf_SearxEngineCaptcha: 1296000
    cf_SearxEngineAccessDenied: 86400
    # ReCAPTCHA
    recaptcha_SearxEngineCaptcha: 604800

  # remove format to deny access, use lower case.
  # formats: [html, csv, json, rss]
  formats:
    - html

server:
  # Is overwritten by ${SEARXNG_PORT} and ${SEARXNG_BIND_ADDRESS}
  port: 8888
  bind_address: "127.0.0.1"
  # public URL of the instance, to ensure correct inbound links. Is overwritten
  # by ${SEARXNG_BASE_URL}.
  base_url: false  # "http://example.com/location"
  # rate limit the number of request on the instance, block some bots.
  # Is overwritten by ${SEARXNG_LIMITER}
  limiter: false
  # enable features designed only for public instances.
  # Is overwritten by ${SEARXNG_PUBLIC_INSTANCE}
  public_instance: false

  # If your instance owns a /etc/searxng/settings.yml file, then set the following
  # values there.

  secret_key: "ultrasecretkey"  # Is overwritten by ${SEARXNG_SECRET}
  # Proxy image results through SearXNG. Is overwritten by ${SEARXNG_IMAGE_PROXY}
  image_proxy: false
  # 1.0 and 1.1 are supported
  http_protocol_version: "1.0"
  # POST queries are "more secure!" but are also the source of hard-to-locate
  # annoyances, which is why GET may be better for end users and their browsers.
  # see https://github.com/searxng/searxng/pull/3619
  # Is overwritten by ${SEARXNG_METHOD}
  method: "POST"
  default_http_headers:
    X-Content-Type-Options: nosniff
    X-Download-Options: noopen
    X-Robots-Tag: noindex, nofollow
    Referrer-Policy: no-referrer

valkey:
  # URL to connect valkey database. Is overwritten by ${SEARXNG_VALKEY_URL}.
  # https://docs.searxng.org/admin/settings/settings_valkey.html#settings-valkey
  # url: valkey://localhost:6379/0
  url: false

ui:
  # Custom static path - leave it blank if you didn't change
  static_path: ""
  # Custom templates path - leave it blank if you didn't change
  templates_path: ""
  # query_in_title: When true, the result page's titles contains the query
  # it decreases the privacy, since the browser can records the page titles.
  query_in_title: false
  # ui theme
  default_theme: simple
  # center the results ?
  center_alignment: false
  # URL prefix of the internet archive, don't forget trailing slash (if needed).
  # cache_url: "https://webcache.googleusercontent.com/search?q=cache:"
  # Default interface locale - leave blank to detect from browser information or
  # use codes from the 'locales' config section
  default_locale: ""
  # Open result links in a new tab by default
  # results_on_new_tab: false
  theme_args:
    # style of simple theme: auto, light, dark, black
    simple_style: auto
  # Perform search immediately if a category selected.
  # Disable to select multiple categories at once and start the search manually.
  search_on_category_select: true
  # Hotkeys: default or vim
  hotkeys: default
  # URL formatting: pretty, full or host
  url_formatting: pretty

# Lock arbitrary settings on the preferences page.
#
# preferences:
#   lock:
#     - categories
#     - language
#     - autocomplete
#     - favicon
#     - safesearch
#     - method
#     - doi_resolver
#     - locale
#     - theme
#     - results_on_new_tab
#     - search_on_category_select
#     - method
#     - image_proxy
#     - query_in_title

# communication with search engines
#
outgoing:
  # default timeout in seconds, can be override by engine
  request_timeout: 3.0
  # the maximum timeout in seconds
  # max_request_timeout: 10.0
  # suffix of searxng_useragent, could contain information like an email address
  # to the administrator
  useragent_suffix: ""
  # The maximum number of concurrent connections that may be established.
  pool_connections: 100
  # Allow the connection pool to maintain keep-alive connections below this
  # point.
  pool_maxsize: 20
  # See https://www.python-httpx.org/http2/
  enable_http2: true
  # uncomment below section if you want to use a custom server certificate
  # see https://www.python-httpx.org/advanced/#changing-the-verification-defaults
  # and https://www.python-httpx.org/compatibility/#ssl-configuration
  #  verify: ~/.mitmproxy/mitmproxy-ca-cert.cer
  #
  # uncomment below section if you want to use a proxyq see: SOCKS proxies
  #   https://2.python-requests.org/en/latest/user/advanced/#proxies
  # are also supported: see
  #   https://2.python-requests.org/en/latest/user/advanced/#socks
  #
  #  proxies:
  #    all://:
  #      - http://proxy1:8080
  #      - http://proxy2:8080
  #
  #  using_tor_proxy: true
  #
  # Extra seconds to add in order to account for the time taken by the proxy
  #
  #  extra_proxy_timeout: 10
  #
  # uncomment below section only if you have more than one network interface
  # which can be the source of outgoing search requests
  #
  #  source_ips:
  #    - 1.1.1.1
  #    - 1.1.1.2
  #    - fe80::/126

# Plugin configuration, for more details see
#   https://docs.searxng.org/admin/settings/settings_plugins.html
#
plugins:

  searx.plugins.calculator.SXNGPlugin:
    active: true

  searx.plugins.infinite_scroll.SXNGPlugin:
    active: false

  searx.plugins.hash_plugin.SXNGPlugin:
    active: true

  searx.plugins.self_info.SXNGPlugin:
    active: true

  searx.plugins.unit_converter.SXNGPlugin:
    active: true

  searx.plugins.ahmia_filter.SXNGPlugin:
    active: true

  searx.plugins.hostnames.SXNGPlugin:
    active: true

  searx.plugins.time_zone.SXNGPlugin:
    active: true

  searx.plugins.oa_doi_rewrite.SXNGPlugin:
    active: false

  searx.plugins.tor_check.SXNGPlugin:
    active: false

  searx.plugins.tracker_url_remover.SXNGPlugin:
    active: true

# Configuration of the "Hostnames plugin":
#

```

To see the entire file jump to [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml)
For a _minimal setup_ you need to set `server:secret_key`.
Use default settingsminimal setup
```
$ sudo -H mkdir -p "/etc/searxng"
$ sudo -H cp "/usr/local/searxng/searxng-src/utils/templates/etc/searxng/settings.yml" \
             "/etc/searxng/settings.yml"

```

```
$ sudo -H sed -i -e "s/ultrasecretkey/$(openssl rand -hex 16)/g" \
              "/etc/searxng/settings.yml"

```

## Check
To check your SearXNG setup, optional enable debugging and start the _webapp_. SearXNG looks at the exported environment `$SEARXNG_SETTINGS_PATH` for a configuration file.
bash
```
# enable debug ..
$ sudo -H sed -i -e "s/debug : False/debug : True/g" "/etc/searxng/settings.yml"

# start webapp
$ sudo -H -u searxng -i
(searxng)$ cd /usr/local/searxng/searxng-src
(searxng)$ export SEARXNG_SETTINGS_PATH="/etc/searxng/settings.yml"
(searxng)$ python searx/webapp.py

# disable debug
$ sudo -H sed -i -e "s/debug : True/debug : False/g" "/etc/searxng/settings.yml"

```

Open WEB browser and visit <http://127.0.0.1:8888> . If you are inside a container or in a script, test with curl:
WEB browsercurl
```
$ xdg-open http://127.0.0.1:8888

```

```
$ curl --location --verbose --head --insecure 127.0.0.1:8888

*   Trying 127.0.0.1:8888...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 8888 (#0)
> HEAD / HTTP/1.1
> Host: 127.0.0.1:8888
> User-Agent: curl/7.68.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
HTTP/1.0 200 OK
...

```

If everything works fine, hit `[CTRL-C]` to stop the _webapp_ and disable the debug option in `settings.yml`. You can now exit SearXNG user bash session (enter exit command twice). At this point SearXNG is not demonized; uwsgi allows this.
