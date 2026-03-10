<!-- source: https://docs.searxng.org/dev/engines/online/adobe_stock.html -->

# Adobe Stock
Contents
[Adobe Stock](https://docs.searxng.org/dev/engines/online/adobe_stock.html#adobe-stock) is a service that gives access to millions of royalty-free assets. Assets types include photos, vectors, illustrations, templates, 3D assets, videos, motion graphics templates and audio tracks.
## Configuration
The engine has the following mandatory setting:
  * SearXNG’s [categories](https://docs.searxng.org/admin/settings/settings_engines.html#engine-categories)
  * Adobe-Stock’s [`adobe_order`](https://docs.searxng.org/dev/engines/online/adobe_stock.html#searx.engines.adobe_stock.adobe_order "searx.engines.adobe_stock.adobe_order")
  * Adobe-Stock’s [`adobe_content_types`](https://docs.searxng.org/dev/engines/online/adobe_stock.html#searx.engines.adobe_stock.adobe_content_types "searx.engines.adobe_stock.adobe_content_types")

```
- name: adobe stock
  engine: adobe_stock
  shortcut: asi
  categories: [images]
  adobe_order: relevance
  adobe_content_types: ["photo", "illustration", "zip_vector", "template", "3d", "image"]

- name: adobe stock video
  engine: adobe_stock
  network: adobe stock
  shortcut: asi
  categories: [videos]
  adobe_order: relevance
  adobe_content_types: ["video"]

```

## Implementation
**engines.adobe_stock.adobe_order** = `''`
Sort order, can be one of:
  * `relevance` or
  * `featured` or
  * `creation` (most recent) or
  * `nb_downloads` (number of downloads)

**engines.adobe_stock.adobe_content_types** = `[]`
A list of of content types. The following content types are offered:
  * Images: `image`
  * Videos: `video`
  * Templates: `template`
  * 3D: `3d`
  * Audio `audio`

Additional subcategories:
  * Photos: `photo`
  * Illustrations: `illustration`
  * Vectors: `zip_vector` (Vectors),
