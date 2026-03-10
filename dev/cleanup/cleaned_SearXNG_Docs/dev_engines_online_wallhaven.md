<!-- source: https://docs.searxng.org/dev/engines/online/wallhaven.html -->

# Wallhaven
[Wallhaven](https://wallhaven.cc/about#Copyright) is a site created by and for people who like wallpapers. 

**engines.wallhaven.api_key** = `''`
If you own an API key you can add it here, further read [Rate Limiting and Errors](https://wallhaven.cc/help/api#limits). 

**engines.wallhaven.safesearch_map** = `{0: '111', 1: '110', 2: '100'}`
Turn purities on(1) or off(0) NSFW requires a valid API key.
```
100/110/111 <-- Bits stands for: SFW, Sketchy and NSFW

```

[What are SFW, Sketchy and NSFW all about?](https://wallhaven.cc/faq#What-are-SFW-Sketchy-and-NSFW-all-about):
  * SFW = “Safe for work” wallpapers. _Grandma approves._
  * Sketchy = Not quite SFW not quite NSFW. _Grandma might be uncomfortable._
  * NSFW = “Not safe for work”. _Grandma isn’t sure who you are anymore._
