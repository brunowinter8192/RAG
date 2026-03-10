<!-- source: https://docs.searxng.org/dev/engines/offline/search-indexer-engines.html -->

# Local Search APIs
**Further reading:**
  * [Comparison to alternatives](https://docs.meilisearch.com/learn/what_is_meilisearch/comparison_to_alternatives.html)

> **Info:**
Initial sponsored by [Search and Discovery Fund](https://nlnet.nl/discovery) of [NLnet Foundation](https://nlnet.nl/).
Administrators might find themselves wanting to integrate locally running search engines. The following ones are supported for now:
  * [Elasticsearch](https://www.elastic.co/elasticsearch/)
  * [Meilisearch](https://www.meilisearch.com)
  * [Solr](https://solr.apache.org)

Each search engine is powerful, capable of full-text search. All of the engines above are added to `settings.yml` just commented out, as you have to `base_url` for all them.
Please note that if you are not using HTTPS to access these engines, you have to enable HTTP requests by setting `enable_http` to `True`.
Furthermore, if you do not want to expose these engines on a public instance, you can still add them and limit the access by setting `tokens` as described in section [Private Engines (tokens)](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines).
## MeiliSearch
> **Info:**
  * [meilisearch.py](https://github.com/searxng/searxng/blob/master/searx/engines/meilisearch.py)
  * [MeiliSearch](https://www.meilisearch.com)
  * [MeiliSearch Documentation](https://docs.meilisearch.com/)
  * [Install MeiliSearch](https://docs.meilisearch.com/learn/getting_started/installation.html)

[MeiliSearch](https://www.meilisearch.com) is aimed at individuals and small companies. It is designed for small-scale (less than 10 million documents) data collections. E.g. it is great for storing web pages you have visited and searching in the contents later.
The engine supports faceted search, so you can search in a subset of documents of the collection. Furthermore, you can search in [MeiliSearch](https://www.meilisearch.com) instances that require authentication by setting [auth_key](https://www.meilisearch.com/docs/reference/api/overview#authorization).
### Example
Here is a simple example to query a Meilisearch instance:
```
- name: meilisearch
  engine: meilisearch
  shortcut: mes
  base_url: http://localhost:7700
  index: my-index
  enable_http: true
  # auth_key: Bearer XXXXX

```

## Elasticsearch
> **Info:**
  * [elasticsearch.py](https://github.com/searxng/searxng/blob/master/searx/engines/elasticsearch.py)
  * [Elasticsearch](https://www.elastic.co/elasticsearch/)
  * [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
  * [Install Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)

[Elasticsearch](https://www.elastic.co/elasticsearch/) supports numerous ways to query the data it is storing. At the moment the engine supports the most popular search methods (`query_type`):
  * `match`,
  * `simple_query_string`,
  * `term` and
  * `terms`.

If none of the methods fit your use case, you can select `custom` query type and provide the JSON payload to submit to Elasticsearch in `custom_query_json`.
### Example
The following is an example configuration for an [Elasticsearch](https://www.elastic.co/elasticsearch/) instance with authentication configured to read from `my-index` index.
```
- name: elasticsearch
  shortcut: els
  engine: elasticsearch
  base_url: http://localhost:9200
  username: elastic
  password: changeme
  index: my-index
  query_type: match
  # custom_query_json: '{ ... }'
  enable_http: true

```

## Solr
> **Info:**
  * [solr.py](https://github.com/searxng/searxng/blob/master/searx/engines/solr.py)
  * [Solr](https://solr.apache.org)
  * [Solr Resources](https://solr.apache.org/resources.html)
  * [Install Solr](https://solr.apache.org/guide/installing-solr.html)

[Solr](https://solr.apache.org) is a popular search engine based on Lucene, just like [Elasticsearch](https://www.elastic.co/elasticsearch/). But instead of searching in indices, you can search in collections.
### Example
This is an example configuration for searching in the collection `my-collection` and get the results in ascending order.
```
- name: solr
  engine: solr
  shortcut: slr
  base_url: http://localhost:8983
  collection: my-collection
  sort: asc
  enable_http: true

```
