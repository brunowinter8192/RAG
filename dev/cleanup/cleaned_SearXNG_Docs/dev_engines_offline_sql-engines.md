<!-- source: https://docs.searxng.org/dev/engines/offline/sql-engines.html -->

# SQL Engines
**Further reading:**
  * [SQLite](https://www.sqlite.org/index.html)
  * [PostgreSQL](https://www.postgresql.org)
  * [MySQL](https://www.mysql.com)

> **Info:**
Initial sponsored by [Search and Discovery Fund](https://nlnet.nl/discovery) of [NLnet Foundation](https://nlnet.nl/).
With the _SQL engines_ you can bind SQL databases into SearXNG. The following Relational Database Management System (RDBMS) are supported:
  * [MySQL](https://docs.searxng.org/dev/engines/offline/sql-engines.html#engine-mysql-server) & [MariaDB](https://docs.searxng.org/dev/engines/offline/sql-engines.html#engine-mariadb-server)

All of the engines above are just commented out in the [settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml), as you have to set the required attributes for the engines, e.g. `database:` …
```
- name: ...
  engine: {sqlite|postgresql|mysql_server}
  database: ...
  result_template: {template_name}
  query_str: ...

```

By default, the engines use the `key-value` template for displaying results / see [simple](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/key-value.html) theme. If you are not satisfied with the original result layout, you can use your own template, set `result_template` attribute to `{template_name}` and place the templates at:
```
searx/templates/{theme_name}/result_templates/{template_name}

```

If you do not wish to expose these engines on a public instance, you can still add them and limit the access by setting `tokens` as described in section [Private Engines (tokens)](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines).
## Extra Dependencies
For using [PostgreSQL](https://docs.searxng.org/dev/engines/offline/sql-engines.html#engine-postgresql) or [MySQL](https://docs.searxng.org/dev/engines/offline/sql-engines.html#engine-mysql-server) you need to install additional packages in Python’s Virtual Environment of your SearXNG instance. To switch into the environment ([Install SearXNG & dependencies](https://docs.searxng.org/admin/installation-searxng.html#searxng-src)) you can use [utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh):
```
$ sudo utils/searxng.sh instance cmd bash
(searxng-pyenv)$ pip install ...

```

## Configure the engines
The configuration of the new database engines are similar. You must put a valid SQL-SELECT query in `query_str`. At the moment you can only bind at most one parameter in your query. By setting the attribute `limit` you can define how many results you want from the SQL server. Basically, it is the same as the `LIMIT` keyword in SQL.
Please, do not include `LIMIT` or `OFFSET` in your SQL query as the engines rely on these keywords during paging. If you want to configure the number of returned results use the option `limit`.
### SQLite
> **Info:**
  * [sqlite.py](https://github.com/searxng/searxng/blob/master/searx/engines/sqlite.py)

SQLite is a small, fast and reliable SQL database engine. It does not require any extra dependency.
#### Configuration
The engine has the following (additional) settings:
  * [`result_type`](https://docs.searxng.org/dev/engines/offline/sql-engines.html#searx.engines.sqlite.result_type "searx.engines.sqlite.result_type")

#### Example
To demonstrate the power of database engines, here is a more complex example which reads from a [MediathekView](https://mediathekview.de/) (DE) movie database. For this example of the SQLite engine download the database:
  * <https://liste.mediathekview.de/filmliste-v2.db.bz2>

and unpack into `searx/data/filmliste-v2.db`. To search the database use e.g Query to test: `!mediathekview concert`
```
- name: mediathekview
  engine: sqlite
  shortcut: mediathekview
  categories: [general, videos]
  result_type: MainResult
  database: searx/data/filmliste-v2.db
  query_str: >-
    SELECT title || ' (' || time(duration, 'unixepoch') || ')' AS title,
           COALESCE( NULLIF(url_video_hd,''), NULLIF(url_video_sd,''), url_video) AS url,
           description AS content
      FROM film
     WHERE title LIKE :wildcard OR description LIKE :wildcard
     ORDER BY duration DESC

```

#### Implementations 

**engines.sqlite.database** = `''`
Filename of the SQLite DB. 

**engines.sqlite.query_str** = `''`
SQL query that returns the result items. 

**engines.sqlite.result_type** = `'KeyValue'`
The result type can be `MainResult` or `KeyValue`. 

**engines.sqlite.sqlite_cursor()**
Implements a [`Context Manager`](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager "\(in Python v3.14\)") for a [`sqlite3.Cursor`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor "\(in Python v3.14\)").
Open database in read only mode: if the database doesn’t exist. The default mode creates an empty file on the file system. See:
  * <https://docs.python.org/3/library/sqlite3.html#sqlite3.connect>
  * <https://www.sqlite.org/uri.html>

### PostgreSQL
> **Info:**
  * [postgresql.py](https://github.com/searxng/searxng/blob/master/searx/engines/postgresql.py)
  * `pip install` [psycopg2-binary](https://docs.searxng.org/dev/engines/offline/psycopg2)

PostgreSQL is a powerful and robust open source database. Before configuring the PostgreSQL engine, you must install the dependency `psychopg2`.
#### Example
Below is an example configuration:
```
- name: my_database
  engine: postgresql
  database: my_database
  username: searxng
  password: password
  query_str: 'SELECT * from my_table WHERE my_column = %(query)s'

```

#### Implementations 

**engines.postgresql.host** = `'127.0.0.1'`
Hostname of the DB connector 

**engines.postgresql.port** = `'5432'`
Port of the DB connector 

**engines.postgresql.database** = `''`
Name of the database. 

**engines.postgresql.username** = `''`
Username for the DB connection. 

**engines.postgresql.password** = `''`
Password for the DB connection. 

**engines.postgresql.query_str** = `''`
SQL query that returns the result items.
### MySQL
> **Info:**
  * [mysql_server.py](https://github.com/searxng/searxng/blob/master/searx/engines/mysql_server.py)
  * `pip install` [mysql-connector-python](https://pypi.org/project/mysql-connector-python)

MySQL is said to be the most popular open source database. Before enabling MySQL engine, you must install the package `mysql-connector-python`.
The authentication plugin is configurable by setting `auth_plugin` in the attributes. By default it is set to `caching_sha2_password`.
#### Example
This is an example configuration for querying a MySQL server:
```
- name: my_database
  engine: mysql_server
  database: my_database
  username: searxng
  password: password
  limit: 5
  query_str: 'SELECT * from my_table WHERE my_column=%(query)s'

```

#### Implementations 

**engines.mysql_server.host** = `'127.0.0.1'`
Hostname of the DB connector 

**engines.mysql_server.port** = `3306`
Port of the DB connector 

**engines.mysql_server.database** = `''`
Name of the database. 

**engines.mysql_server.username** = `''`
Username for the DB connection. 

**engines.mysql_server.password** = `''`
Password for the DB connection. 

**engines.mysql_server.query_str** = `''`
SQL query that returns the result items.
### MariaDB
> **Info:**
  * [mariadb_server.py](https://github.com/searxng/searxng/blob/master/searx/engines/mariadb_server.py)
  * `pip install` [mariadb](https://pypi.org/project/mariadb)

MariaDB is a community driven fork of MySQL. Before enabling MariaDB engine, you must the install the pip package `mariadb` along with the necessary prerequities.
[See the following documentation for more details](https://mariadb.com/docs/server/connect/programming-languages/c/install/)
#### Example
This is an example configuration for querying a MariaDB server:
```
- name: my_database
  engine: mariadb_server
  database: my_database
  username: searxng
  password: password
  limit: 5
  query_str: 'SELECT * from my_table WHERE my_column=%(query)s'

```

#### Implementations 

**engines.mariadb_server.host** = `'127.0.0.1'`
Hostname of the DB connector 

**engines.mariadb_server.port** = `3306`
Port of the DB connector 

**engines.mariadb_server.database** = `''`
Name of the database. 

**engines.mariadb_server.username** = `''`
Username for the DB connection. 

**engines.mariadb_server.password** = `''`
Password for the DB connection. 

**engines.mariadb_server.query_str** = `''`
SQL query that returns the result items.
