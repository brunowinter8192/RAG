<!-- source: https://docs.searxng.org/dev/templates.html -->

# Simple Theme Templates
The simple template is complex, it consists of many different elements and also uses macros and include statements. The following is a rough overview that we would like to give the developer at hand, details must still be taken from the [sources](https://github.com/searxng/searxng/blob/master/searx/templates/simple/).
A [result item](https://docs.searxng.org/dev/result_types/index.html#result-types) can be of different media types. The media type of a result is defined by the `result_type.Result.template`. To set another media-type as [default.html](https://docs.searxng.org/dev/templates.html#template-default), the field `template` in the result item must be set to the desired type.
Contents
## Result template macros
### `result_header`
Execpt `image.html` and some others this macro is used in nearly all result types in the [Main Result List](https://docs.searxng.org/dev/templates.html#main-result-list).
Fields used in the template [macro result_header](https://github.com/searxng/searxng/blob/master/searx/templates/simple/macros.html): 

url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Link URL of the result item. 

title[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Link title of the result item. 

img_src, thumbnail[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of a image or thumbnail that is displayed in the result item.
### `result_sub_header`
Execpt `image.html` and some others this macro is used in nearly all result types in the [Main Result List](https://docs.searxng.org/dev/templates.html#main-result-list).
Fields used in the template [macro result_sub_header](https://github.com/searxng/searxng/blob/master/searx/templates/simple/macros.html): 

publishedDate[`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime "\(in Python v3.14\)") 
    
The date on which the object was published. 

length: [`datetime.timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)") 
    
Playing duration in seconds. 

views: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
View count in humanized number format. 

author[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Author of the title. 

metadata[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Miscellaneous metadata.
### `engine_data_form`
The `engine_data_form` macro is used in [results,html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/results.html) in a HTML `<form/>` element. The intention of this macro is to pass data of a engine from one [`response`](https://docs.searxng.org/dev/engines/demo/demo_online.html#searx.engines.demo_online.response "searx.engines.demo_online.response") to the `searx.search.SearchQuery` of the next [`request`](https://docs.searxng.org/dev/engines/demo/demo_online.html#searx.engines.demo_online.request "searx.engines.demo_online.request").
To pass data, engine’s response handler can append result items of typ `engine_data`. This is by example used to pass a token from the response to the next request:
```
def response(resp):
    ...
    results.append({
       'engine_data': token,
       'key': 'next_page_token',
    })
    ...
    return results

def request(query, params):
    page_token = params['engine_data'].get('next_page_token')

```

## Main Result List
The **media types** of the **main result type** are the template files in the [result_templates](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates).
### `default.html`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header) and
  * [result_sub_header](https://docs.searxng.org/dev/templates.html#macro-result-sub-header)

Additional fields used in the [default.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/default.html): 

content[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
General text of the result item. 

iframe_src[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of an embedded `<iframe>` / the frame is collapsible. 

audio_srcuri, 
    
URL of an embedded `<audio controls>`.
### `images.html`
The images are displayed as small thumbnails in the main results list. 

title[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Title of the image. 

thumbnail_src[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of a preview of the image. 

resolution [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The resolution of the image (e.g. `1920 x 1080` pixel)
#### Image labels
Clicking on the preview opens a gallery view in which all further metadata for the image is displayed. Addition fields used in the [images.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/images.html): 

img_src[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of the full size image. 

content: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Description of the image. 

author: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Name of the author of the image. 

img_format[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The format of the image (e.g. `png`). 

source[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Source of the image. 

filesize: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Size of bytes in `human readable` notation (e.g. `MB` for 1024 * 1024 Bytes filesize). 

url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of the page from where the images comes from (source).
### `videos.html`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header) and
  * [result_sub_header](https://docs.searxng.org/dev/templates.html#macro-result-sub-header)

Additional fields used in the [videos.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/videos.html): 

iframe_src[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of an embedded `<iframe>` / the frame is collapsible.
The videos are displayed as small thumbnails in the main results list, there is an additional button to collaps/open the embeded video. 

content[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Description of the code fragment.
### `torrent.html`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header) and
  * [result_sub_header](https://docs.searxng.org/dev/templates.html#macro-result-sub-header)

Additional fields used in the [torrent.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/torrent.html): 

magnetlink:
    
URL of the [magnet link](https://en.wikipedia.org/wiki/Magnet_URI_scheme). 

torrentfile
    
URL of the [torrent file](https://en.wikipedia.org/wiki/Torrent_file). 

seed`int` 
    
Number of seeders. 

leech`int` 
    
Number of leecher 

filesize`int` 
    
Size in Bytes (rendered to human readable unit of measurement). 

files`int` 
    
Number of files.
### `map.html`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header) and
  * [result_sub_header](https://docs.searxng.org/dev/templates.html#macro-result-sub-header)

Additional fields used in the [map.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/map.html): 

content[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Description of the item. 

address_label[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Label of the address / default `_('address')`. 

geojson[GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) 
    
Geometries mapped to [HTMLElement.dataset](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset) (`data-map-geojson`) and used by [Leaflet](https://github.com/Leaflet/Leaflet). 

boundingbox`[ min-lon, min-lat, max-lon, max-lat]` 
    
A [bbox](https://wiki.openstreetmap.org/wiki/Bounding_Box) area defined by min longitude , min latitude , max longitude and max latitude. The bounding box is mapped to [HTMLElement.dataset](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset) (`data-map-boundingbox`) and is used by [Leaflet](https://github.com/Leaflet/Leaflet). 

longitude, latitude[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Geographical coordinates, mapped to [HTMLElement.dataset](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset) (`data-map-lon`, `data-map-lat`) and is used by [Leaflet](https://github.com/Leaflet/Leaflet). 

address`{...}` 
    
A dicticonary with the address data:
```
address = {
    'name'          : str,  # name of object
    'road'          : str,  # street name of object
    'house_number'  : str,  # house number of object
    'postcode'      : str,  # postcode of object
    'country'       : str,  # country of object
    'country_code'  : str,
    'locality'      : str,
}

```

country_code[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
[Country code](https://wiki.openstreetmap.org/wiki/Country_code) of the object. 

locality[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The name of the city, town, township, village, borough, etc. in which this object is located. 

links`[link1, link2, ...]` 
    
A list of links with labels:
```
links.append({
    'label'       : str,
    'url'         : str,
    'url_label'   : str,  # set by some engines but unused (oscar)
})

```

data`[data1, data2, ...]` 
    
A list of additional data, shown in two columns and containing a label and value.
```
data.append({
   'label'   : str,
   'value'   : str,
   'key'     : str,  # set by some engines but unused
})

```

type[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") # set by some engines but unused (oscar) 
    
Tag label from [OSM_KEYS_TAGS[‘tags’]](https://docs.searxng.org/dev/searxng_extra/update.html#update-osm-keys-tags-py). 

type_icon[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") # set by some engines but unused (oscar) 
    
Type’s icon. 

osm`{...}` 
    
OSM-type and OSM-ID, can be used to [Lookup](https://nominatim.org/release-docs/latest/api/Lookup/) OSM data ([Nominatim](https://nominatim.org/release-docs/latest/)). There is also a discussion about “[place_id is not a persistent id](https://nominatim.org/release-docs/latest/api/Output/#place_id-is-not-a-persistent-id)” and the [perma_id](https://wiki.openstreetmap.org/wiki/Permanent_ID).
```
osm = {
    'type': str,
    'id':   str,
}

```

type[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Type of osm-object (if OSM-Result). 

id :
    
ID of osm-object (if OSM-Result).
Hint
The `osm` property is set by engine `openstreetmap.py`, but it is not used in the `map.html` template yet.
### `paper.html`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header)

Additional fields used in the [paper.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/paper.html): 

content[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
An abstract or excerpt from the document. 

comments[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Free text display in italic below the content. 

tags[`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Free tag list. 

type[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Short description of medium type, e.g. _book_ , _pdf_ or _html_ … 

authors[`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
List of authors of the work (authors with a “s” suffix, the “author” is in the [result_sub_header](https://docs.searxng.org/dev/templates.html#macro-result-sub-header)). 

editor[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Editor of the book/paper. 

publisher[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Name of the publisher. 

journal[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Name of the journal or magazine the article was published in. 

volume[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Volume number. 

pages[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Page range where the article is. 

number[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Number of the report or the issue number for a journal article. 

doi[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
DOI number (like `10.1038/d41586-018-07848-2`). 

issn[`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
ISSN number like `1476-4687` 

isbn[`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
ISBN number like `9780201896831` 

pdf_url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL to the full article, the PDF version 

html_url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL to full article, HTML version
### `packages`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header)

Additional fields used in the [packages.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/packages.html): 

package_name[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The name of the package. 

version[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The current version of the package. 

maintainer[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The maintainer or author of the project. 

publishedDate[`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime "\(in Python v3.14\)") 
    
Date of latest update or release. 

tags[`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] 
    
Free tag list. 

popularity[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The popularity of the package, e.g. rating or download count. 

license_name[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The name of the license. 

license_url[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The web location of a license copy. 

homepage[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The url of the project’s homepage. 

source_code_url: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The location of the project’s source code. 

links[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)") 
    
Additional links in the form of `{'link_name': 'http://example.com'}`
### `products.html`
Displays result fields from:
  * [result_header](https://docs.searxng.org/dev/templates.html#macro-result-header) and
  * [result_sub_header](https://docs.searxng.org/dev/templates.html#macro-result-sub-header)

Additional fields used in the [products.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/result_templates/products.html): 

content[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Description of the product. 

price[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
The price must include the currency. 

shipping[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Shipping details. 

source_country[`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Place from which the shipment is made.
## Answer results
See [Answer Results](https://docs.searxng.org/dev/result_types/answer.html#result-types-answer)
## Suggestion results
See [Suggestion Results](https://docs.searxng.org/dev/result_types/suggestion.html#result-types-suggestion)
## Correction results
See [Correction Results](https://docs.searxng.org/dev/result_types/correction.html#result-types-corrections)
## Infobox results
See [Infobox Results](https://docs.searxng.org/dev/result_types/infobox.html#result-types-infobox)
