<!-- source: https://docs.searxng.org/dev/result_types/answer.html -->

# Answer Results
The [area answers](https://docs.searxng.org/dev/result_types/index.html#area-answer-results) is an area in which additional information can be displayed.
Typification of the _answer_ results. Results of this type are rendered in the [answers.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/elements/answers.html) template.
* * * 

_class_ searx.result_types.answer.BaseAnswer(_*_ , _url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _engine :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=''_, _parsed_url :[ParseResult](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
Bases: [`Result`](https://docs.searxng.org/dev/result_types/base_result.html#searx.result_types._base.Result "searx.result_types._base.Result")
Base class of all answer types. It is not intended to build instances of this class (aka _abstract_). 

_class_ searx.result_types.answer.Answer(_*_ , _url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _engine :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=''_, _parsed_url :[ParseResult](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _template :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='answer/legacy.html'_, _answer :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Bases: [`BaseAnswer`](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")
Simple answer type where the _answer_ is a simple string with an optional `url field` field to link a resource (article, map, ..) related to the answer. 

answer _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Text of the answer. 

_class_ searx.result_types.answer.Translations(_*_ , _url :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _engine :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=''_, _parsed_url :[ParseResult](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _template :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='answer/translations.html'_, _translations :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[Item](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.Translations.Item "searx.result_types.answer.Translations.Item")]_) 
    
Bases: [`BaseAnswer`](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")
Answer type with a list of translations.
The items in the list of [`Translations.translations`](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.Translations.translations "searx.result_types.answer.Translations.translations") are of type [`Translations.Item`](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.Translations.Item "searx.result_types.answer.Translations.Item"):
```
def response(resp):
    results = []
    ...
    foo_1 = Translations.Item(
        text="foobar",
        synonyms=["bar", "foo"],
        examples=["foo and bar are placeholders"],
    )
    foo_url="https://www.deepl.com/de/translator#en/de/foo"
    ...
    Translations(results=results, translations=[foo], url=foo_url)

```

template _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
The template in [answer/translations.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/answer/translations.html) 

translations _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[Translations.Item](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.Translations.Item "searx.result_types.answer.Translations.Item")]_ 
    
List of translations. 

_class_ Item(_*_ , _text: str_, _transliteration: str = ''_, _examples: list[str] = <factory>_, _definitions: list[str] = <factory>_, _synonyms: list[str] = <factory>_) 
    
Bases: `Struct`
A single element of the translations / a translation. A translation consists of at least a mandatory `text` property (the translation) , optional properties such as _definitions_ , _synonyms_ and _examples_ are possible. 

text _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Translated text. 

transliteration _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
[Transliteration](https://en.wikipedia.org/wiki/Transliteration) of the requested translation. 

examples _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of examples for the requested translation. 

definitions _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of definitions for the requested translation. 

synonyms _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_ 
    
List of synonyms for the requested translation. 

_class_ searx.result_types.answer.WeatherAnswer(_*_ , _url: str | None = None_, _engine: str | None = ''_, _parsed_url: ~urllib.parse.ParseResult | None = None_, _template: str = 'answer/weather.html'_, _current: ~searx.result_types.answer.WeatherAnswer.Item_, _forecasts: list[~searx.result_types.answer.WeatherAnswer.Item] = <factory>_, _service: str = ''_) 
    
Bases: [`BaseAnswer`](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer")
Answer type for weather data. 

template _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
The template is located at [answer/weather.html](https://github.com/searxng/searxng/blob/master/searx/templates/simple/answer/weather.html) 

current _:[ WeatherAnswer.Item](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.WeatherAnswer.Item "searx.result_types.answer.WeatherAnswer.Item")_ 
    
Current weather at `location`. 

forecasts _:[ list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[WeatherAnswer.Item](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.WeatherAnswer.Item "searx.result_types.answer.WeatherAnswer.Item")]_ 
    
Weather forecasts for `location`. 

service _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ 
    
Weather service from which this information was provided. 

_class_ Item(_*_ , _location :[GeoLocation](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation")_, _temperature :[Temperature](https://docs.searxng.org/src/searx.weather.html#searx.weather.Temperature "searx.weather.Temperature")_, _condition :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['clear sky','partly cloudy','cloudy','fair','fog','light rain and thunder','light rain showers and thunder','light rain showers','light rain','rain and thunder','rain showers and thunder','rain showers','rain','heavy rain and thunder','heavy rain showers and thunder','heavy rain showers','heavy rain','light sleet and thunder','light sleet showers and thunder','light sleet showers','light sleet','sleet and thunder','sleet showers and thunder','sleet showers','sleet','heavy sleet and thunder','heavy sleet showers and thunder','heavy sleet showers','heavy sleet','light snow and thunder','light snow showers and thunder','light snow showers','light snow','snow and thunder','snow showers and thunder','snow showers','snow','heavy snow and thunder','heavy snow showers and thunder','heavy snow showers','heavy snow']_, _datetime :[DateTime](https://docs.searxng.org/src/searx.weather.html#searx.weather.DateTime "searx.weather.DateTime")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _summary :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _feels_like :[Temperature](https://docs.searxng.org/src/searx.weather.html#searx.weather.Temperature "searx.weather.Temperature")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _pressure :[Pressure](https://docs.searxng.org/src/searx.weather.html#searx.weather.Pressure "searx.weather.Pressure")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _humidity :[RelativeHumidity](https://docs.searxng.org/src/searx.weather.html#searx.weather.RelativeHumidity "searx.weather.RelativeHumidity")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _wind_from :[Compass](https://docs.searxng.org/src/searx.weather.html#searx.weather.Compass "searx.weather.Compass")_, _wind_speed :[WindSpeed](https://docs.searxng.org/src/searx.weather.html#searx.weather.WindSpeed "searx.weather.WindSpeed")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _cloud_cover :[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) 
    
Bases: `Struct`
Weather parameters valid for a specific point in time. 

location _:[ GeoLocation](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation")_ 
    
The geo-location the weather data is from (e.g. Berlin, Germany). 

temperature _:[ Temperature](https://docs.searxng.org/src/searx.weather.html#searx.weather.Temperature "searx.weather.Temperature")_ 
    
Air temperature at 2m above the ground. 

condition _:[ Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['clear sky','partly cloudy','cloudy','fair','fog','light rain and thunder','light rain showers and thunder','light rain showers','light rain','rain and thunder','rain showers and thunder','rain showers','rain','heavy rain and thunder','heavy rain showers and thunder','heavy rain showers','heavy rain','light sleet and thunder','light sleet showers and thunder','light sleet showers','light sleet','sleet and thunder','sleet showers and thunder','sleet showers','sleet','heavy sleet and thunder','heavy sleet showers and thunder','heavy sleet showers','heavy sleet','light snow and thunder','light snow showers and thunder','light snow showers','light snow','snow and thunder','snow showers and thunder','snow showers','snow','heavy snow and thunder','heavy snow showers and thunder','heavy snow showers','heavy snow']_ 
    
Standardized designations that summarize the weather situation (e.g. `light sleet showers and thunder`). 

datetime _:[ DateTime](https://docs.searxng.org/src/searx.weather.html#searx.weather.DateTime "searx.weather.DateTime")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Time of the forecast - not needed for the current weather. 

summary _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
One-liner about the weather forecast / current weather conditions. If unset, a summary is build up from temperature and current weather conditions. 

feels_like _:[ Temperature](https://docs.searxng.org/src/searx.weather.html#searx.weather.Temperature "searx.weather.Temperature")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Apparent temperature, the temperature equivalent perceived by humans, caused by the combined effects of air temperature, relative humidity and wind speed. The measure is most commonly applied to the perceived outdoor temperature. 

pressure _:[ Pressure](https://docs.searxng.org/src/searx.weather.html#searx.weather.Pressure "searx.weather.Pressure")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Air pressure at sea level (e.g. 1030 hPa) 

humidity _:[ RelativeHumidity](https://docs.searxng.org/src/searx.weather.html#searx.weather.RelativeHumidity "searx.weather.RelativeHumidity")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Amount of relative humidity in the air at 2m above the ground. The unit is `%`, e.g. 60%) 

wind_from _:[ Compass](https://docs.searxng.org/src/searx.weather.html#searx.weather.Compass "searx.weather.Compass")_ 
    
The directon which moves towards / direction the wind is coming from. 

wind_speed _:[ WindSpeed](https://docs.searxng.org/src/searx.weather.html#searx.weather.WindSpeed "searx.weather.WindSpeed")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Speed of wind / wind speed at 10m above the ground (10 min average). 

cloud_cover _:[ int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Amount of sky covered by clouds / total cloud cover for all heights (cloudiness, unit: %) 

_property_ url _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ 
    
Determines a [data URL](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data) with a symbol for the weather conditions. If no symbol can be assigned, `None` is returned. 

_class_ searx.result_types.answer.AnswerSet 
    
Bases: [`object`](https://docs.python.org/3/library/functions.html#object "\(in Python v3.14\)")
Aggregator for [`BaseAnswer`](https://docs.searxng.org/dev/result_types/answer.html#searx.result_types.answer.BaseAnswer "searx.result_types.answer.BaseAnswer") items in a result container.
