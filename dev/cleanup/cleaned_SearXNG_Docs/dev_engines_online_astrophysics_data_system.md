<!-- source: https://docs.searxng.org/dev/engines/online/astrophysics_data_system.html -->

# Astrophysics Data System (ADS)
The Astrophysics Data System ([ADS](https://ui.adsabs.harvard.edu)) is a digital library portal for researchers in astronomy and physics, operated by the Smithsonian Astrophysical Observatory (SAO) under a NASA grant. The [ADS](https://ui.adsabs.harvard.edu) is a solr instance, but not with the standard API paths.
Note
The [ADS](https://ui.adsabs.harvard.edu) engine requires an [`API key`](https://docs.searxng.org/dev/engines/online/astrophysics_data_system.html#searx.engines.astrophysics_data_system.api_key "searx.engines.astrophysics_data_system.api_key").
This engine uses the [search/query](https://ui.adsabs.harvard.edu/help/api/api-docs.html#get-/search/query) API endpoint. Since the user’s search term is passed through, the [search syntax](https://ui.adsabs.harvard.edu/help/search/search-syntax) of ADS can be used (at least to some extent).
## Configuration
The engine has the following additional settings:
```
- name: astrophysics data system
  api_key: "..."
  inactive: false

```

## Implementations 

**engines.astrophysics_data_system.api_key** = `'unset'`
Get an API token as described in <https://ui.adsabs.harvard.edu/help/api> 

**engines.astrophysics_data_system.ads_field_list** = `['abstract', 'author', 'bibcode', 'comment', 'date', 'doi', 'isbn', 'issn', 'keyword', 'page', 'page_count', 'page_range', 'pub', 'pubdate', 'pubnote', 'read_count', 'title', 'volume', 'year']`
Set of fields to return in the response from ADS. 

**engines.astrophysics_data_system.ads_rows** = `10`
How many records to return for the ADS request. 

**engines.astrophysics_data_system.ads_sort** = `'read_count desc'`
The format is ‘field’ + ‘direction’ where direction is one of ‘asc’ or ‘desc’ and field is any of the valid indexes. 

searx.engines.astrophysics_data_system.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the [ADS](https://ui.adsabs.harvard.edu) engine, checks whether the [`api_key`](https://docs.searxng.org/dev/engines/online/astrophysics_data_system.html#searx.engines.astrophysics_data_system.api_key "searx.engines.astrophysics_data_system.api_key") is set, otherwise the engine is inactive.
