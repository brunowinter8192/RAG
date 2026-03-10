<!-- source: https://docs.searxng.org/src/searx.weather.html -->

# Weather
Implementations used for weather conditions and forecast. 

searx.weather.symbol_url(_condition :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['clear sky','partly cloudy','cloudy','fair','fog','light rain and thunder','light rain showers and thunder','light rain showers','light rain','rain and thunder','rain showers and thunder','rain showers','rain','heavy rain and thunder','heavy rain showers and thunder','heavy rain showers','heavy rain','light sleet and thunder','light sleet showers and thunder','light sleet showers','light sleet','sleet and thunder','sleet showers and thunder','sleet showers','sleet','heavy sleet and thunder','heavy sleet showers and thunder','heavy sleet showers','heavy sleet','light snow and thunder','light snow showers and thunder','light snow showers','light snow','snow and thunder','snow showers and thunder','snow showers','snow','heavy snow and thunder','heavy snow showers and thunder','heavy snow showers','heavy snow']_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Returns `data:` URL for the weather condition symbol or `None` if the condition is not of type [`WeatherConditionType`](https://docs.searxng.org/src/searx.weather.html#searx.weather.WeatherConditionType "searx.weather.WeatherConditionType").
If symbol (SVG) is not already in the `WEATHER_DATA_CACHE` its fetched from <https://github.com/nrkno/yr-weather-symbols> 

_class_ searx.weather.Temperature(_*_ , _val :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _unit :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['°C','°F','K']_) 
    
Class for converting temperature units and for string representation of measured values. 

l10n(_unit :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['°C','°F','K']|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _locale :[Locale](https://babel.readthedocs.io/en/latest/api/core.html#babel.core.Locale "\(in Babel v2.2\)")|[GeoLocation](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _template :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='{value} {unit}'_, _num_pattern :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='#,##0'_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Localized representation of a measured value.
If the `unit` is not set, an attempt is made to determine a `unit` matching the territory of the `locale`. If the locale is not set, an attempt is made to determine it from the HTTP request.
The value is converted into the respective unit before formatting.
The argument `num_pattern` is used to determine the string formatting of the numerical value:
  * <https://babel.pocoo.org/en/latest/numbers.html#pattern-syntax>
  * <https://unicode.org/reports/tr35/tr35-numbers.html#Number_Format_Patterns>

The argument `template` specifies how the **string formatted** value and unit are to be arranged.
  * Format Specification Mini-Language <https://docs.python.org/3/library/string.html#format-specification-mini-language>.

_class_ searx.weather.Pressure(_*_ , _val :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _unit :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['Pa','hPa','cm Hg','bar']_) 
    
Class for converting pressure units and for string representation of measured values. 

_class_ searx.weather.WindSpeed(_*_ , _val :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _unit :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['m/s','km/h','kn','mph','mi/h','Bft']_) 
    
Class for converting speed or velocity units and for string representation of measured values.
Hint
Working with unit `Bft` (`searx.wikidata_units.Beaufort`) will throw a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") for egative values or values greater 16 Bft (55.6 m/s) 

_class_ searx.weather.RelativeHumidity(_val :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_) 
    
Amount of relative humidity in the air. The unit is `%` 

_class_ searx.weather.Compass(_val :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")|[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")|[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']_, _unit :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['°','Point']='°'_) 
    
Class for converting compass points and azimuth values (360°) 

TURN _:[ ClassVar](https://docs.python.org/3/library/typing.html#typing.ClassVar "\(in Python v3.14\)")[[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")]__= 360.0_ 
    
Full turn (360°) 

POINTS _:[ ClassVar](https://docs.python.org/3/library/typing.html#typing.ClassVar "\(in Python v3.14\)")[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']]]__=('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW')_ 
    
Compass points. 

RANGE _:[ ClassVar](https://docs.python.org/3/library/typing.html#typing.ClassVar "\(in Python v3.14\)")[[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")]__= 22.5_ 
    
Angle sector of a compass point 

_classmethod_ point(_azimuth :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")|[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_) → [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'] 
    
Returns the compass point to an azimuth value. 

searx.weather.WeatherConditionType 
    
Standardized designations for weather conditions. The designators were taken from a collaboration between NRK and Norwegian Meteorological Institute ([yr.no](https://www.yr.no/en)). [Weather symbols](https://github.com/nrkno/yr-weather-symbols) can be assigned to the identifiers ([weathericons](https://github.com/metno/weathericons)) and they are included in the translation (i18n/l10n [git://searx/searxng.msg](https://github.com/searxng/searxng/blob/master/searx/searxng.msg)).
alias of [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")[‘clear sky’, ‘partly cloudy’, ‘cloudy’, ‘fair’, ‘fog’, ‘light rain and thunder’, ‘light rain showers and thunder’, ‘light rain showers’, ‘light rain’, ‘rain and thunder’, ‘rain showers and thunder’, ‘rain showers’, ‘rain’, ‘heavy rain and thunder’, ‘heavy rain showers and thunder’, ‘heavy rain showers’, ‘heavy rain’, ‘light sleet and thunder’, ‘light sleet showers and thunder’, ‘light sleet showers’, ‘light sleet’, ‘sleet and thunder’, ‘sleet showers and thunder’, ‘sleet showers’, ‘sleet’, ‘heavy sleet and thunder’, ‘heavy sleet showers and thunder’, ‘heavy sleet showers’, ‘heavy sleet’, ‘light snow and thunder’, ‘light snow showers and thunder’, ‘light snow showers’, ‘light snow’, ‘snow and thunder’, ‘snow showers and thunder’, ‘snow showers’, ‘snow’, ‘heavy snow and thunder’, ‘heavy snow showers and thunder’, ‘heavy snow showers’, ‘heavy snow’] 

_class_ searx.weather.DateTime 
    
Class to represent date & time. Essentially, it is a wrapper that conveniently combines [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime "\(in Python v3.14\)") and [`babel.dates.format_datetime`](https://babel.readthedocs.io/en/latest/api/dates.html#babel.dates.format_datetime "\(in Babel v2.2\)"). A conversion of time zones is not provided (in the current version).
The localized string representation can be obtained via the [`DateTime.l10n`](https://docs.searxng.org/src/searx.weather.html#searx.weather.DateTime.l10n "searx.weather.DateTime.l10n") and [`DateTime.l10n_date`](https://docs.searxng.org/src/searx.weather.html#searx.weather.DateTime.l10n_date "searx.weather.DateTime.l10n_date") methods, where the `locale` parameter defaults to the search language. Alternatively, a [`GeoLocation`](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation") or a `babel.Locale` instance can be passed directly. If the UI language is to be used, the string `UI` can be passed as the value for the `locale`. 

l10n(_fmt :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['full','long','medium','short']|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='medium'_, _locale :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['UI']|[Locale](https://babel.readthedocs.io/en/latest/api/core.html#babel.core.Locale "\(in Babel v2.2\)")|[GeoLocation](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Localized representation of date & time. 

l10n_date(_fmt :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['full','long','medium','short']|[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")='medium'_, _locale :[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['UI']|[Locale](https://babel.readthedocs.io/en/latest/api/core.html#babel.core.Locale "\(in Babel v2.2\)")|[GeoLocation](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Localized representation of date. 

_class_ searx.weather.GeoLocation(_*_ , _name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _latitude :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _longitude :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _elevation :[float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_, _country_code :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _timezone :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) 
    
Minimal implementation of Geocoding. 

_classmethod_ by_query(_search_term :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [GeoLocation](https://docs.searxng.org/src/searx.weather.html#searx.weather.GeoLocation "searx.weather.GeoLocation") 
    
Factory method to get a GeoLocation object by a search term. If no location can be determined for the search term, a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") is thrown.
