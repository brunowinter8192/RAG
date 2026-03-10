<!-- source: https://docs.searxng.org/dev/engines/online/soundcloud.html -->

# Soundcloud
SoundCloud is a German audio streaming service. 

**engines.soundcloud.search_url** = `'https://api-v2.soundcloud.com/search'`
This is not the official (developer) url, it is the API which is used by the HTML frontend of the common WEB site. 

searx.engines.soundcloud.CACHE _:[ EngineCache](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.EngineCache "searx.enginelib.EngineCache")_ 
    
Persistent (SQLite) key/value cache that deletes its values after `expire` seconds.
