<!-- source: https://docs.searxng.org/admin/settings/settings_redis.html -->

#  `redis:`
Attention
SearXNG is switching from the Redis DB to [Valkey](https://valkey.io). The configuration description of [Valkey](https://valkey.io) in SearXNG can be found here: [settings](https://docs.searxng.org/admin/settings/settings_valkey.html#settings-valkey).
If you have built and installed a local Redis DB for SearXNG, it is recommended to uninstall it now and replace it with the installation of a [Valkey](https://valkey.io) DB.
## Redis Developer Notes
To uninstall SearXNG’s local Redis DB you can use:
```
# stop your SearXNG instance
$ ./utils/searxng.sh remove.redis

```

Remove the Redis DB in your YAML setting:
```
redis:
  url: unix:///usr/local/searxng-redis/run/redis.sock?db=0

```

To install [Valkey](https://valkey.io) read: [Valkey Developer Notes](https://docs.searxng.org/admin/settings/settings_valkey.html#valkey-developer-notes)
