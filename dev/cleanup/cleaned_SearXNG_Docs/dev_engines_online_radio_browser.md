<!-- source: https://docs.searxng.org/dev/engines/online/radio_browser.html -->

# RadioBrowser
Search radio stations from RadioBrowser by [Advanced station search API](https://de1.api.radio-browser.info/#Advanced_station_search). 

**engines.radio_browser.station_filters** = `[]`
A list of filters to be applied to the search of radio stations. By default none filters are applied. Valid filters are: 

`language`
    
Filter stations by selected language. For instance the `de` from `:de-AU` will be translated to german and used in the argument `language=`. 

`countrycode`
    
Filter stations by selected country. The 2-digit countrycode of the station comes from the region the user selected. For instance `:de-AU` will filter out all stations not in `AU`.
Note
RadioBrowser has registered a lot of languages and countrycodes unknown to `babel` and note that when searching for radio stations, users are more likely to search by name than by region or language. 

searx.engines.radio_browser.CACHE _:[ EngineCache](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.EngineCache "searx.enginelib.EngineCache")_ 
    
Persistent (SQLite) key/value cache that deletes its values after `expire` seconds. 

searx.engines.radio_browser.fetch_traits(_engine_traits :[EngineTraits](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.traits.EngineTraits "searx.enginelib.traits.EngineTraits")_) 
    
Fetch languages and countrycodes from RadioBrowser
  * `traits.languages`: [list of languages API](https://de1.api.radio-browser.info/#List_of_languages)
  * `traits.custom['countrycodes']`: [list of countries API](https://de1.api.radio-browser.info/#List_of_countries)
