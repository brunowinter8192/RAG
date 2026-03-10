<!-- source: https://docs.searxng.org/dev/engines/online/marginalia.html -->

# Marginalia Search
[Marginalia Search](https://about.marginalia-search.com/) is an independent open source Internet search engine operating out of Sweden. It is principally developed and operated by Viktor Lofgren .
## Configuration
The engine has the following required settings:
  * [`api_key`](https://docs.searxng.org/dev/engines/online/marginalia.html#searx.engines.marginalia.api_key "searx.engines.marginalia.api_key")

You can configure a Marginalia engine by:
```
- name: marginalia
  engine: marginalia
  shortcut: mar
  api_key: ...

```

## Implementations 

**engines.marginalia.api_key** = `None`
To get an API key, please follow the instructions from [Key and license](https://about.marginalia-search.com/article/api/) 

_class_ searx.engines.marginalia.ApiSearchResult 
    
Marginalia’s [ApiSearchResult](https://github.com/MarginaliaSearch/MarginaliaSearch/blob/master/code/services-application/api-service/java/nu/marginalia/api/model/ApiSearchResult.java) class definition. 

_class_ searx.engines.marginalia.ApiSearchResults 
    
Marginalia’s [ApiSearchResults](https://github.com/MarginaliaSearch/MarginaliaSearch/blob/master/code/services-application/api-service/java/nu/marginalia/api/model/ApiSearchResults.java) class definition.
