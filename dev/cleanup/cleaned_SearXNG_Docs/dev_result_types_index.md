<!-- source: https://docs.searxng.org/dev/result_types/index.html -->

# Result Types
To understand the typification of the results, let’s take a brief look at the structure of SearXNG .. At its core, SearXNG is nothing more than an aggregator that aggregates the results from various sources, renders them via templates and displays them to the user.
The **sources** can be:
  1. [engines](https://docs.searxng.org/dev/engines/index.html#engine-implementations)
  2. [plugins](https://docs.searxng.org/dev/plugins/development.html#dev-plugin)
  3. [answerers](https://docs.searxng.org/dev/answerers/development.html#dev-answerers)

The sources provide the results, which are displayed in different **areas** depending on the type of result. The areas are: 

[area main results](https://docs.searxng.org/dev/result_types/main_result.html#main-search-results)
    
It is the main area in which – as is typical for search engines – the results that a search engine has found for the search term are displayed. 

[area answers](https://docs.searxng.org/dev/result_types/answer.html#result-types-answer)
    
This area displays short answers that could be found for the search term. 

[area info box](https://docs.searxng.org/dev/result_types/infobox.html#result-types-infobox)
    
An area in which additional information can be displayed, e.g. excerpts from wikipedia or other sources such as maps. 

[area suggestions](https://docs.searxng.org/dev/result_types/suggestion.html#result-types-suggestion)
    
Suggestions for alternative search terms can be found in this area. These can be clicked on and a search is carried out with these search terms. 

[area corrections](https://docs.searxng.org/dev/result_types/correction.html#result-types-corrections)
    
Results in this area are like the suggestion of alternative search terms, which usually result from spelling corrections
At this point it is important to note that all **sources** can contribute results to all of the areas mentioned above.
In most cases, however, the [engines](https://docs.searxng.org/dev/engines/index.html#engine-implementations) will fill the _main results_ and the [answerers](https://docs.searxng.org/dev/answerers/development.html#dev-answerers) will generally provide the contributions for the _answer_ area. Not necessary to mention here but for a better understanding: the plugins can also filter out or change results from the main results area (e.g. the URL of the link).
The result items are organized in the `results.ResultContainer` and after all sources have delivered their results, this container is passed to the templating to build a HTML output. The output is usually HTML, but it is also possible to output the result lists as JSON or RSS feed. Thats quite all we need to know before we dive into typification of result items.
Hint
Typification of result items: we are at the very first beginng!
The first thing we have to realize is that there is no typification of the result items so far, we have to build it up first .. and that is quite a big task, which we will only be able to accomplish gradually.
The foundation for the typeless results was laid back in 2013 in the very first commit [@ae9fb1d](https://github.com/searxng/searxng/commit/ae9fb1d7d), and the principle has not changed since then. At the time, the approach was perfectly adequate, but we have since evolved and the demands on SearXNG increase with every feature request.
**Motivation:** in the meantime, it has become very difficult to develop new features that require structural changes and it is especially hard for newcomers to find their way in this typeless world. As long as the results are only simple key/value dictionaries, it is not even possible for the IDEs to support the application developer in his work.
**Planning:** The procedure for subsequent typing will have to be based on the circumstances ..
Attention
As long as there is no type defined for a kind of result the HTML template specify what the properties of a type are.
In this sense, you will either find a type definition here in the documentation or, if this does not yet exist, a description of the HTML template.
  * [Result](https://docs.searxng.org/dev/result_types/base_result.html)
  * [Main Search Results](https://docs.searxng.org/dev/result_types/main_result.html)
    * [`MainResult`](https://docs.searxng.org/dev/result_types/main/mainresult.html)
    * [Key-Value Results](https://docs.searxng.org/dev/result_types/main/keyvalue.html)
    * [Code Results](https://docs.searxng.org/dev/result_types/main/code.html)
    * [Paper Results](https://docs.searxng.org/dev/result_types/main/paper.html)
    * [File Results](https://docs.searxng.org/dev/result_types/main/file.html)
  * [Answer Results](https://docs.searxng.org/dev/result_types/answer.html)
  * [Correction Results](https://docs.searxng.org/dev/result_types/correction.html)
  * [Suggestion Results](https://docs.searxng.org/dev/result_types/suggestion.html)
  * [Infobox Results](https://docs.searxng.org/dev/result_types/infobox.html)
