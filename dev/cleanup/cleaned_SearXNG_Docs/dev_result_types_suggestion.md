<!-- source: https://docs.searxng.org/dev/result_types/suggestion.html -->

# Suggestion Results
Hint
There is still no typing for these result items. The templates can be used as orientation until the final typing is complete.
The [area suggestions](https://docs.searxng.org/dev/result_types/index.html#area-suggestions-results) shows the user alternative search terms.
A result of this type is a very simple dictionary with only one key/value pair
```
{"suggestion" : "lorem ipsum .."}

```

From this simple dict another dict is build up:
```
{"url" : "!bang lorem ipsum ..", "title": "lorem ipsum" }

```

and used in the template [suggestions.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/elements/suggestions.html):
```
# use RawTextQuery to get the suggestion URLs with the same bang
{"url" : "!bang lorem ipsum ..", "title": "lorem ipsum" }

```

title[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Suggested search term 

url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Not really an URL, its the value to insert in a HTML form for a SearXNG query.
