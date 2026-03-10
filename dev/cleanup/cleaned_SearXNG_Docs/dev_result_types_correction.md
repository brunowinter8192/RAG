<!-- source: https://docs.searxng.org/dev/result_types/correction.html -->

# Correction Results
Hint
There is still no typing for these result items. The templates can be used as orientation until the final typing is complete.
The [area corrections](https://docs.searxng.org/dev/result_types/index.html#area-corrections-results) shows the user alternative search terms.
A result of this type is a very simple dictionary with only one key/value pair
```
{"correction" : "lorem ipsum .."}

```

From this simple dict another dict is build up:
```
# use RawTextQuery to get the corrections URLs with the same bang
{"url" : "!bang lorem ipsum ..", "title": "lorem ipsum .." }

```

and used in the template [corrections.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/elements/corrections.html): 

title[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Corrected search term. 

url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Not really an URL, its the value to insert in a HTML form for a SearXNG query.
