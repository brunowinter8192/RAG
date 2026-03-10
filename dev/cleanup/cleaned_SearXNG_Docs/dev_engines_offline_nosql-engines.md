<!-- source: https://docs.searxng.org/dev/engines/offline/nosql-engines.html -->

# NoSQL databases
**Further reading:**
  * [NoSQL databases](https://en.wikipedia.org/wiki/NoSQL)
  * [valkey.io](https://valkey.io/)
  * [MongoDB](https://www.mongodb.com)

> **Info:**
Initial sponsored by [Search and Discovery Fund](https://nlnet.nl/discovery) of [NLnet Foundation](https://nlnet.nl/).
The following [NoSQL databases](https://en.wikipedia.org/wiki/NoSQL) are supported:
All of the engines above are just commented out in the [settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml), as you have to set various options and install dependencies before using them.
By default, the engines use the `key-value` template for displaying results / see [simple](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/key-value.html) theme. If you are not satisfied with the original result layout, you can use your own template, set `result_template` attribute to `{template_name}` and place the templates at:
```
searx/templates/{theme_name}/result_templates/{template_name}

```

Furthermore, if you do not wish to expose these engines on a public instance, you can still add them and limit the access by setting `tokens` as described in section [Private Engines (tokens)](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines).
## Extra Dependencies
For using [Valkey Server](https://docs.searxng.org/dev/engines/offline/nosql-engines.html#engine-valkey-server) or [MongoDB](https://docs.searxng.org/dev/engines/offline/nosql-engines.html#engine-mongodb) you need to install additional packages in Python’s Virtual Environment of your SearXNG instance. To switch into the environment ([Install SearXNG & dependencies](https://docs.searxng.org/admin/installation-searxng.html#searxng-src)) you can use [utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh):
```
$ sudo utils/searxng.sh instance cmd bash
(searxng-pyenv)$ pip install ...

```

## Configure the engines
[NoSQL databases](https://en.wikipedia.org/wiki/NoSQL) are used for storing arbitrary data without first defining their structure.
### Valkey Server
> **Info:**
  * `pip install` [valkey](https://github.com/andymccurdy/valkey-py#installation)
  * [valkey.io](https://valkey.io/)
  * [valkey_server.py](https://github.com/searxng/searxng/blob/master/searx/engines/valkey_server.py)

Valkey is an open source (BSD licensed), in-memory data structure (key value based) store. Before configuring the `valkey_server` engine, you must install the dependency [valkey](https://github.com/andymccurdy/valkey-py#installation).
#### Configuration
Select a database to search in and set its index in the option `db`. You can either look for exact matches or use partial keywords to find what you are looking for by configuring `exact_match_only`.
#### Example
Below is an example configuration:
```
# Required dependency: valkey

- name: myvalkey
  shortcut : rds
  engine: valkey_server
  exact_match_only: false
  host: '127.0.0.1'
  port: 6379
  enable_http: true
  password: ''
  db: 0

```

#### Implementations
### MongoDB
> **Info:**
  * `pip install` [pymongo](https://github.com/mongodb/mongo-python-driver#installation)
  * [MongoDB](https://www.mongodb.com)
  * [mongodb.py](https://github.com/searxng/searxng/blob/master/searx/engines/mongodb.py)

[MongoDB](https://www.mongodb.com) is a document based database program that handles JSON like data. Before configuring the `mongodb` engine, you must install the dependency [pymongo](https://github.com/mongodb/mongo-python-driver#installation).
#### Configuration
In order to query [MongoDB](https://www.mongodb.com), you have to select a `database` and a `collection`. Furthermore, you have to select a `key` that is going to be searched. [MongoDB](https://www.mongodb.com) also supports the option `exact_match_only`, so configure it as you wish.
#### Example
Below is an example configuration for using a MongoDB collection:
```
# MongoDB engine
# Required dependency: pymongo

- name: mymongo
  engine: mongodb
  shortcut: md
  exact_match_only: false
  host: '127.0.0.1'
  port: 27017
  enable_http: true
  results_per_page: 20
  database: 'business'
  collection: 'reviews'  # name of the db collection
  key: 'name'            # key in the collection to search for

```

#### Implementations
