<!-- source: https://docs.searxng.org/admin/settings/settings.html -->

#  `settings.yml`
This page describe the options possibilities of the [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml) file.
Further reading ..
## settings.yml location
The initial `settings.yml` we be load from these locations:
  1. the full path specified in the `SEARXNG_SETTINGS_PATH` environment variable.
  2. `/etc/searxng/settings.yml`

If these files don’t exist (or are empty or can’t be read), SearXNG uses the [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml) file. Read [use_default_settings](https://docs.searxng.org/admin/settings/settings.html#settings-use-default-settings) to see how you can simplify your _user defined_ `settings.yml`.
## use_default_settings
`use_default_settings: true`
  * [/etc/searxng/settings.yml](https://github.com/searxng/searxng/blob/master/utils/templates/etc/searxng/settings.yml)

The user defined `settings.yml` is loaded from the [settings.yml location](https://docs.searxng.org/admin/settings/settings.html#settings-location) and can relied on the default configuration [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml) using:
> `use_default_settings: true` 

`server:`
    
In the following example, the actual settings are the default settings defined in [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml) with the exception of the `secret_key` and the `bind_address`:
```
use_default_settings: true
server:
    secret_key: "ultrasecretkey"   # change this!
    bind_address: "[::]"

```

`engines:`
    
With `use_default_settings: true`, each settings can be override in a similar way, the `engines` section is merged according to the engine `name`. In this example, SearXNG will load all the default engines, will enable the `bing` engine and define a [token](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines) for the arch linux engine:
```
use_default_settings: true
server:
  secret_key: "ultrasecretkey"   # change this!
engines:
  - name: arch linux wiki
    tokens: ['$ecretValue']
  - name: bing
    disabled: false

```

`engines:` / `remove:` 
    
It is possible to remove some engines from the default settings. The following example is similar to the above one, but SearXNG doesn’t load the the google engine:
```
use_default_settings:
  engines:
    remove:
      - google
server:
  secret_key: "ultrasecretkey"   # change this!
engines:
  - name: arch linux wiki
    tokens: ['$ecretValue']

```

`engines:` / `keep_only:` 
    
As an alternative, it is possible to specify the engines to keep. In the following example, SearXNG has only two engines:
```
use_default_settings:
  engines:
    keep_only:
      - google
      - duckduckgo
server:
  secret_key: "ultrasecretkey"   # change this!
engines:
  - name: google
    tokens: ['$ecretValue']
  - name: duckduckgo
    tokens: ['$ecretValue']

```
