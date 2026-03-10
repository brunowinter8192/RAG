<!-- source: https://docs.searxng.org/dev/translation.html -->

# Translation
[![translated](https://translate.codeberg.org/widgets/searxng/-/searxng/svg-badge.svg)](https://translate.codeberg.org/projects/searxng/)
  * [Custom message extractor (i18n)](https://docs.searxng.org/src/searx.babel_extract.html#searx-babel-extract)
  * [Weblate](https://docs.weblate.org)
  * SearXNG [translations branch](https://github.com/searxng/searxng/tree/translations)
  * SearXNG [Weblate repository](https://translate.codeberg.org/projects/searxng/searxng/#repository)
  * Weblate Client: [wlc](https://docs.weblate.org/en/latest/wlc.html)
  * Babel Command-Line: [pybabel](http://babel.pocoo.org/en/latest/cmdline.html)
  * [weblate workflow](https://docs.weblate.org/en/latest/workflows.html)

Translation takes place on [translate.codeberg.org](https://translate.codeberg.org/projects/searxng/).
Translations which has been added by translators on the [translate.codeberg.org](https://translate.codeberg.org/projects/searxng/) UI are committed to Weblate’s counterpart of the SearXNG _origin_ repository which is located at `https://translate.codeberg.org/git/searxng/searxng`.
There is no need to clone this repository, [SearXNG’s PR workflow to be in sync with Weblate](https://docs.searxng.org/dev/translation.html#searxng-weblate-workflow) take care of the synchronization with the _origin_. To avoid merging commits from the counterpart directly on the `master` branch of _SearXNG origin_ , a _pull request_ (PR) is created by this workflow.
Weblate monitors the [translations branch](https://github.com/searxng/searxng/tree/translations), not the `master` branch. This branch is an [orphan branch](https://git-scm.com/docs/git-checkout#Documentation/git-checkout.txt---orphanltnewbranchgt), decoupled from the master branch (we already know orphan branches from the `gh-pages`). The [translations branch](https://github.com/searxng/searxng/tree/translations) contains only the
  * `translation/messages.pot` and the
  * `translation/*/messages.po` files, nothing else.

![../_images/translation.svg](https://docs.searxng.org/_images/translation.svg)
Fig. 3 SearXNG’s PR workflow to be in sync with Weblate 

Sync from _origin_ to _weblate_ : using `make weblate.push.translations` 
    
For each commit on the `master` branch of SearXNG _origin_ the GitHub job [babel / Update translations branch](https://github.com/searxng/searxng/blob/master/.github/workflows/integration.yml) checks for updated translations. 

Sync from _weblate_ to _origin_ : using `make weblate.translations.commit` 
    
Every Friday, the GitHub workflow [babel / create PR for additions from weblate](https://github.com/searxng/searxng/blob/master/.github/workflows/translations-update.yml) creates a PR with the updated translation files:
  * `translation/messages.pot`,
  * `translation/*/messages.po` and
  * `translation/*/messages.mo`

## wlc
All weblate integration is done by GitHub workflows, but if you want to use [wlc](https://docs.weblate.org/en/latest/wlc.html), copy this content into [wlc configuration](https://docs.weblate.org/en/latest/wlc.html#wlc-config) in your HOME `~/.config/weblate`
```
[keys]
https://translate.codeberg.org/api/ = APIKEY

```

Replace `APIKEY` by your [API key](https://translate.codeberg.org/accounts/profile/#api).
