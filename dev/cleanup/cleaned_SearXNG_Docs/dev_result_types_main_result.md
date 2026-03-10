<!-- source: https://docs.searxng.org/dev/result_types/main_result.html -->

# Main Search Results
In the [area main results](https://docs.searxng.org/dev/result_types/index.html#area-main-results) the results that a search engine has found for the search term are displayed.
There is still no typing for all items in the [Main Result List](https://docs.searxng.org/dev/templates.html#main-result-list). The following types have been implemented so far ..
  * [`MainResult`](https://docs.searxng.org/dev/result_types/main/mainresult.html)
  * [Key-Value Results](https://docs.searxng.org/dev/result_types/main/keyvalue.html)
    * [`KeyValue`](https://docs.searxng.org/dev/result_types/main/keyvalue.html#searx.result_types.keyvalue.KeyValue)
  * [Code Results](https://docs.searxng.org/dev/result_types/main/code.html)
    * [`Code`](https://docs.searxng.org/dev/result_types/main/code.html#searx.result_types.code.Code)
  * [Paper Results](https://docs.searxng.org/dev/result_types/main/paper.html)
    * [`Paper`](https://docs.searxng.org/dev/result_types/main/paper.html#searx.result_types.paper.Paper)
  * [File Results](https://docs.searxng.org/dev/result_types/main/file.html)
    * [`File`](https://docs.searxng.org/dev/result_types/main/file.html#searx.result_types.file.File)

The [LegacyResult](https://docs.searxng.org/dev/result_types/base_result.html#legacyresult) is used internally for the results that have not yet been typed. The templates can be used as orientation until the final typing is complete.
  * [default.html](https://docs.searxng.org/dev/templates.html#template-default) / `Result`
