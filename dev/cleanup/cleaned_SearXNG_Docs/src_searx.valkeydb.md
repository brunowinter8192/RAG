<!-- source: https://docs.searxng.org/src/searx.valkeydb.html -->

# Valkey DB
Implementation of the valkey client ([valkey-py](https://github.com/valkey-io/valkey-py)).
This implementation uses the [valkey:](https://docs.searxng.org/admin/settings/settings_valkey.html#settings-valkey) setup from `settings.yml`. A valkey DB connect can be tested by:
```
>>> from searx import valkeydb
>>> valkeydb.initialize()
True
>>> db = valkeydb.client()
>>> db.set("foo", "bar")
True
>>> db.get("foo")
b'bar'
>>>

```

searx.valkeydb.client() → [Valkey](https://valkey-py.readthedocs.io/en/stable/connections.html#valkey.Valkey "\(in valkey-py v99.99.99\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns SearXNG’s global Valkey DB connector (Valkey client object).
