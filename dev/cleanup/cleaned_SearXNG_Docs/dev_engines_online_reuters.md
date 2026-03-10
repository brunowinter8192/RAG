<!-- source: https://docs.searxng.org/dev/engines/online/reuters.html -->

# Reuters
[Reuters](https://www.reuters.com) (news) is an international news agency.
## Configuration
The engine has the following additional settings:
  * [`sort_order`](https://docs.searxng.org/dev/engines/online/reuters.html#searx.engines.reuters.sort_order "searx.engines.reuters.sort_order")

```
- name: reuters
  engine: reuters
  shortcut: reu
  sort_order: "relevance"

```

## Implementations 

**engines.reuters.sort_order** = `'relevance'`
Sort order, one of `relevance`, `display_date:desc` or `display_data:asc`. 

searx.engines.reuters.resize_url(_thumbnail :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_, _width :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=0_, _height :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")=0_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Generates a URL for Reuter’s thumbnail with the dimensions _width_ and _height_. If no URL can be generated from the _thumbnail data_ , an empty string will be returned. 

width: default is _unset_ (`0`)
    
Image width in pixels (negative values are ignored). If only width is specified, the height matches the original aspect ratio. 

height: default is _unset_ (`0`)
    
Image height in pixels (negative values are ignored). If only height is specified, the width matches the original aspect ratio.
The file size of a full-size image is usually several MB; when reduced to a height of, for example, 80 points, only a few KB remain!
Fields of the _thumbnail data_ (`result.articles.[<int>].thumbnail`): 

thumbnail.url:
    
Is a full-size image (>MB). 

thumbnail.width & .height:
    
Dimensions of the full-size image. 

thumbnail.resizer_url:
    
Reuters has a _resizer_ [REST-API for the images](https://dev.arcxp.com/photo-center/image-resizer/resizer-v2-how-to-transform-images/#query-parameters), this is the URL of the service. This URL includes the `&auth` argument, other arguments are `&width=<int>` and `&height=<int>`.
