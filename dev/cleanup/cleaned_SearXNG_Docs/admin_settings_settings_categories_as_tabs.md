<!-- source: https://docs.searxng.org/admin/settings/settings_categories_as_tabs.html -->

#  `categories_as_tabs:`
A list of the categories that are displayed as tabs in the user interface. Categories not listed here can still be searched with the [Search syntax](https://docs.searxng.org/user/search-syntax.html#search-syntax).
```
categories_as_tabs:
  general:
  images:
  videos:
  news:
  map:
  music:
  it:
  science:
  files:
  social media:

```

Engines are added to `categories:` (compare [categories](https://docs.searxng.org/admin/settings/settings_engines.html#engine-categories)), the categories listed in `categories_as_tabs` are shown as tabs in the UI. If there are no active engines in a category, the tab is not displayed (e.g. if a user disables all engines in a category).
On the preferences page (`/preferences`) – under _engines_ – there is an additional tab, called _other_. In this tab are all engines listed that are not in one of the UI tabs (not included in `categories_as_tabs`).
