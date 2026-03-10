<!-- source: https://docs.searxng.org/admin/settings/settings_valkey.html -->

#  `valkey:`
A [Valkey](https://valkey.io) DB can be connected by an URL, in section [Valkey DB](https://docs.searxng.org/src/searx.valkeydb.html#valkey-db) you will find a description to test your valkey connection in SearXNG. 

`url``$SEARXNG_VALKEY_URL` 
    
URL to connect valkey database. [There are several ways to specify a database number](https://valkey-py.readthedocs.io/en/stable/connections.html#valkey.Valkey.from_url):
```
valkey://[[username]:[password]]@localhost:6379/0
valkeys://[[username]:[password]]@localhost:6379/0
unix://[[username]:[password]]@/path/to/socket.sock?db=0

```

When using sockets, don’t forget to check the access rights on the socket:
```
ls -la /usr/local/searxng-valkey/run/valkey.sock
srwxrwx--- 1 searxng-valkey searxng-valkey ... /usr/local/searxng-valkey/run/valkey.sock

```

In this example read/write access is given to the _searxng-valkey_ group. To get access rights to valkey instance (the socket), your SearXNG (or even your developer) account needs to be added to the _searxng-valkey_ group.
## Valkey Developer Notes
To set up a local [Valkey](https://valkey.io) DB, set the URL connector in your YAML setting:
```
valkey:
  url: valkey://localhost:6379/0

```

To install a local [Valkey](https://valkey.io) DB from package manager read [Valkey-Installation](https://valkey.io/topics/installation/) or use:
```
$ ./utils/searxng.sh install valkey
# restart your SearXNG instance

```
