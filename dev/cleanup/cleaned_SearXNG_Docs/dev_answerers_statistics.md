<!-- source: https://docs.searxng.org/dev/answerers/statistics.html -->

# Statistics 

_class_ searx.answerers.statistics.SXNGAnswerer 
    
Statistics functions 

keywords _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__=['min', 'max', 'avg', 'sum', 'prod', 'range']_ 
    
Keywords to which the answerer has _answers_. 

info() 
    
Information about the _answerer_ , see `AnswererInfo`. 

answer(_query :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[BaseAnswer](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")] 
    
Function that returns a list of answers to the question/query.
