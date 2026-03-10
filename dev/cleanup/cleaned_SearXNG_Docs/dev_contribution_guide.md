<!-- source: https://docs.searxng.org/dev/contribution_guide.html -->

# How to contribute
## Prime directives: Privacy, Hackability
SearXNG has two prime directives, **privacy-by-design and hackability** . The hackability comes in three levels:
  * support of search engines
  * plugins to alter search behaviour
  * hacking SearXNG itself

Note the lack of “world domination” among the directives. SearXNG has no intention of wide mass-adoption, rounded corners, etc. The prime directive “privacy” deserves a separate chapter, as it’s quite uncommon unfortunately.
### Privacy-by-design
SearXNG was born out of the need for a **privacy-respecting** search tool which can be extended easily to maximize both its search and its privacy protecting capabilities.
Some widely used search engine features may work differently, may be turned off by default, or may not be implemented at all in SearXNG **as a consequence of a privacy-by-design approach**.
Following this approach, features reducing the privacy preserving aspects of SearXNG should be switched off by default or should not be implemented at all. There are plenty of search engines already providing such features. If a feature reduces SearXNG’s efficacy in protecting a user’s privacy, the user must be informed about the effect of choosing to enable it. Features that protect privacy but differ from the expectations of the user should also be carefully explained to them.
Also, if you think that something works weird with SearXNG, it might be because the tool you are using is designed in a way that interferes with SearXNG’s privacy aspects. Submitting a bug report to the vendor of the tool that misbehaves might be a good feedback for them to reconsider the disrespect to their customers (e.g., `GET` vs `POST` requests in various browsers).
Remember the other prime directive of SearXNG is to be hackable, so if the above privacy concerns do not fancy you, simply fork it.
> _Happy hacking._
## Code
Create good commits!
  * [Git Commits & Change Management](https://docs.searxng.org/dev/commits.html#create-commit)

In order to submit a patch, please follow the steps below:
  * Follow coding conventions.
    * [PEP8](https://www.python.org/dev/peps/pep-0008/) standards apply, except the convention of line length
    * Maximum line length is 120 characters
  * The cardinal rule for creating good commits is to ensure there is only one _logical change_ per commit / read [Structural split of changes](https://wiki.openstack.org/wiki/GitCommitMessages#Structural_split_of_changes)
  * Check if your code breaks existing tests. If so, update the tests or fix your code.
  * If your code can be unit-tested, add unit tests.
  * Add yourself to the [git://AUTHORS.rst](https://github.com/searxng/searxng/blob/master/AUTHORS.rst) file.
  * Choose meaningful commit messages, see [Git Commits & Change Management](https://docs.searxng.org/dev/commits.html#create-commit)
  * Create a pull request.

For more help on getting started with SearXNG development, see [Development Quickstart](https://docs.searxng.org/dev/quickstart.html#devquickstart).
## Translation
Translation currently takes place on [weblate](https://docs.searxng.org/dev/translation.html#translation).
## Documentation
The reST sources
has been moved from `gh-branch` into `master` ([git://docs](https://github.com/searxng/searxng/blob/master/docs)).
The documentation is built using [Sphinx](https://www.sphinx-doc.org). So in order to be able to generate the required files, you have to install it on your system. Much easier, use our [Makefile & ./manage](https://docs.searxng.org/dev/makefile.html#makefile).
Here is an example which makes a complete rebuild:
```
$ make docs.clean docs.html
...
The HTML pages are in dist/docs.

```

### Live build
docs.clean
It is recommended to assert a complete rebuild before deploying (use `docs.clean`).
Live build is like WYSIWYG. It’s the recommended way to go if you want to edit the documentation. The Makefile target `docs.live` builds the docs, opens URL in your favorite browser and rebuilds every time a reST file has been changed ([make docs.clean docs.live](https://docs.searxng.org/dev/makefile.html#make-docs-clean)).
```
$ make docs.live
...
The HTML pages are in dist/docs.
... Serving on http://0.0.0.0:8000
... Start watching changes

```

Live builds are implemented by [sphinx-autobuild](https://github.com/executablebooks/sphinx-autobuild/blob/master/README.md). Use environment `$(SPHINXOPTS)` to pass arguments to the [sphinx-autobuild](https://github.com/executablebooks/sphinx-autobuild/blob/master/README.md) command. You can pass any argument except for the `--host` option (which is always set to `0.0.0.0`). E.g., to find and use a free port, use:
```
$ SPHINXOPTS="--port 0" make docs.live
...
... Serving on http://0.0.0.0:50593
...

```

### deploy on github.io
To deploy documentation at [github.io](https://docs.searxng.org//.) use Makefile target [make docs.gh-pages](https://docs.searxng.org/dev/makefile.html#make-docs-gh-pages), which builds the documentation and runs all the needed git add, commit and push:
```
$ make docs.clean docs.gh-pages

```

Attention
If you are working in your own brand, don’t forget to adjust your [brand:](https://docs.searxng.org/admin/settings/settings_brand.html#settings-brand).
