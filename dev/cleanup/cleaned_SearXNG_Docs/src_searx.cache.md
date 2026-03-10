<!-- source: https://docs.searxng.org/src/searx.cache.html -->

# Caches
Implementation of caching solutions.
  * [`searx.cache.ExpireCache`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCache "searx.cache.ExpireCache") and its [`searx.cache.ExpireCacheCfg`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg "searx.cache.ExpireCacheCfg")

* * * 

_class_ searx.cache.ExpireCacheCfg(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _db_url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")=''_, _MAX_VALUE_LEN :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=10240_, _MAXHOLD_TIME :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=604800_, _MAINTENANCE_PERIOD :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=3600_, _MAINTENANCE_MODE :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['auto','off']='auto'_, _password :[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")=b'ultrasecretkey'_) 
    
Configuration of a [`ExpireCache`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCache "searx.cache.ExpireCache") cache. 

name _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the cache. 

db_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
URL of the SQLite DB, the path to the database file. If unset a default DB will be created in /tmp/sxng_cache_{self.name}.db 

MAX_VALUE_LEN _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Max length of a _serialized_ value. 

MAXHOLD_TIME _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Hold time (default in sec.), after which a value is removed from the cache. 

MAINTENANCE_PERIOD _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Maintenance period in seconds / when [`MAINTENANCE_MODE`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.MAINTENANCE_MODE "searx.cache.ExpireCacheCfg.MAINTENANCE_MODE") is set to `auto`. 

MAINTENANCE_MODE _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['auto','off']_ 
    
Type of maintenance mode 

`auto`:
    
Maintenance is carried out automatically as part of the maintenance intervals ([`MAINTENANCE_PERIOD`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.MAINTENANCE_PERIOD "searx.cache.ExpireCacheCfg.MAINTENANCE_PERIOD")); no external process is required. 

`off`:
    
Maintenance is switched off and must be carried out by an external process if required. 

password _:[ bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")_ 
    
Password used by [`ExpireCache.secret_hash`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCache.secret_hash "searx.cache.ExpireCache.secret_hash").
The default password is taken from [secret_key](https://docs.searxng.org/admin/settings/settings_server.html#server-secret-key). When the password is changed, the hashed keys in the cache can no longer be used, which is why all values in the cache are deleted when the password is changed. 

_class_ searx.cache.ExpireCacheStats(_cached_items :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"),[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]]]_) 
    
Dataclass which provides information on the status of the cache. 

cached_items _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"),[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]]]_ 
    
Values in the cache mapped by context name. 

_class_ searx.cache.ExpireCache 
    
Abstract base class for the implementation of a key/value cache with expire date. 

_abstractmethod_ set(_key :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _value :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_, _expire :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _ctx :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Set _key_ to _value_. To set a timeout on key use argument `expire` (in sec.). If expire is unset the default is taken from [`ExpireCacheCfg.MAXHOLD_TIME`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.MAXHOLD_TIME "searx.cache.ExpireCacheCfg.MAXHOLD_TIME"). After the timeout has expired, the key will automatically be deleted.
The `ctx` argument specifies the context of the `key`. A key is only unique in its context.
The concrete implementations of this abstraction determine how the context is mapped in the connected database. In SQL databases, for example, the context is a DB table or in a Key/Value DB it could be a prefix for the key.
If the context is not specified (the default is `None`) then a default context should be used, e.g. a default table for SQL databases or a default prefix in a Key/Value DB. 

_abstractmethod_ get(_key :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _default :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")=None_, _ctx :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Return _value_ of _key_. If key is unset, `None` is returned. 

_abstractmethod_ maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_, _truncate :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Performs maintenance on the cache. 

`force`:
    
Maintenance should be carried out even if the maintenance interval has not yet been reached. 

`truncate`:
    
Truncate the entire cache, which is necessary, for example, if the password has changed. 

_abstractmethod_ state() → [ExpireCacheStats](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheStats "searx.cache.ExpireCacheStats") 
    
Returns a [`ExpireCacheStats`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheStats "searx.cache.ExpireCacheStats"), which provides information about the status of the cache. 

_static_ build_cache(_cfg :[ExpireCacheCfg](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg "searx.cache.ExpireCacheCfg")_) → [ExpireCacheSQLite](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheSQLite "searx.cache.ExpireCacheSQLite") 
    
Factory to build a caching instance.
Note
Currently, only the SQLite adapter is available, but other database types could be implemented in the future, e.g. a Valkey (Redis) adapter. 

_static_ normalize_name(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Returns a normalized name that can be used as a file name or as a SQL table name (is used, for example, to normalize the context name). 

secret_hash(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Creates a hash of the argument `name`. The hash value is formed from the `name` combined with the [`password`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.password "searx.cache.ExpireCacheCfg.password"). Can be used, for example, to make the `key` stored in the DB unreadable for third parties. 

_class_ searx.cache.ExpireCacheSQLite(_cfg :[ExpireCacheCfg](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg "searx.cache.ExpireCacheCfg")_) 
    
Cache that manages key/value pairs in a SQLite DB. The DB model in the SQLite DB is implemented in abstract class [`SQLiteAppl`](https://docs.searxng.org/src/searx.sqlitedb.html#searx.sqlitedb.SQLiteAppl "searx.sqlitedb.SQLiteAppl").
The following configurations are required / supported:
DB_SCHEMA _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ _= 1_ 
    
As soon as changes are made to the DB schema, the version number must be increased. Changes to the version number require the DB to be recreated (or migrated / if an migration path exists and is implemented). 

init(_conn :[Connection](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initializes the DB schema and properties, is only executed once even if called several times.
If the initialization has not yet taken place, it is carried out and a True is returned to the caller at the end. If the initialization has already been carried out in the past, False is returned. 

maintenance(_force :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_, _truncate :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Performs maintenance on the cache. 

`force`:
    
Maintenance should be carried out even if the maintenance interval has not yet been reached. 

`truncate`:
    
Truncate the entire cache, which is necessary, for example, if the password has changed. 

create_table(_table :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Create DB `table` if it has not yet been created, no recreates are initiated if the table already exists. 

_property_ table_names _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of key/value tables already created in the DB. 

_property_ next_maintenance_time _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_ 
    
Returns (unix epoch) time of the next maintenance. 

set(_key :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _value :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_, _expire :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_, _ctx :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Set key/value in DB table given by argument `ctx`. If expire is unset the default is taken from [`ExpireCacheCfg.MAXHOLD_TIME`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.MAXHOLD_TIME "searx.cache.ExpireCacheCfg.MAXHOLD_TIME"). If `ctx` argument is `None` (the default), a table name is generated from the [`ExpireCacheCfg.name`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.name "searx.cache.ExpireCacheCfg.name"). If DB table does not exists, it will be created (on demand) by [`self.create_table`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheSQLite.create_table "searx.cache.ExpireCacheSQLite.create_table"). 

setmany(_opt_list :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"),[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]]_, _ctx :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") 
    
Efficient bootload of the cache from a list of options. The list contains tuples with the arguments described in [`ExpireCacheSQLite.set`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheSQLite.set "searx.cache.ExpireCacheSQLite.set"). 

get(_key :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _default :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")=None_, _ctx :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)") 
    
Get value of `key` from table given by argument `ctx`. If `ctx` argument is `None` (the default), a table name is generated from the [`ExpireCacheCfg.name`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.name "searx.cache.ExpireCacheCfg.name"). If `key` not exists (in table), the `default` value is returned. 

pairs(_ctx :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [Iterator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator "\(in Python v3.14\)")[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]] 
    
Iterate over key/value pairs from table given by argument `ctx`. If `ctx` argument is `None` (the default), a table name is generated from the [`ExpireCacheCfg.name`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheCfg.name "searx.cache.ExpireCacheCfg.name"). 

state() → [ExpireCacheStats](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheStats "searx.cache.ExpireCacheStats") 
    
Returns a [`ExpireCacheStats`](https://docs.searxng.org/src/searx.cache.html#searx.cache.ExpireCacheStats "searx.cache.ExpireCacheStats"), which provides information about the status of the cache.
