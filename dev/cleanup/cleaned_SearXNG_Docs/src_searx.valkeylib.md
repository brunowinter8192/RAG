<!-- source: https://docs.searxng.org/src/searx.valkeylib.html -->

# Valkey Library
A collection of convenient functions and valkey/lua scripts.
This code was partial inspired by the [Bullet-Proofing Lua Scripts in ValkeyPy](https://redis.com/blog/bullet-proofing-lua-scripts-in-redispy/) article. 

**valkeylib.LUA_SCRIPT_STORAGE** = `{}`
A global dictionary to cache client’s `Script` objects, used by [`lua_script_storage`](https://docs.searxng.org/src/searx.valkeylib.html#searx.valkeylib.lua_script_storage "searx.valkeylib.lua_script_storage") 

**valkeylib.lua_script_storage(_client_ , _script_)**
Returns a valkey [`Script`](https://valkey-py.readthedocs.io/en/stable/commands.html#valkey.commands.core.CoreCommands.register_script "\(in valkey-py v99.99.99\)") instance.
Due to performance reason the `Script` object is instantiated only once for a client (`client.register_script(..)`) and is cached in [`LUA_SCRIPT_STORAGE`](https://docs.searxng.org/src/searx.valkeylib.html#searx.valkeylib.LUA_SCRIPT_STORAGE "searx.valkeylib.LUA_SCRIPT_STORAGE"). 

searx.valkeylib.purge_by_prefix(_client_ , _prefix :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='SearXNG_'_) 
    
Purge all keys with `prefix` from database.
Queries all keys in the database by the given prefix and set expire time to zero. The default prefix will drop all keys which has been set by SearXNG (drops SearXNG schema entirely from database).
The implementation is the lua script from string `PURGE_BY_PREFIX`. The lua script uses [EXPIRE](https://valkey.io/commands/expire/) instead of [DEL](https://valkey.io/commands/del/): if there are a lot keys to delete and/or their values are big, DEL could take more time and blocks the command loop while EXPIRE turns back immediate. 

Parameters: 
    
**prefix** – prefix of the key to delete (default: `SearXNG_`) 

searx.valkeylib.secret_hash(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Creates a hash of the `name`.
Combines argument `name` with the `secret_key` from [server:](https://docs.searxng.org/admin/settings/settings_server.html#settings-server). This function can be used to get a more anonymized name of a Valkey KEY. 

Parameters: 
    
**name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – the name to create a secret hash for 

searx.valkeylib.incr_counter(_client_ , _name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _limit :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=0_, _expire :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=0_) 
    
Increment a counter and return the new value.
If counter with valkey key `SearXNG_counter_<name>` does not exists it is created with initial value 1 returned. The replacement `<name>` is a _secret hash_ of the value from argument `name` (see [`secret_hash()`](https://docs.searxng.org/src/searx.valkeylib.html#searx.valkeylib.secret_hash "searx.valkeylib.secret_hash")).
The implementation of the valkey counter is the lua script from string `INCR_COUNTER`. 

Parameters: 
    
  * **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – name of the counter
  * **expire** (int / see [EXPIRE](https://valkey.io/commands/expire/)) – live-time of the counter in seconds (default `None` means infinite).
  * **limit** (int / limit is 2^64 see [INCR](https://valkey.io/commands/incr/)) – limit where the counter stops to increment (default `None`)

Returns: 
    
value of the incremented counter
A simple demo of a counter with expire time and limit:
```
>>> for i in range(6):
...   i, incr_counter(client, "foo", 3, 5) # max 3, duration 5 sec
...   time.sleep(1) # from the third call on max has been reached
...
(0, 1)
(1, 2)
(2, 3)
(3, 3)
(4, 3)
(5, 1)

```

**valkeylib.drop_counter(_client_ , _name_)**
Drop counter with valkey key `SearXNG_counter_<name>`
The replacement `<name>` is a _secret hash_ of the value from argument `name` (see [`incr_counter()`](https://docs.searxng.org/src/searx.valkeylib.html#searx.valkeylib.incr_counter "searx.valkeylib.incr_counter") and [`incr_sliding_window()`](https://docs.searxng.org/src/searx.valkeylib.html#searx.valkeylib.incr_sliding_window "searx.valkeylib.incr_sliding_window")). 

searx.valkeylib.incr_sliding_window(_client_ , _name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _duration :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) 
    
Increment a sliding-window counter and return the new value.
If counter with valkey key `SearXNG_counter_<name>` does not exists it is created with initial value 1 returned. The replacement `<name>` is a _secret hash_ of the value from argument `name` (see [`secret_hash()`](https://docs.searxng.org/src/searx.valkeylib.html#searx.valkeylib.secret_hash "searx.valkeylib.secret_hash")). 

Parameters: 
    
  * **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – name of the counter
  * **duration** – live-time of the sliding window in seconds

Typeduration: 
    
int 

Returns: 
    
value of the incremented counter
The implementation of the valkey counter is the lua script from string `INCR_SLIDING_WINDOW`. The lua script uses [sorted sets in Valkey](https://valkey.com/ebook/part-1-getting-started/chapter-1-getting-to-know-valkey/1-2-what-valkey-data-structures-look-like/1-2-5-sorted-sets-in-valkey/) to implement a sliding window for the valkey key `SearXNG_counter_<name>` ([ZADD](https://valkey.io/commands/zadd/)). The current [TIME](https://valkey.io/commands/time/) is used to score the items in the sorted set and the time window is moved by removing items with a score lower current time minus _duration_ time ([ZREMRANGEBYSCORE](https://valkey.io/commands/zremrangebyscore/)).
The [EXPIRE](https://valkey.io/commands/expire/) time (the duration of the sliding window) is refreshed on each call (increment) and if there is no call in this duration, the sorted set expires from the valkey DB.
The return value is the amount of items in the sorted set ([ZCOUNT](https://valkey.io/commands/zcount/)), what means the number of calls in the sliding window.
A simple demo of the sliding window:
```
>>> for i in range(5):
...   incr_sliding_window(client, "foo", 3) # duration 3 sec
...   time.sleep(1) # from the third call (second) on the window is moved
...
1
2
3
3
3
>>> time.sleep(3)  # wait until expire
>>> incr_sliding_window(client, "foo", 3)
1

```
