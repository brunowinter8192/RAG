<!-- source: https://docs.searxng.org/dev/engines/online/springer.html -->

# Springer Nature
[Springer Nature](https://www.springernature.com/) is a global publisher dedicated to providing service to research community with official [Springer-API](https://dev.springernature.com/docs/introduction/) ([API-Playground](https://dev.springernature.com/docs/live-documentation/)).
Note
The Springer engine requires an API key, which can be obtained via the [Springer subscription](https://dev.springernature.com/subscription/).
Since the search term is passed 1:1 to the API, SearXNG users can use the [Supported Query Parameters](https://dev.springernature.com/docs/supported-query-params/).
  * `!springer (doi:10.1007/s10948-025-07019-1 OR doi:10.1007/s10948-025-07035-1)`
  * `!springer keyword:ybco`

However, please note that the available options depend on the subscription type.
For example, the `year:` filter requires a _Premium Plan_ subscription.
  * `!springer keyword:ybco year:2024`

The engine uses the REST [Meta-API](https://dev.springernature.com/docs/api-endpoints/meta-api/) v2 endpoint, but there is also a [Python API Wrapper](https://pypi.org/project/springernature-api-client/).
## Configuration
The engine has the following additional settings:
  * [`api_key`](https://docs.searxng.org/dev/engines/online/springer.html#searx.engines.springer.api_key "searx.engines.springer.api_key")

```
- name: springer nature
  api_key: "..."
  inactive: false

```

## Implementations 

**engines.springer.nb_per_page** = `10`
Number of results to return in the request, see [Pagination and Limits](https://dev.springernature.com/docs/advanced-querying/pagination-limits/) for more details. 

**engines.springer.api_key** = `''`
Key used for the [Meta-API](https://dev.springernature.com/docs/api-endpoints/meta-api/). Get your API key from: [Springer subscription](https://dev.springernature.com/subscription/) 

**engines.springer.base_url** = `'https://api.springernature.com/meta/v2/json'`
An enhanced endpoint with additional metadata fields and optimized queries for more efficient and comprehensive retrieval ([Meta-API](https://dev.springernature.com/docs/api-endpoints/meta-api/) v2). 

searx.engines.springer.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the Springer engine, checks whether the [`api_key`](https://docs.searxng.org/dev/engines/online/springer.html#searx.engines.springer.api_key "searx.engines.springer.api_key") is set, otherwise the engine is inactive.
