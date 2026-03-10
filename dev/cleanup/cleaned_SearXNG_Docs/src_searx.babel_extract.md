<!-- source: https://docs.searxng.org/src/searx.babel_extract.html -->

# Custom message extractor (i18n)
This module implements the [searxng_msg](https://github.com/searxng/searxng/blob/master/babel.cfg) extractor to extract messages from:
  * [git://searx/searxng.msg](https://github.com/searxng/searxng/blob/master/searx/searxng.msg)

The `searxng.msg` files are selected by [Babel](https://babel.pocoo.org/en/latest/index.html), see Babel’s configuration in [git://babel.cfg](https://github.com/searxng/searxng/blob/master/babel.cfg):
```
searxng_msg = searx.babel_extract.extract
...
[searxng_msg: **/searxng.msg]

```

A `searxng.msg` file is a python file that is _executed_ by the [`extract`](https://docs.searxng.org/src/searx.babel_extract.html#searx.babel_extract.extract "searx.babel_extract.extract") function. Additional `searxng.msg` files can be added by:
  1. Adding a `searxng.msg` file in one of the SearXNG python packages and
  2. implement a method in [`extract`](https://docs.searxng.org/src/searx.babel_extract.html#searx.babel_extract.extract "searx.babel_extract.extract") that yields messages from this file.

**babel_extract.extract(_fileobj_ , _keywords_ , _comment_tags_ , _options_)**
Extract messages from `searxng.msg` files by a custom [extractor](https://babel.pocoo.org/en/latest/messages.html#writing-extraction-methods).
