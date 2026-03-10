<!-- source: https://docs.searxng.org/dev/engines/online_url_search/tineye.html -->

# Tineye
This engine implements _Tineye - reverse image search_
Using TinEye, you can search by image or perform what we call a reverse image search. You can do that by uploading an image or searching by URL. You can also simply drag and drop your images to start your search. TinEye constantly crawls the web and adds images to its index. Today, the TinEye index is over 50.2 billion images [[tineye.com]](https://tineye.com/how).
Hint
This SearXNG engine only supports _‘searching by URL’_ and it does not use the official API [[api.tineye.com]](https://api.tineye.com/python/docs/). 

**engines.tineye.engine_type** = `'online_url_search'`
[`searx.search.processors.online_url_search`](https://docs.searxng.org/src/searx.search.processors.html#module-searx.search.processors.online_url_search "searx.search.processors.online_url_search") 

**engines.tineye.FORMAT_NOT_SUPPORTED** = `'Could not read that image url. This may be due to an unsupported file format. TinEye only supports images that are JPEG, PNG, GIF, BMP, TIFF or WebP.'`
TinEye error message 

**engines.tineye.NO_SIGNATURE_ERROR** = `'The image is too simple to find matches. TinEye requires a basic level of visual detail to successfully identify matches.'`
TinEye error message 

**engines.tineye.DOWNLOAD_ERROR** = `'The image could not be downloaded.'`
TinEye error message 

**engines.tineye.request(_query_ , _params_)**
Build TinEye HTTP request using `search_urls` of a [`engine_type`](https://docs.searxng.org/dev/engines/online_url_search/tineye.html#searx.engines.tineye.engine_type "searx.engines.tineye.engine_type"). 

**engines.tineye.parse_tineye_match(_match_json_)**
Takes parsed JSON from the API server and turns it into a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)") object.
Attributes [(class Match)](https://github.com/TinEye/pytineye/blob/main/pytineye/api.py)
  * image_url, link to the result image.
  * domain, domain this result was found on.
  * score, a number (0 to 100) that indicates how closely the images match.
  * width, image width in pixels.
  * height, image height in pixels.
  * size, image area in pixels.
  * format, image format.
  * filesize, image size in bytes.
  * overlay, overlay URL.
  * tags, whether this match belongs to a collection or stock domain.
  * backlinks, a list of Backlink objects pointing to the original websites and image URLs. List items are instances of [`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)"), ([Backlink](https://github.com/TinEye/pytineye/blob/main/pytineye/api.py)):
    * url, the image URL to the image.
    * backlink, the original website URL.
    * crawl_date, the date the image was crawled.

searx.engines.tineye.response(_resp_) → [EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults") 
    
Parse HTTP response from TinEye.
