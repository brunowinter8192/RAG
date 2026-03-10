<!-- source: https://docs.searxng.org/dev/answerers/development.html -->

# Answerer Development
The _answerers_ give instant answers related to the search query, they usually provide answers of type `Answer`.
Here is an example of a very simple answerer that adds a “Hello” into the answer area:
```
from flask_babel import gettext as _
from searx.answerers import Answerer
from searx.result_types import Answer

class MyAnswerer(Answerer):

    keywords = [ "hello", "hello world" ]

    def info(self):
        return AnswererInfo(name=_("Hello"), description=_("lorem .."), keywords=self.keywords)

    def answer(self, request, search):
        return [ Answer(answer="Hello") ]

```

* * * 

_class_ searx.answerers.Answerer 
    
Abstract base class of answerers. 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
Keywords to which the answerer has _answers_. 

_abstractmethod_ answer(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[BaseAnswer](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")] 
    
Function that returns a list of answers to the question/query. 

_abstractmethod_ info() → [AnswererInfo](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.AnswererInfo "searx.answerers._core.AnswererInfo") 
    
Information about the _answerer_ , see [`AnswererInfo`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.AnswererInfo "searx.answerers.AnswererInfo"). 

_class_ searx.answerers.AnswererInfo(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _description :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _examples :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_, _keywords :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) 
    
Object that holds information about an answerer, these infos are shown to the user in the Preferences menu.
To be able to translate the information into other languages, the text must be written in English and translated with [`flask_babel.gettext`](https://python-babel.github.io/flask-babel/index.html#flask_babel.gettext "\(in Flask-Babel\)"). 

name _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Name of the _answerer_. 

description _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Short description of the _answerer_. 

examples _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of short examples of the usage / of query terms. 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
See [`Answerer.keywords`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer.keywords "searx.answerers.Answerer.keywords") 

_class_ searx.answerers.AnswerStorage 
    
A storage for managing the _answerers_ of SearXNG. With the [`AnswerStorage.ask`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.AnswerStorage.ask "searx.answerers.AnswerStorage.ask")” method, a caller can ask questions to all _answerers_ and receives a list of the results. 

answerer_list _:[ set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[Answerer](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer "searx.answerers._core.Answerer")]_ 
    
The list of [`Answerer`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer "searx.answerers.Answerer") in this storage. 

load_builtins() 
    
Loads `answerer.py` modules from the python packages in [git://searx/answerers](https://github.com/searxng/searxng/blob/master/searx/answerers). The python modules are wrapped by `ModuleAnswerer`. 

register_by_fqn(_fqn :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Register a [`Answerer`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer "searx.answerers.Answerer") via its fully qualified class namen(FQN). 

register(_answerer :[Answerer](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer "searx.answerers._core.Answerer")_) 
    
Register a [`Answerer`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer "searx.answerers.Answerer"). 

ask(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[BaseAnswer](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")] 
    
An answerer is identified via keywords, if there is a keyword at the first position in the `query` for which there is one or more answerers, then these are called, whereby the entire `query` is passed as argument to the answerer function. 

_class_ searx.answerers._core.ModuleAnswerer(_mod_) 
    
Bases: [`Answerer`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.Answerer "searx.answerers._core.Answerer")
A wrapper class for legacy _answerers_ where the names (keywords, answer, info) are implemented on the module level (not in a class).
Note
For internal use only! 

answer(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[BaseAnswer](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")] 
    
Function that returns a list of answers to the question/query. 

info() → [AnswererInfo](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.AnswererInfo "searx.answerers._core.AnswererInfo") 
    
Information about the _answerer_ , see [`AnswererInfo`](https://docs.searxng.org/dev/answerers/development.html#searx.answerers.AnswererInfo "searx.answerers._core.AnswererInfo").
