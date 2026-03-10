<!-- source: https://docs.searxng.org/admin/settings/settings_plugins.html -->

#  `plugins:`
Attention
The `enabled_plugins:` section in SearXNG’s settings no longer exists. There is no longer a distinction between built-in and external plugin, all plugins are registered via the settings in the `plugins:` section.
Further reading ..
In SearXNG, plugins can be registered in the [`PluginStore`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginStorage "searx.plugins.PluginStorage") via a fully qualified class name.
A configuration ([`PluginCfg`](https://docs.searxng.org/dev/plugins/development.html#searx.plugins.PluginCfg "searx.plugins.PluginCfg")) can be transferred to the plugin, e.g. to activate it by default / _opt-in_ or _opt-out_ from user’s point of view.
Please note that some plugins, such as the [Hostnames](https://docs.searxng.org/dev/plugins/hostnames.html#hostnames-plugin) plugin, require further configuration before they can be made available for selection.
By default the [built-in plugins](https://docs.searxng.org/admin/settings/settings_plugins.html#settings-built-in-plugins) are loaded. To change the list of plugins to be loaded, the value for `plugins:` in `/etc/searxng/settings.yml` must be overwritten.
Following is an example that uses [use_default_settings](https://docs.searxng.org/admin/settings/settings.html#settings-use-default-settings) and only two plugins are registered: the calculator can be activated by the user and the unit converter is active by default.
```
use_default_settings: true

plugins:

  searx.plugins.calculator.SXNGPlugin:
    active: false

  searx.plugins.unit_converter.SXNGPlugin:
    active: true

```

To prevent any plugins from loading, the following setting can be used:
```
use_default_settings: true

plugins: {}

```

## built-in plugins
The built-in plugins are all located in the namespace searx.plugins.
```
plugins:

  searx.plugins.calculator.SXNGPlugin:
    active: true

  searx.plugins.infinite_scroll.SXNGPlugin:
    active: false

  searx.plugins.hash_plugin.SXNGPlugin:
    active: true

  searx.plugins.self_info.SXNGPlugin:
    active: true

  searx.plugins.tracker_url_remover.SXNGPlugin:
    active: true

  searx.plugins.unit_converter.SXNGPlugin:
    active: true

  searx.plugins.ahmia_filter.SXNGPlugin:
    active: true

  searx.plugins.hostnames.SXNGPlugin:
    active: true

  searx.plugins.oa_doi_rewrite.SXNGPlugin:
    active: false

  searx.plugins.tor_check.SXNGPlugin:
    active: false

```

## external plugins
SearXNG supports _external plugins_ / there is no need to install one, SearXNG runs out of the box.
  * [Only show green hosted results](https://github.com/return42/tgwf-searx-plugins/)
