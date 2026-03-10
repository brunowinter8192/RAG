<!-- source: https://docs.searxng.org/src/searx.exceptions.html -->

# SearXNG Exceptions
Exception types raised by SearXNG modules. 

_exception_ searx.exceptions.SearxException 
    
Base SearXNG exception. 

_exception_ searx.exceptions.SearxParameterException(_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _value :[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_) 
    
Raised when query miss a required parameter 

_final exception_searx.exceptions.SearxSettingsException(_message :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[Exception](https://docs.python.org/3/library/exceptions.html#Exception "\(in Python v3.14\)")_, _filename :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_) 
    
Error while loading the settings 

_exception_ searx.exceptions.SearxEngineException 
    
Error inside an engine 

_exception_ searx.exceptions.SearxXPathSyntaxException(_xpath_spec :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|XPath_, _message :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Syntax error in a XPATH 

_exception_ searx.exceptions.SearxEngineResponseException 
    
Impossible to parse the result of an engine 

_exception_ searx.exceptions.SearxEngineAPIException 
    
The website has returned an application error 

_exception_ searx.exceptions.SearxEngineAccessDeniedException(_suspended_time :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _message :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='Access denied'_) 
    
The website is blocking the access 

SUSPEND_TIME_SETTING _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'search.suspended_times.SearxEngineAccessDenied'_ 
    
This settings contains the default suspended time (default 86400 sec / 1 day). 

_exception_ searx.exceptions.SearxEngineCaptchaException(_suspended_time :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _message :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='CAPTCHA'_) 
    
The website has returned a CAPTCHA. 

SUSPEND_TIME_SETTING _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'search.suspended_times.SearxEngineCaptcha'_ 
    
This settings contains the default suspended time (default 86400 sec / 1 day). 

_exception_ searx.exceptions.SearxEngineTooManyRequestsException(_suspended_time :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _message :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='Too many request'_) 
    
The website has returned a Too Many Request status code
By default, SearXNG stops sending requests to this engine for 1 hour. 

SUSPEND_TIME_SETTING _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _= 'search.suspended_times.SearxEngineTooManyRequests'_ 
    
This settings contains the default suspended time (default 3660 sec / 1 hour). 

_exception_ searx.exceptions.SearxEngineXPathException(_xpath_spec :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|XPath_, _message :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Error while getting the result of an XPath expression
