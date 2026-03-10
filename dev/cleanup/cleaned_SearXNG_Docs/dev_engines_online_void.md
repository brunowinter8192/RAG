<!-- source: https://docs.searxng.org/dev/engines/online/void.html -->

# Void Linux binary packages
SearXNG engine for [Void Linux binary packages](https://voidlinux.org/packages/). Void is a general purpose operating system, based on the monolithic Linux kernel. Its package system allows you to quickly install, update and remove software; software is provided in binary packages or can be built directly from sources with the help of the XBPS source packages collection. 

**engines.voidlinux.void_arch** = `'x86_64'`
Default architecture to search for. For valid values see [`ARCH_RE`](https://docs.searxng.org/dev/engines/online/void.html#searx.engines.voidlinux.ARCH_RE "searx.engines.voidlinux.ARCH_RE") 

**engines.voidlinux.ARCH_RE** = `re.compile('aarch64-musl|armv6l-musl|armv7l-musl|x86_64-musl|aarch64|armv6l|armv7l|i686|x86_64')`
Regular expression that match a architecture in the query string. 

**engines.voidlinux.response(_resp_)**
At Void Linux, several packages sometimes share the same source code (template) and therefore also have the same URL. Results with identical URLs are merged as one result for SearXNG.
