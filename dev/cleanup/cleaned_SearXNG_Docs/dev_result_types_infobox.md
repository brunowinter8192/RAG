<!-- source: https://docs.searxng.org/dev/result_types/infobox.html -->

# Infobox Results
Hint
There is still no typing for these result items. The templates can be used as orientation until the final typing is complete.
The [area info box](https://docs.searxng.org/dev/result_types/index.html#area-info-box) is an area where addtional infos shown to the user.
Fields used in the [infobox.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/elements/infobox.html): 

img_src: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
URL of a image or thumbnail that is displayed in the infobox. 

infobox: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Title of the info box. 

content: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Text of the info box.
The infobox has additional subsections for _attributes_ , _urls_ and _relatedTopics_ : 

attributes: [`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")]
    
A list of attributes. An _attribute_ is a dictionary with keys:
  * label [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): (mandatory)
  * value [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): (mandatory)
  * image [`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")] (optional)
A list of images. An _image_ is a dictionary with keys:
    * src [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): URL of an image/thumbnail (mandatory)
    * alt [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): alternative text for the image (mandatory)

urls: [`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")]
    
A list of links. An _link_ is a dictionary with keys:
  * url [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): URL of the link (mandatory)
  * title [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): Title of the link (mandatory)

relatedTopics: [`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")]
    
A list of topics. An _topic_ is a dictionary with keys:
  * name: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): (mandatory)
  * suggestions: [`List`](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[`dict`](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")] (optional)
A list of suggestions. A _suggestion_ is simple dictionary with just one key/value pair:
    * suggestion: [`str`](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"): suggested search term (mandatory)
