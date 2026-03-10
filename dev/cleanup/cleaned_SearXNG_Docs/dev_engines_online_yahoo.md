<!-- source: https://docs.searxng.org/dev/engines/online/yahoo.html -->

# Yahoo Engine
Yahoo Search (Web)
Languages are supported by mapping the language to a domain. If domain is not found in [`lang2domain`](https://docs.searxng.org/dev/engines/online/yahoo.html#searx.engines.yahoo.lang2domain "searx.engines.yahoo.lang2domain") URL `<lang>.search.yahoo.com` is used. 

**engines.yahoo.region2domain** = `{'AR': 'ar.search.yahoo.com', 'BR': 'br.search.yahoo.com', 'CA': 'ca.search.yahoo.com', 'CL': 'cl.search.yahoo.com', 'CO': 'co.search.yahoo.com', 'DE': 'de.search.yahoo.com', 'ES': 'espanol.search.yahoo.com', 'FR': 'fr.search.yahoo.com', 'GB': 'uk.search.yahoo.com', 'HK': 'hk.search.yahoo.com', 'IN': 'in.search.yahoo.com', 'MX': 'mx.search.yahoo.com', 'PE': 'pe.search.yahoo.com', 'PH': 'ph.search.yahoo.com', 'SG': 'sg.search.yahoo.com', 'TH': 'th.search.yahoo.com', 'TW': 'tw.search.yahoo.com', 'UK': 'uk.search.yahoo.com', 'VE': 've.search.yahoo.com'}`
Map regions to domain 

**engines.yahoo.lang2domain** = `{'any': 'search.yahoo.com', 'bg': 'search.yahoo.com', 'cs': 'search.yahoo.com', 'da': 'search.yahoo.com', 'el': 'search.yahoo.com', 'en': 'search.yahoo.com', 'et': 'search.yahoo.com', 'he': 'search.yahoo.com', 'hr': 'search.yahoo.com', 'ja': 'search.yahoo.com', 'ko': 'search.yahoo.com', 'sk': 'search.yahoo.com', 'sl': 'search.yahoo.com', 'zh_chs': 'hk.search.yahoo.com', 'zh_cht': 'tw.search.yahoo.com'}`
Map language to domain 

**engines.yahoo.build_sb_cookie(_cookie_params_)**
Build sB cookie parameter from provided parameters. 

Parameters: 
    
**cookie_params** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")) – Dictionary of cookie parameters 

Returns: 
    
Formatted cookie string 

Return type: 
    
[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 

Example:
    
```
>>> cookie_params = {'v': '1', 'vm': 'p', 'fl': '1', 'vl': 'lang_fr'}
>>> build_sb_cookie(cookie_params)
'v=1&vm=p&fl=1&vl=lang_fr'

```

**engines.yahoo.request(_query_ , _params_)**
Build Yahoo search request. 

**engines.yahoo.parse_url(_url_string_)**
remove yahoo-specific tracking-url 

**engines.yahoo.response(_resp_)**
parse response
