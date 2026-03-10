<!-- source: https://docs.searxng.org/user/configured_engines.html -->

# Configured Engines
Further reading ..
SearXNG supports 243 search engines of which 89 are enabled by default.
Engines can be assigned to multiple [categories](https://docs.searxng.org/admin/settings/settings_engines.html#engine-categories). The UI displays the tabs that are configured in [categories_as_tabs](https://docs.searxng.org/admin/settings/settings_categories_as_tabs.html#settings-categories-as-tabs). In addition to these UI categories (also called _tabs_), engines can be queried by their name or the categories they belong to, by using a [!bing syntax](https://docs.searxng.org/user/search-syntax.html#search-syntax).
## tab `!general`
### group `!books`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[openlibrary](https://openlibrary.org) | `!ol` | [`openlibrary`](https://docs.searxng.org/dev/engines/online/openlibrary.html#module-searx.engines.openlibrary "searx.engines.openlibrary") | y | 10 | 1 | y |  |  |   
### group `!currency`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[currency](https://duckduckgo.com/) | `!cc` | [currency_convert](https://github.com/searxng/searxng/blob/master/searx/engines/currency_convert.py) |  | 3.0 | 100 |  not applicable (online_currency)  
### group `!translate`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[dictzone](https://dictzone.com/) | `!dc` | [dictzone](https://github.com/searxng/searxng/blob/master/searx/engines/dictzone.py) |  | 3.0 | 100 |  not applicable (online_dictionary)  
[lingva](https://lingva.ml) | `!lv` | [lingva](https://github.com/searxng/searxng/blob/master/searx/engines/lingva.py) |  | 3.0 | 1 |  not applicable (online_dictionary)  
[mozhi](https://codeberg.org/aryak/mozhi) | `!mz` | [mozhi](https://github.com/searxng/searxng/blob/master/searx/engines/mozhi.py) | y | 4.0 | 1 |  not applicable (online_dictionary)  
[mymemory translated](https://mymemory.translated.net/) | `!tl` | [translated](https://github.com/searxng/searxng/blob/master/searx/engines/translated.py) |  | 5.0 | 100 |  not applicable (online_dictionary)  
### group `!web`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[bing](https://www.bing.com) | `!bi` | [`bing`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing "searx.engines.bing") | y | 3.0 | 1 | y | y | y | y  
[brave](https://search.brave.com/) | `!br` | [`brave`](https://docs.searxng.org/dev/engines/online/brave.html#module-searx.engines.brave "searx.engines.brave") |  | 3.0 | 1 | y | y | y | y  
[duckduckgo](https://lite.duckduckgo.com/lite/) | `!ddg` | [`duckduckgo`](https://docs.searxng.org/dev/engines/online/duckduckgo.html#module-searx.engines.duckduckgo "searx.engines.duckduckgo") |  | 3.0 | 1 | y | y | y | y  
[google](https://www.google.com) | `!go` | [`google`](https://docs.searxng.org/dev/engines/online/google.html#module-searx.engines.google "searx.engines.google") |  | 3.0 | 1 | y | y | y | y  
[mojeek](https://mojeek.com) | `!mjk` | [mojeek](https://github.com/searxng/searxng/blob/master/searx/engines/mojeek.py) | y | 3.0 | 1 | y | y | y | y  
[presearch](https://presearch.io) | `!ps` | [`presearch`](https://docs.searxng.org/dev/engines/online/presearch.html#module-searx.engines.presearch "searx.engines.presearch") | y | 4.0 | 1 | y |  | y | y  
[presearch videos](https://presearch.io) | `!psvid` | [`presearch`](https://docs.searxng.org/dev/engines/online/presearch.html#module-searx.engines.presearch "searx.engines.presearch") | y | 4.0 | 1 | y |  | y | y  
[qwant](https://www.qwant.com/) | `!qw` | [`qwant`](https://docs.searxng.org/dev/engines/online/qwant.html#module-searx.engines.qwant "searx.engines.qwant") | y | 3.0 | 1 | y | y | y |   
[startpage](https://startpage.com) | `!sp` | [`startpage`](https://docs.searxng.org/dev/engines/online/startpage.html#module-searx.engines.startpage "searx.engines.startpage") |  | 3.0 | 1 | y | y | y | y  
[wiby](https://wiby.me/) | `!wib` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") | y | 3.0 | 1 | y |  |  |   
[yahoo](https://search.yahoo.com/) | `!yh` | [`yahoo`](https://docs.searxng.org/dev/engines/online/yahoo.html#module-searx.engines.yahoo "searx.engines.yahoo") | y | 3.0 | 1 | y |  |  | y  
[seznam](https://www.seznam.cz/) (CZ) | `!szn` | [seznam](https://github.com/searxng/searxng/blob/master/searx/engines/seznam.py) | y | 3.0 | 1 |  |  |  |   
[naver](https://search.naver.com) (KO) | `!nvr` | [naver](https://github.com/searxng/searxng/blob/master/searx/engines/naver.py) | y | 3.0 | 1 | y |  |  | y  
### group `!wikimedia`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[wikibooks](https://www.wikibooks.org/) | `!wb` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 0.5 | y |  |  |   
[wikiquote](https://www.wikiquote.org/) | `!wq` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 0.5 | y |  |  |   
[wikisource](https://www.wikisource.org/) | `!ws` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 0.5 | y |  |  |   
[wikispecies](https://species.wikimedia.org/) | `!wsp` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 1 | y |  |  |   
[wikiversity](https://www.wikiversity.org/) | `!wv` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 0.5 | y |  |  |   
[wikivoyage](https://www.wikivoyage.org/) | `!wy` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 0.5 | y |  |  |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[ask](https://www.ask.com/) | `!ask` | [ask](https://github.com/searxng/searxng/blob/master/searx/engines/ask.py) | y | 3.0 | 1 | y |  |  |   
[crowdview](https://crowdview.ai/) | `!cv` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") | y | 3.0 | 1 |  |  |  |   
[ddg definitions](https://duckduckgo.com/) | `!ddd` | [`duckduckgo_definitions`](https://docs.searxng.org/dev/engines/online/duckduckgo.html#module-searx.engines.duckduckgo_definitions "searx.engines.duckduckgo_definitions") | y | 3.0 | 2 |  |  |  |   
[encyclosearch](https://encyclosearch.org) | `!es` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") | y | 3.0 | 1 | y |  |  |   
[fynd](https://fynd.bot) | `!fynd` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 3.0 | 1 | y |  | y |   
[mwmbl](https://github.com/mwmbl/mwmbl) | `!mwm` | [`mwmbl`](https://docs.searxng.org/dev/engines/online/mwmbl.html#module-searx.engines.mwmbl "searx.engines.mwmbl") | y | 3.0 | 1 |  |  |  |   
[right dao](https://rightdao.com/) | `!rd` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 3.0 | 1 | y |  |  |   
[searchmysite](https://searchmysite.net) | `!sms` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 3.0 | 1 | y |  |  |   
[tineye](https://tineye.com) | `!tin` | [`tineye`](https://docs.searxng.org/dev/engines/online_url_search/tineye.html#module-searx.engines.tineye "searx.engines.tineye") | y | 9.0 | 1 |  not applicable (online_url_search)  
[wikidata](https://wikidata.org/) | `!wd` | [`wikidata`](https://docs.searxng.org/dev/engines/online/wikipedia.html#module-searx.engines.wikidata "searx.engines.wikidata") |  | 3.0 | 2 |  | y |  |   
[wikipedia](https://www.wikipedia.org/) | `!wp` | [`wikipedia`](https://docs.searxng.org/dev/engines/online/wikipedia.html#module-searx.engines.wikipedia "searx.engines.wikipedia") |  | 3.0 | 1 |  | y |  |   
[wolframalpha](https://www.wolframalpha.com/) | `!wa` | [wolframalpha_noapi](https://github.com/searxng/searxng/blob/master/searx/engines/wolframalpha_noapi.py) | y | 6.0 | 1 |  |  |  |   
[yacy](https://yacy.net/) | `!ya` | [`yacy`](https://docs.searxng.org/dev/engines/online/yacy.html#module-searx.engines.yacy "searx.engines.yacy") | y | 5.0 | 1 | y |  |  |   
[yandex](https://yandex.com/) | `!yd` | [yandex](https://github.com/searxng/searxng/blob/master/searx/engines/yandex.py) | y | 3.0 | 1 | y |  |  |   
[yep](https://yep.com/) | `!yep` | [yep](https://github.com/searxng/searxng/blob/master/searx/engines/yep.py) | y | 15 | 1 |  |  | y |   
[bpb](https://www.bpb.de) (DE) | `!bpb` | [`bpb`](https://docs.searxng.org/dev/engines/online/bpb.html#module-searx.engines.bpb "searx.engines.bpb") | y | 3.0 | 1 | y |  |  |   
[tagesschau](https://tagesschau.de) (DE) | `!ts` | [`tagesschau`](https://docs.searxng.org/dev/engines/online/tagesschau.html#module-searx.engines.tagesschau "searx.engines.tagesschau") | y | 3.0 | 1 | y |  |  |   
[wikimini](https://wikimini.org/) (FR) | `!wkmn` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 3.0 | 1 |  |  |  |   
[360search](https://www.so.com/) (ZH) | `!360so` | [360search](https://github.com/searxng/searxng/blob/master/searx/engines/360search.py) | y | 10.0 | 1 | y |  |  | y  
[baidu](https://www.baidu.com) (ZH) | `!bd` | [baidu](https://github.com/searxng/searxng/blob/master/searx/engines/baidu.py) | y | 3.0 | 1 | y |  |  | y  
[quark](https://quark.sm.cn/) (ZH) | `!qk` | [quark](https://github.com/searxng/searxng/blob/master/searx/engines/quark.py) | y | 3.0 | 1 | y |  |  | y  
[sogou](https://www.sogou.com/) (ZH) | `!sogou` | [sogou](https://github.com/searxng/searxng/blob/master/searx/engines/sogou.py) | y | 3.0 | 1 | y |  |  | y  
## tab `!images`
### group `!icons`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[devicons](https://devicon.dev/) | `!di` | [devicons](https://github.com/searxng/searxng/blob/master/searx/engines/devicons.py) |  | 3.0 | 1 |  |  |  |   
[lucide](https://lucide.dev/) | `!luc` | [lucide](https://github.com/searxng/searxng/blob/master/searx/engines/lucide.py) |  | 3.0 | 1 |  |  |  |   
[material icons](https://fonts.google.com/icons) | `!mi` | [material_icons](https://github.com/searxng/searxng/blob/master/searx/engines/material_icons.py) | y | 3.0 | 1 |  |  |  |   
[selfhst icons](https://selfh.st/icons/) | `!si` | [selfhst](https://github.com/searxng/searxng/blob/master/searx/engines/selfhst.py) | y | 3.0 | 1 |  |  |  |   
[svgrepo](https://www.svgrepo.com) | `!svg` | [svgrepo](https://github.com/searxng/searxng/blob/master/searx/engines/svgrepo.py) | y | 10.0 | 1 | y |  |  |   
[uxwing](https://uxwing.com) | `!ux` | [uxwing](https://github.com/searxng/searxng/blob/master/searx/engines/uxwing.py) | y | 3.0 | 1 |  |  |  |   
### group `!web`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[bing images](https://www.bing.com/images) | `!bii` | [`bing_images`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing_images "searx.engines.bing_images") |  | 3.0 | 1 | y | y | y | y  
[brave.images](https://search.brave.com/) | `!brimg` | [`brave`](https://docs.searxng.org/dev/engines/online/brave.html#module-searx.engines.brave "searx.engines.brave") |  | 3.0 | 1 |  | y | y |   
[google images](https://images.google.com) | `!goi` | [`google_images`](https://docs.searxng.org/dev/engines/online/google.html#module-searx.engines.google_images "searx.engines.google_images") |  | 3.0 | 1 | y | y | y | y  
[mojeek images](https://mojeek.com) | `!mjkimg` | [mojeek](https://github.com/searxng/searxng/blob/master/searx/engines/mojeek.py) | y | 3.0 | 1 |  | y | y | y  
[presearch images](https://presearch.io) | `!psimg` | [`presearch`](https://docs.searxng.org/dev/engines/online/presearch.html#module-searx.engines.presearch "searx.engines.presearch") | y | 4.0 | 1 | y |  | y | y  
[qwant images](https://www.qwant.com/) | `!qwi` | [`qwant`](https://docs.searxng.org/dev/engines/online/qwant.html#module-searx.engines.qwant "searx.engines.qwant") |  | 3.0 | 1 | y | y | y |   
[startpage images](https://startpage.com) | `!spi` | [`startpage`](https://docs.searxng.org/dev/engines/online/startpage.html#module-searx.engines.startpage "searx.engines.startpage") |  | 3.0 | 1 | y | y | y | y  
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[1x](https://1x.com/) | `!1x` | [www1x](https://github.com/searxng/searxng/blob/master/searx/engines/www1x.py) | y | 3.0 | 1 |  |  |  |   
[adobe stock](https://stock.adobe.com/) | `!asi` | [`adobe_stock`](https://docs.searxng.org/dev/engines/online/adobe_stock.html#module-searx.engines.adobe_stock "searx.engines.adobe_stock") | y | 6 | 1 | y |  |  |   
[artic](https://www.artic.edu) | `!arc` | [artic](https://github.com/searxng/searxng/blob/master/searx/engines/artic.py) |  | 4.0 | 1 | y |  |  |   
[artstation](https://www.artstation.com/) | `!as` | [artstation](https://github.com/searxng/searxng/blob/master/searx/engines/artstation.py) | y | 3.0 | 1 | y |  |  |   
[deviantart](https://www.deviantart.com/) | `!da` | [deviantart](https://github.com/searxng/searxng/blob/master/searx/engines/deviantart.py) |  | 3.0 | 1 | y |  |  |   
[duckduckgo images](https://duckduckgo.com/) | `!ddi` | [`duckduckgo_extra`](https://docs.searxng.org/dev/engines/online/duckduckgo.html#module-searx.engines.duckduckgo_extra "searx.engines.duckduckgo_extra") |  | 3.0 | 1 | y | y | y |   
[findthatmeme](https://findthatmeme.com) | `!ftm` | [findthatmeme](https://github.com/searxng/searxng/blob/master/searx/engines/findthatmeme.py) | y | 3.0 | 1 | y |  |  |   
[flickr](https://www.flickr.com) | `!fl` | [flickr_noapi](https://github.com/searxng/searxng/blob/master/searx/engines/flickr_noapi.py) |  | 3.0 | 1 | y |  |  | y  
[frinkiac](https://frinkiac.com) | `!frk` | [frinkiac](https://github.com/searxng/searxng/blob/master/searx/engines/frinkiac.py) | y | 3.0 | 1 |  |  |  |   
[imgur](https://imgur.com/) | `!img` | [imgur](https://github.com/searxng/searxng/blob/master/searx/engines/imgur.py) | y | 3.0 | 1 | y |  |  | y  
[ipernity](https://www.ipernity.com) | `!ip` | [ipernity](https://github.com/searxng/searxng/blob/master/searx/engines/ipernity.py) | y | 3.0 | 1 | y |  |  |   
[library of congress](https://www.loc.gov/pictures/) | `!loc` | [`loc`](https://docs.searxng.org/dev/engines/online/loc.html#module-searx.engines.loc "searx.engines.loc") | y | 3.0 | 1 | y |  |  |   
[openverse](https://openverse.org/) | `!opv` | [openverse](https://github.com/searxng/searxng/blob/master/searx/engines/openverse.py) |  | 3.0 | 1 | y |  |  |   
[pexels](https://www.pexels.com) | `!pe` | [pexels](https://github.com/searxng/searxng/blob/master/searx/engines/pexels.py) |  | 3.0 | 1 | y |  |  | y  
[pinterest](https://www.pinterest.com/) | `!pin` | [pinterest](https://github.com/searxng/searxng/blob/master/searx/engines/pinterest.py) |  | 3.0 | 1 | y |  |  |   
[pixabay images](https://pixabay.com) | `!pixi` | [pixabay](https://github.com/searxng/searxng/blob/master/searx/engines/pixabay.py) | y | 3.0 | 1 | y |  | y | y  
[public domain image archive](https://pdimagearchive.org) | `!pdia` | [public_domain_image_archive](https://github.com/searxng/searxng/blob/master/searx/engines/public_domain_image_archive.py) | y | 3.0 | 1 | y |  |  |   
[sogou images](https://pic.sogou.com/) | `!sogoui` | [sogou_images](https://github.com/searxng/searxng/blob/master/searx/engines/sogou_images.py) | y | 3.0 | 1 | y |  |  |   
[unsplash](https://unsplash.com) | `!us` | [unsplash](https://github.com/searxng/searxng/blob/master/searx/engines/unsplash.py) |  | 3.0 | 1 | y |  |  |   
[wikicommons.images](https://commons.wikimedia.org/) | `!wci` | [wikicommons](https://github.com/searxng/searxng/blob/master/searx/engines/wikicommons.py) |  | 3.0 | 1 | y |  |  |   
[yacy images](https://yacy.net/) | `!yai` | [`yacy`](https://docs.searxng.org/dev/engines/online/yacy.html#module-searx.engines.yacy "searx.engines.yacy") | y | 5.0 | 1 | y |  |  |   
[yandex images](https://yandex.com/) | `!ydi` | [yandex](https://github.com/searxng/searxng/blob/master/searx/engines/yandex.py) | y | 3.0 | 1 | y |  |  |   
[yep images](https://yep.com/) | `!yepi` | [yep](https://github.com/searxng/searxng/blob/master/searx/engines/yep.py) | y | 3.0 | 1 |  |  | y |   
[naver images](https://search.naver.com) (KO) | `!nvri` | [naver](https://github.com/searxng/searxng/blob/master/searx/engines/naver.py) | y | 3.0 | 1 | y |  |  | y  
[baidu images](https://www.baidu.com) (ZH) | `!bdi` | [baidu](https://github.com/searxng/searxng/blob/master/searx/engines/baidu.py) | y | 3.0 | 1 | y |  |  | y  
[quark images](https://quark.sm.cn/) (ZH) | `!qki` | [quark](https://github.com/searxng/searxng/blob/master/searx/engines/quark.py) | y | 3.0 | 1 | y |  |  | y  
## tab `!videos`
### group `!web`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[bing videos](https://www.bing.com/videos) | `!biv` | [`bing_videos`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing_videos "searx.engines.bing_videos") |  | 3.0 | 1 | y | y | y | y  
[brave.videos](https://search.brave.com/) | `!brvid` | [`brave`](https://docs.searxng.org/dev/engines/online/brave.html#module-searx.engines.brave "searx.engines.brave") |  | 3.0 | 1 |  | y | y |   
[google videos](https://www.google.com) | `!gov` | [`google_videos`](https://docs.searxng.org/dev/engines/online/google.html#module-searx.engines.google_videos "searx.engines.google_videos") |  | 3.0 | 1 | y | y | y | y  
[qwant videos](https://www.qwant.com/) | `!qwv` | [`qwant`](https://docs.searxng.org/dev/engines/online/qwant.html#module-searx.engines.qwant "searx.engines.qwant") |  | 3.0 | 1 | y | y | y |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[360search videos](https://tv.360kan.com/) | `!360sov` | [360search_videos](https://github.com/searxng/searxng/blob/master/searx/engines/360search_videos.py) | y | 3.0 | 1 | y |  |  |   
[adobe stock video](https://stock.adobe.com/) | `!asv` | [`adobe_stock`](https://docs.searxng.org/dev/engines/online/adobe_stock.html#module-searx.engines.adobe_stock "searx.engines.adobe_stock") | y | 6 | 1 | y |  |  |   
[bilibili](https://www.bilibili.com) | `!bil` | [bilibili](https://github.com/searxng/searxng/blob/master/searx/engines/bilibili.py) | y | 3.0 | 1 | y |  |  |   
[bitchute](https://bitchute.com) | `!bit` | [bitchute](https://github.com/searxng/searxng/blob/master/searx/engines/bitchute.py) | y | 3.0 | 1 | y |  |  |   
[dailymotion](https://www.dailymotion.com) | `!dm` | [`dailymotion`](https://docs.searxng.org/dev/engines/online/dailymotion.html#module-searx.engines.dailymotion "searx.engines.dailymotion") |  | 3.0 | 1 | y | y | y | y  
[duckduckgo videos](https://duckduckgo.com/) | `!ddv` | [`duckduckgo_extra`](https://docs.searxng.org/dev/engines/online/duckduckgo.html#module-searx.engines.duckduckgo_extra "searx.engines.duckduckgo_extra") |  | 3.0 | 1 | y | y | y |   
[google play movies](https://play.google.com/) | `!gpm` | [google_play](https://github.com/searxng/searxng/blob/master/searx/engines/google_play.py) | y | 3.0 | 1 |  |  |  |   
[media.ccc.de](https://media.ccc.de) | `!c3tv` | [ccc_media](https://github.com/searxng/searxng/blob/master/searx/engines/ccc_media.py) | y | 3.0 | 1 | y |  |  |   
[odysee](https://odysee.com/) | `!od` | [`odysee`](https://docs.searxng.org/dev/engines/online/odysee.html#module-searx.engines.odysee "searx.engines.odysee") | y | 3.0 | 1 | y | y |  | y  
[peertube](https://joinpeertube.org) | `!ptb` | [`peertube`](https://docs.searxng.org/dev/engines/online/peertube.html#module-searx.engines.peertube "searx.engines.peertube") | y | 6.0 | 1 | y | y | y | y  
[pixabay videos](https://pixabay.com) | `!pixv` | [pixabay](https://github.com/searxng/searxng/blob/master/searx/engines/pixabay.py) | y | 3.0 | 1 | y |  | y | y  
[rumble](https://rumble.com/) | `!ru` | [rumble](https://github.com/searxng/searxng/blob/master/searx/engines/rumble.py) | y | 3.0 | 1 | y |  |  |   
[sepiasearch](https://sepiasearch.org) | `!sep` | [`sepiasearch`](https://docs.searxng.org/dev/engines/online/peertube.html#module-searx.engines.sepiasearch "searx.engines.sepiasearch") |  | 3.0 | 1 | y | y | y | y  
[vimeo](https://vimeo.com/) | `!vm` | [vimeo](https://github.com/searxng/searxng/blob/master/searx/engines/vimeo.py) |  | 3.0 | 1 | y |  |  |   
[wikicommons.videos](https://commons.wikimedia.org/) | `!wcv` | [wikicommons](https://github.com/searxng/searxng/blob/master/searx/engines/wikicommons.py) |  | 3.0 | 1 | y |  |  |   
[youtube](https://www.youtube.com/) | `!yt` | [youtube_noapi](https://github.com/searxng/searxng/blob/master/searx/engines/youtube_noapi.py) |  | 3.0 | 1 | y |  |  | y  
[mediathekviewweb](https://mediathekviewweb.de/) (DE) | `!mvw` | [mediathekviewweb](https://github.com/searxng/searxng/blob/master/searx/engines/mediathekviewweb.py) | y | 3.0 | 1 | y |  |  |   
[ina](https://www.ina.fr/) (FR) | `!in` | [ina](https://github.com/searxng/searxng/blob/master/searx/engines/ina.py) | y | 6.0 | 1 | y |  |  |   
[niconico](https://www.nicovideo.jp/) (JA) | `!nico` | [niconico](https://github.com/searxng/searxng/blob/master/searx/engines/niconico.py) | y | 3.0 | 1 | y |  |  | y  
[naver videos](https://search.naver.com) (KO) | `!nvrv` | [naver](https://github.com/searxng/searxng/blob/master/searx/engines/naver.py) | y | 3.0 | 1 | y |  |  | y  
[acfun](https://www.acfun.cn/) (ZH) | `!acf` | [acfun](https://github.com/searxng/searxng/blob/master/searx/engines/acfun.py) | y | 3.0 | 1 | y |  |  |   
[iqiyi](https://www.iqiyi.com/) (ZH) | `!iq` | [iqiyi](https://github.com/searxng/searxng/blob/master/searx/engines/iqiyi.py) | y | 3.0 | 1 | y |  |  | y  
[sogou videos](https://v.sogou.com/) (ZH) | `!sogouv` | [sogou_videos](https://github.com/searxng/searxng/blob/master/searx/engines/sogou_videos.py) | y | 3.0 | 1 | y |  |  |   
## tab `!news`
### group `!web`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[mojeek news](https://mojeek.com) | `!mjknews` | [mojeek](https://github.com/searxng/searxng/blob/master/searx/engines/mojeek.py) | y | 3.0 | 1 |  | y | y | y  
[presearch news](https://presearch.io) | `!psnews` | [`presearch`](https://docs.searxng.org/dev/engines/online/presearch.html#module-searx.engines.presearch "searx.engines.presearch") | y | 4.0 | 1 | y |  | y | y  
[startpage news](https://startpage.com) | `!spn` | [`startpage`](https://docs.searxng.org/dev/engines/online/startpage.html#module-searx.engines.startpage "searx.engines.startpage") |  | 3.0 | 1 | y | y | y | y  
### group `!wikimedia`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[wikinews](https://www.wikinews.org/) | `!wn` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") |  | 3.0 | 1 | y |  |  |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[bing news](https://www.bing.com/news) | `!bin` | [`bing_news`](https://docs.searxng.org/dev/engines/online/bing.html#module-searx.engines.bing_news "searx.engines.bing_news") |  | 3.0 | 1 | y | y |  | y  
[brave.news](https://search.brave.com/) | `!brnews` | [`brave`](https://docs.searxng.org/dev/engines/online/brave.html#module-searx.engines.brave "searx.engines.brave") |  | 3.0 | 1 |  | y | y |   
[duckduckgo news](https://duckduckgo.com/) | `!ddn` | [`duckduckgo_extra`](https://docs.searxng.org/dev/engines/online/duckduckgo.html#module-searx.engines.duckduckgo_extra "searx.engines.duckduckgo_extra") |  | 3.0 | 1 | y | y | y |   
[google news](https://news.google.com) | `!gon` | [`google_news`](https://docs.searxng.org/dev/engines/online/google.html#module-searx.engines.google_news "searx.engines.google_news") |  | 3.0 | 1 |  | y | y |   
[qwant news](https://www.qwant.com/) | `!qwn` | [`qwant`](https://docs.searxng.org/dev/engines/online/qwant.html#module-searx.engines.qwant "searx.engines.qwant") |  | 3.0 | 1 | y | y | y |   
[reuters](https://www.reuters.com) | `!reu` | [`reuters`](https://docs.searxng.org/dev/engines/online/reuters.html#module-searx.engines.reuters "searx.engines.reuters") |  | 3.0 | 1 | y |  |  | y  
[yahoo news](https://news.yahoo.com) | `!yhn` | [yahoo_news](https://github.com/searxng/searxng/blob/master/searx/engines/yahoo_news.py) |  | 3.0 | 1 | y |  |  |   
[yep news](https://yep.com/) | `!yepn` | [yep](https://github.com/searxng/searxng/blob/master/searx/engines/yep.py) | y | 3.0 | 1 |  |  | y |   
[tagesschau](https://tagesschau.de) (DE) | `!ts` | [`tagesschau`](https://docs.searxng.org/dev/engines/online/tagesschau.html#module-searx.engines.tagesschau "searx.engines.tagesschau") | y | 3.0 | 1 | y |  |  |   
[ansa](https://www.ansa.it) (IT) | `!ans` | [ansa](https://github.com/searxng/searxng/blob/master/searx/engines/ansa.py) | y | 3.0 | 1 | y |  |  | y  
[il post](https://www.ilpost.it) (IT) | `!pst` | [il_post](https://github.com/searxng/searxng/blob/master/searx/engines/il_post.py) | y | 3.0 | 1 | y |  |  | y  
[naver news](https://search.naver.com) (KO) | `!nvrn` | [naver](https://github.com/searxng/searxng/blob/master/searx/engines/naver.py) | y | 3.0 | 1 | y |  |  | y  
[sogou wechat](https://weixin.sogou.com/) (ZH) | `!sogouw` | [sogou_wechat](https://github.com/searxng/searxng/blob/master/searx/engines/sogou_wechat.py) | y | 3.0 | 1 | y |  |  |   
## tab `!map`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[apple maps](https://www.apple.com/maps/) | `!apm` | [apple_maps](https://github.com/searxng/searxng/blob/master/searx/engines/apple_maps.py) | y | 5.0 | 1 |  |  |  |   
[openstreetmap](https://www.openstreetmap.org/) | `!osm` | [openstreetmap](https://github.com/searxng/searxng/blob/master/searx/engines/openstreetmap.py) |  | 3.0 | 1 |  |  |  |   
[photon](https://photon.komoot.io) | `!ph` | [photon](https://github.com/searxng/searxng/blob/master/searx/engines/photon.py) |  | 3.0 | 1 |  |  |  |   
## tab `!music`
### group `!lyrics`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[genius](https://genius.com/) | `!gen` | [genius](https://github.com/searxng/searxng/blob/master/searx/engines/genius.py) |  | 3.0 | 1 | y |  |  |   
### group `!radio`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[radio browser](https://www.radio-browser.info/) | `!rb` | [`radio_browser`](https://docs.searxng.org/dev/engines/online/radio_browser.html#module-searx.engines.radio_browser "searx.engines.radio_browser") |  | 3.0 | 1 | y | y |  |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[adobe stock audio](https://stock.adobe.com/) | `!asa` | [`adobe_stock`](https://docs.searxng.org/dev/engines/online/adobe_stock.html#module-searx.engines.adobe_stock "searx.engines.adobe_stock") | y | 6 | 1 | y |  |  |   
[bandcamp](https://bandcamp.com/) | `!bc` | [bandcamp](https://github.com/searxng/searxng/blob/master/searx/engines/bandcamp.py) |  | 3.0 | 1 | y |  |  |   
[deezer](https://deezer.com) | `!dz` | [deezer](https://github.com/searxng/searxng/blob/master/searx/engines/deezer.py) | y | 3.0 | 1 | y |  |  |   
[mixcloud](https://www.mixcloud.com/) | `!mc` | [mixcloud](https://github.com/searxng/searxng/blob/master/searx/engines/mixcloud.py) |  | 3.0 | 1 | y |  |  |   
[soundcloud](https://soundcloud.com) | `!sc` | [`soundcloud`](https://docs.searxng.org/dev/engines/online/soundcloud.html#module-searx.engines.soundcloud "searx.engines.soundcloud") |  | 3.0 | 1 | y |  |  |   
[wikicommons.audio](https://commons.wikimedia.org/) | `!wca` | [wikicommons](https://github.com/searxng/searxng/blob/master/searx/engines/wikicommons.py) |  | 3.0 | 1 | y |  |  |   
[yandex music](https://music.yandex.ru) | `!ydm` | [yandex_music](https://github.com/searxng/searxng/blob/master/searx/engines/yandex_music.py) | y | 3.0 | 1 | y |  |  |   
[youtube](https://www.youtube.com/) | `!yt` | [youtube_noapi](https://github.com/searxng/searxng/blob/master/searx/engines/youtube_noapi.py) |  | 3.0 | 1 | y |  |  | y  
## tab `!it`
### group `!packages`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[alpine linux packages](https://www.alpinelinux.org) | `!alp` | [`alpinelinux`](https://docs.searxng.org/dev/engines/online/alpinelinux.html#module-searx.engines.alpinelinux "searx.engines.alpinelinux") | y | 3.0 | 1 | y |  |  |   
[cachy os packages](https://cachyos.org) | `!cos` | [cachy_os](https://github.com/searxng/searxng/blob/master/searx/engines/cachy_os.py) | y | 3.0 | 1 | y |  |  |   
[crates.io](https://crates.io/) | `!crates` | [crates](https://github.com/searxng/searxng/blob/master/searx/engines/crates.py) | y | 6.0 | 1 | y |  |  |   
[docker hub](https://hub.docker.com) | `!dh` | [docker_hub](https://github.com/searxng/searxng/blob/master/searx/engines/docker_hub.py) |  | 3.0 | 1 | y |  |  |   
[hex](https://hex.pm/) | `!hex` | [hex](https://github.com/searxng/searxng/blob/master/searx/engines/hex.py) | y | 3.0 | 1 | y |  |  |   
[hoogle](https://hoogle.haskell.org/) | `!ho` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") |  | 3.0 | 1 |  |  |  |   
[lib.rs](https://lib.rs) | `!lrs` | [lib_rs](https://github.com/searxng/searxng/blob/master/searx/engines/lib_rs.py) | y | 3.0 | 1 |  |  |  |   
[metacpan](https://metacpan.org/) | `!cpan` | [metacpan](https://github.com/searxng/searxng/blob/master/searx/engines/metacpan.py) | y | 3.0 | 1 | y |  |  |   
[npm](https://npms.io/) | `!npm` | [npm](https://github.com/searxng/searxng/blob/master/searx/engines/npm.py) | y | 5.0 | 1 | y |  |  |   
[packagist](https://packagist.org) | `!pack` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") | y | 5.0 | 1 | y |  |  |   
[pkg.go.dev](https://pkg.go.dev/) | `!pgo` | [pkg_go_dev](https://github.com/searxng/searxng/blob/master/searx/engines/pkg_go_dev.py) | y | 3.0 | 1 |  |  |  |   
[pub.dev](https://pub.dev/) | `!pd` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 3.0 | 1 | y |  |  |   
[pypi](https://pypi.org) | `!pypi` | [pypi](https://github.com/searxng/searxng/blob/master/searx/engines/pypi.py) |  | 3.0 | 1 |  |  |  |   
[rubygems](https://rubygems.org/) | `!rbg` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 3.0 | 1 | y |  |  |   
[voidlinux](https://voidlinux.org/packages/) | `!void` | [`voidlinux`](https://docs.searxng.org/dev/engines/online/void.html#module-searx.engines.voidlinux "searx.engines.voidlinux") | y | 3.0 | 1 |  |  |  |   
### group `!q&a`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[askubuntu](https://stackexchange.com) | `!ubuntu` | [stackexchange](https://github.com/searxng/searxng/blob/master/searx/engines/stackexchange.py) |  | 3.0 | 1 | y |  |  |   
[caddy.community](https://discourse.org/) | `!caddy` | [`discourse`](https://docs.searxng.org/dev/engines/online/discourse.html#module-searx.engines.discourse "searx.engines.discourse") | y | 3.0 | 1 | y |  |  | y  
[discuss.python](https://discourse.org/) | `!dpy` | [`discourse`](https://docs.searxng.org/dev/engines/online/discourse.html#module-searx.engines.discourse "searx.engines.discourse") | y | 3.0 | 1 | y |  |  | y  
[pi-hole.community](https://discourse.org/) | `!pi` | [`discourse`](https://docs.searxng.org/dev/engines/online/discourse.html#module-searx.engines.discourse "searx.engines.discourse") | y | 3.0 | 1 | y |  |  | y  
[stackoverflow](https://stackexchange.com) | `!st` | [stackexchange](https://github.com/searxng/searxng/blob/master/searx/engines/stackexchange.py) |  | 3.0 | 1 | y |  |  |   
[superuser](https://stackexchange.com) | `!su` | [stackexchange](https://github.com/searxng/searxng/blob/master/searx/engines/stackexchange.py) |  | 3.0 | 1 | y |  |  |   
### group `!repos`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[bitbucket](https://bitbucket.org/) | `!bb` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 4.0 | 1 | y |  |  |   
[codeberg](https://about.gitea.com) | `!cb` | [`gitea`](https://docs.searxng.org/dev/engines/online/gitea.html#module-searx.engines.gitea "searx.engines.gitea") | y | 3.0 | 1 | y |  |  |   
[gitea.com](https://about.gitea.com) | `!gitea` | [`gitea`](https://docs.searxng.org/dev/engines/online/gitea.html#module-searx.engines.gitea "searx.engines.gitea") | y | 3.0 | 1 | y |  |  |   
[github](https://github.com/) | `!gh` | [github](https://github.com/searxng/searxng/blob/master/searx/engines/github.py) |  | 3.0 | 1 |  |  |  |   
[gitlab](https://gitlab.com/) | `!gl` | [`gitlab`](https://docs.searxng.org/dev/engines/online/gitlab.html#module-searx.engines.gitlab "searx.engines.gitlab") | y | 3.0 | 1 | y |  |  |   
[huggingface](https://huggingface.co/) | `!hf` | [`huggingface`](https://docs.searxng.org/dev/engines/online/huggingface.html#module-searx.engines.huggingface "searx.engines.huggingface") | y | 3.0 | 1 |  |  |  |   
[huggingface datasets](https://huggingface.co/) | `!hfd` | [`huggingface`](https://docs.searxng.org/dev/engines/online/huggingface.html#module-searx.engines.huggingface "searx.engines.huggingface") | y | 3.0 | 1 |  |  |  |   
[huggingface spaces](https://huggingface.co/) | `!hfs` | [`huggingface`](https://docs.searxng.org/dev/engines/online/huggingface.html#module-searx.engines.huggingface "searx.engines.huggingface") | y | 3.0 | 1 |  |  |  |   
[ollama](https://ollama.com) | `!ollama` | [ollama](https://github.com/searxng/searxng/blob/master/searx/engines/ollama.py) | y | 3.0 | 1 |  |  |  |   
[sourcehut](https://sourcehut.org) | `!srht` | [`sourcehut`](https://docs.searxng.org/dev/engines/online/sourcehut.html#module-searx.engines.sourcehut "searx.engines.sourcehut") | y | 3.0 | 1 | y |  |  |   
### group `!software_wikis`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[arch linux wiki](https://wiki.archlinux.org/) | `!al` | [`archlinux`](https://docs.searxng.org/dev/engines/online/archlinux.html#module-searx.engines.archlinux "searx.engines.archlinux") |  | 3.0 | 1 | y | y |  |   
[free software directory](https://directory.fsf.org/) | `!fsd` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 5.0 | 1 | y |  |  |   
[gentoo](https://docs.searxng.org/user/None) | `!ge` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") |  | 10 | 1 | y |  |  |   
[nixos wiki](https://docs.searxng.org/user/None) | `!nixw` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 1 | y |  |  |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[anaconda](https://docs.searxng.org/user/{}) | `!conda` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 6.0 | 1 | y |  |  |   
[habrahabr](https://habr.com/) | `!habr` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 4.0 | 1 | y |  |  |   
[hackernews](https://news.ycombinator.com/) | `!hn` | [hackernews](https://github.com/searxng/searxng/blob/master/searx/engines/hackernews.py) | y | 3.0 | 1 | y |  |  | y  
[lobste.rs](https://lobste.rs/) | `!lo` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 5.0 | 1 |  |  |  |   
[mankier](https://www.mankier.com/) | `!man` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") |  | 3.0 | 1 |  |  |  |   
[mdn](https://developer.mozilla.org) | `!mdn` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") |  | 3.0 | 1 | y |  |  |   
[microsoft learn](https://learn.microsoft.com) | `!msl` | [microsoft_learn](https://github.com/searxng/searxng/blob/master/searx/engines/microsoft_learn.py) | y | 3.0 | 1 | y |  |  |   
[national vulnerability database](https://nvd.nist.gov) | `!nvd` | [nvd](https://github.com/searxng/searxng/blob/master/searx/engines/nvd.py) | y | 3.0 | 1 | y |  |  |   
[baidu kaifa](https://www.baidu.com) (ZH) | `!bdk` | [baidu](https://github.com/searxng/searxng/blob/master/searx/engines/baidu.py) | y | 3.0 | 1 | y |  |  | y  
## tab `!science`
### group `!scientific_publications`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[arxiv](https://arxiv.org) | `!arx` | [`arxiv`](https://docs.searxng.org/dev/engines/online/arxiv.html#module-searx.engines.arxiv "searx.engines.arxiv") |  | 3.0 | 1 | y |  |  |   
[crossref](https://www.crossref.org/) | `!cr` | [`crossref`](https://docs.searxng.org/dev/engines/online/crossref.html#module-searx.engines.crossref "searx.engines.crossref") | y | 30 | 1 | y |  |  |   
[google scholar](https://scholar.google.com) | `!gos` | [`google_scholar`](https://docs.searxng.org/dev/engines/online/google.html#module-searx.engines.google_scholar "searx.engines.google_scholar") |  | 3.0 | 1 | y | y |  | y  
[openalex](https://openalex.org/) | `!oa` | [`openalex`](https://docs.searxng.org/dev/engines/online/openalex.html#module-searx.engines.openalex "searx.engines.openalex") | y | 5.0 | 1 | y |  |  |   
[pubmed](https://www.ncbi.nlm.nih.gov/pubmed/) | `!pub` | [`pubmed`](https://docs.searxng.org/dev/engines/online/pubmed.html#module-searx.engines.pubmed "searx.engines.pubmed") |  | 3.0 | 1 |  |  |  |   
[semantic scholar](https://www.semanticscholar.org/) | `!se` | [`semantic_scholar`](https://docs.searxng.org/dev/engines/online/semantic_scholar.html#module-searx.engines.semantic_scholar "searx.engines.semantic_scholar") |  | 3.0 | 1 | y |  |  |   
### group `!wikimedia`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[wikispecies](https://species.wikimedia.org/) | `!wsp` | [`mediawiki`](https://docs.searxng.org/dev/engines/mediawiki.html#module-searx.engines.mediawiki "searx.engines.mediawiki") | y | 3.0 | 1 | y |  |  |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[openairedatasets](https://www.openaire.eu/) | `!oad` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") |  | 5.0 | 1 | y |  |  |   
[openairepublications](https://www.openaire.eu/) | `!oap` | [`json_engine`](https://docs.searxng.org/dev/engines/json_engine.html#module-searx.engines.json_engine "searx.engines.json_engine") |  | 5.0 | 1 | y |  |  |   
[pdbe](https://www.ebi.ac.uk/pdbe) | `!pdb` | [pdbe](https://github.com/searxng/searxng/blob/master/searx/engines/pdbe.py) |  | 3.0 | 1 |  |  |  |   
## tab `!files`
### group `!apps`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[apk mirror](https://www.apkmirror.com) | `!apkm` | [apkmirror](https://github.com/searxng/searxng/blob/master/searx/engines/apkmirror.py) | y | 4.0 | 1 | y |  |  |   
[apple app store](https://www.apple.com/app-store/) | `!aps` | [apple_app_store](https://github.com/searxng/searxng/blob/master/searx/engines/apple_app_store.py) | y | 3.0 | 1 |  |  | y |   
[fdroid](https://f-droid.org/) | `!fd` | [fdroid](https://github.com/searxng/searxng/blob/master/searx/engines/fdroid.py) | y | 3.0 | 1 | y |  |  |   
[google play apps](https://play.google.com/) | `!gpa` | [google_play](https://github.com/searxng/searxng/blob/master/searx/engines/google_play.py) | y | 3.0 | 1 |  |  |  |   
### group `!books`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[annas archive](https://annas-archive.gl/) | `!aa` | [`annas_archive`](https://docs.searxng.org/dev/engines/online/annas_archive.html#module-searx.engines.annas_archive "searx.engines.annas_archive") | y | 5 | 1 | y | y |  |   
### without further subgrouping
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[1337x](https://1337x.to/) | `!1337x` | [1337x](https://github.com/searxng/searxng/blob/master/searx/engines/1337x.py) | y | 3.0 | 1 | y |  |  |   
[bt4g](https://bt4gprx.com) | `!bt4g` | [`bt4g`](https://docs.searxng.org/dev/engines/online/bt4g.html#module-searx.engines.bt4g "searx.engines.bt4g") |  | 3.0 | 1 | y |  |  | y  
[btdigg](https://btdig.com) | `!bt` | [btdigg](https://github.com/searxng/searxng/blob/master/searx/engines/btdigg.py) | y | 3.0 | 1 | y |  |  |   
[kickass](https://kickasstorrents.to) | `!kc` | [kickass](https://github.com/searxng/searxng/blob/master/searx/engines/kickass.py) |  | 4.0 | 1 | y |  |  |   
[library genesis](https://libgen.fun/) | `!lg` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 7.0 | 1 |  |  |  |   
[nyaa](https://nyaa.si/) | `!nt` | [nyaa](https://github.com/searxng/searxng/blob/master/searx/engines/nyaa.py) | y | 3.0 | 1 | y |  |  |   
[openrepos](https://openrepos.net/) | `!or` | [`xpath`](https://docs.searxng.org/dev/engines/xpath.html#module-searx.engines.xpath "searx.engines.xpath") | y | 4.0 | 1 | y |  |  |   
[piratebay](https://thepiratebay.org) | `!tpb` | [piratebay](https://github.com/searxng/searxng/blob/master/searx/engines/piratebay.py) |  | 3.0 | 1 |  |  |  |   
[solidtorrents](https://www.solidtorrents.to/) | `!solid` | [solidtorrents](https://github.com/searxng/searxng/blob/master/searx/engines/solidtorrents.py) |  | 4.0 | 1 | y |  |  |   
[tokyotoshokan](https://www.tokyotosho.info/) | `!tt` | [tokyotoshokan](https://github.com/searxng/searxng/blob/master/searx/engines/tokyotoshokan.py) | y | 6.0 | 1 | y |  |  |   
[wikicommons.files](https://commons.wikimedia.org/) | `!wcf` | [wikicommons](https://github.com/searxng/searxng/blob/master/searx/engines/wikicommons.py) |  | 3.0 | 1 | y |  |  |   
## tab `!social_media`
Engines configured by default (in [settings.yml](https://docs.searxng.org/dev/engines/engine_overview.html#engine-settings)) |  [Supported features](https://docs.searxng.org/dev/engines/engine_overview.html#engine-file)  
---|---  
Name | !bang | Module | Disabled | Timeout | Weight | Paging | Locale | Safe search | Time range  
[9gag](https://9gag.com/) | `!9g` | [9gag](https://github.com/searxng/searxng/blob/master/searx/engines/9gag.py) | y | 3.0 | 1 | y |  |  |   
[lemmy comments](https://lemmy.ml/) | `!lecom` | [`lemmy`](https://docs.searxng.org/dev/engines/online/lemmy.html#module-searx.engines.lemmy "searx.engines.lemmy") |  | 3.0 | 1 | y |  |  |   
[lemmy communities](https://lemmy.ml/) | `!leco` | [`lemmy`](https://docs.searxng.org/dev/engines/online/lemmy.html#module-searx.engines.lemmy "searx.engines.lemmy") |  | 3.0 | 1 | y |  |  |   
[lemmy posts](https://lemmy.ml/) | `!lepo` | [`lemmy`](https://docs.searxng.org/dev/engines/online/lemmy.html#module-searx.engines.lemmy "searx.engines.lemmy") |  | 3.0 | 1 | y |  |  |   
[lemmy users](https://lemmy.ml/) | `!leus` | [`lemmy`](https://docs.searxng.org/dev/engines/online/lemmy.html#module-searx.engines.lemmy "searx.engines.lemmy") |  | 3.0 | 1 | y |  |  |   
[mastodon hashtags](https://joinmastodon.org/) | `!mah` | [`mastodon`](https://docs.searxng.org/dev/engines/online/mastodon.html#module-searx.engines.mastodon "searx.engines.mastodon") |  | 3.0 | 1 |  |  |  |   
[mastodon users](https://joinmastodon.org/) | `!mau` | [`mastodon`](https://docs.searxng.org/dev/engines/online/mastodon.html#module-searx.engines.mastodon "searx.engines.mastodon") |  | 3.0 | 1 |  |  |  |   
[reddit](https://www.reddit.com/) | `!re` | [reddit](https://github.com/searxng/searxng/blob/master/searx/engines/reddit.py) | y | 3.0 | 1 |  |  |  |   
[tootfinder](https://www.tootfinder.ch) | `!toot` | [tootfinder](https://github.com/searxng/searxng/blob/master/searx/engines/tootfinder.py) |  | 3.0 | 1 |  |  |  |   
