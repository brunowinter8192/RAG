<!-- source: https://docs.searxng.org/dev/engines/online/piped.html -->

# Piped
Contents
An alternative privacy-friendly YouTube frontend which is efficient by design. [Piped’s architecture](https://docs.piped.video/docs/architecture/) consists of 3 components:
  * proxy

## Configuration
The [`backend_url`](https://docs.searxng.org/dev/engines/online/piped.html#searx.engines.piped.backend_url "searx.engines.piped.backend_url") and [`frontend_url`](https://docs.searxng.org/dev/engines/online/piped.html#searx.engines.piped.frontend_url "searx.engines.piped.frontend_url") has to be set in the engine named piped and are used by all `piped` engines (unless an individual values for `backend_url` and `frontend_url` are configured for the engine).
```
- name: piped
  engine: piped
  piped_filter: videos
  ...
  frontend_url: https://..
  backend_url:
    - https://..
    - https://..

- name: piped.music
  engine: piped
  network: piped
  shortcut: ppdm
  piped_filter: music_songs
  ...

```

## Known Quirks
The implementation to support [`paging`](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.Engine.paging "searx.enginelib.Engine.paging") is based on the _nextpage_ method of Piped’s REST API / the [`frontend API`](https://docs.searxng.org/dev/engines/online/piped.html#searx.engines.piped.frontend_url "searx.engines.piped.frontend_url"). This feature is _next page driven_ and plays well with the [infinite_scroll](https://docs.searxng.org/admin/settings/settings_plugins.html#settings-plugins) plugin in SearXNG but it does not really fit into SearXNG’s UI to select a page by number.
## Implementations
**engines.piped.backend_url** = `[]`
[Piped-Backend](https://github.com/TeamPiped/Piped-Backend): The core component behind Piped. The value is an URL or a list of URLs. In the latter case instance will be selected randomly. For a complete list of official instances see Piped-Instances ([JSON](https://piped-instances.kavin.rocks/)) 

**engines.piped.frontend_url** = `None`
[Piped-Frontend](https://github.com/TeamPiped/Piped): URL to use as link and for embeds. 

**engines.piped.piped_filter** = `'all'`
Content filter `music_songs` or `videos`
