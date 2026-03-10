<!-- source: https://docs.searxng.org/admin/settings/settings_brand.html -->

#  `brand:` 

_class_ searx.brand.SettingsBrand(_*_ , _issue_url: str = 'https://github.com/searxng/searxng/issues'_, _docs_url: str = 'https://docs.searxng.org'_, _public_instances: str = 'https://searx.space'_, _wiki_url: str = 'https://github.com/searxng/searxng/wiki'_, _custom: ~searx.brand.BrandCustom = <factory>_, _new_issue_url: str = 'https://github.com/searxng/searxng/issues/new'_) 
    
Options for configuring brand properties.
```
brand:
  issue_url: https://github.com/searxng/searxng/issues
  docs_url: https://docs.searxng.org
  public_instances: https://searx.space
  wiki_url: https://github.com/searxng/searxng/wiki

  custom:
    links:
      Uptime: https://uptime.searxng.org/history/example-org
      About: https://example.org/user/about.html

```

issue_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
If you host your own issue tracker change this URL. 

docs_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
If you host your own documentation change this URL. 

public_instances _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
If you host your own <https://searx.space> change this URL. 

wiki_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Link to your wiki (or `false`) 

custom _: BrandCustom_ 
    
Optional customizing. 

_class_ BrandCustom(_*_ , _links: dict[str_, _str] = <factory>_) 
    
Custom settings in the brand section. 

BrandCustom.links _:[ dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Custom entries in the footer of the WEB page: `[title]: [link]` 

new_issue_url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
If you host your own issue tracker not on GitHub, then unset this URL.
Note: This URL will create a pre-filled GitHub bug report form for an engine. Since this feature is implemented only for GH (and limited to engines), it will probably be replaced by another solution in the near future.
