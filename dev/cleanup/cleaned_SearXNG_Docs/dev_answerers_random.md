<!-- source: https://docs.searxng.org/dev/answerers/random.html -->

# Random 

_class_ searx.answerers.random.SXNGAnswerer 
    
Random value generator 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__=['random']_ 
    
Keywords to which the answerer has _answers_. 

info() 
    
Information about the _answerer_ , see `AnswererInfo`. 

answer(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[BaseAnswer](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")] 
    
Function that returns a list of answers to the question/query.
