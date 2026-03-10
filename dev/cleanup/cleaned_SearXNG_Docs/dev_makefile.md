<!-- source: https://docs.searxng.org/dev/makefile.html -->

# Makefile & `./manage`
All relevant build and development tasks are implemented in the [./manage](https://github.com/searxng/searxng/blob/master/manage) script and for CI or IDE integration a small [git://Makefile](https://github.com/searxng/searxng/blob/master/Makefile) wrapper is available. If you are not familiar with Makefiles, we recommend to read [gnu-make](https://www.gnu.org/software/make/manual/make.html#Introduction) introduction.
build environment
Before looking deeper at the targets, first read about [Python environment (make install)](https://docs.searxng.org/dev/makefile.html#make-install).
To install developer requirements follow [Buildhosts](https://docs.searxng.org/admin/buildhosts.html#buildhosts).
The usage is simple, just type `make {target-name}` to _build_ a target. Calling the `help` target gives a first overview (`make help`):
`make``./manage`
```
INFO:  sourced NVM environment from /home/runner/.nvm
nvm.: use nvm (without dot) to execute nvm commands directly
  install   : install NVM locally at /home/runner/work/searxng/searxng/.nvm
  clean     : remove NVM installation
  status    : prompt some status information about nvm & node
  nodejs    : install latest Node.js
  cmd ...   : run command ... in NVM environment
  bash      : start bash interpreter with NVM environment sourced
webapp.:
  run       : run developer instance
docs.:
  html      : build HTML documentation
  live      : autobuild HTML documentation while editing
  gh-pages  : deploy on gh-pages branch
  prebuild  : build reST include files (./build/docs/includes)
  clean     : clean documentation build
gecko.driver:
  download & install geckodriver if not already installed (required for
  robot_tests)
valkey:
  install   : create user () and install systemd service ()
py.:
  build     : Build python packages at ./dist
  clean     : delete virtualenv and intermediate py files
pyenv.:
  install   : developer install of SearXNG into virtualenv
  uninstall : uninstall developer installation
  cmd ...   : run command ... in virtualenv
  OK        : test if virtualenv is OK
format.:
  python    : format Python code source using black
  shell     : format Shell scripts using shfmt
go:           GOROOT=/home/runner/work/searxng/searxng/.govm/go1.24.5
  install   : compiles and installs packages
node.:
  env       : download & install SearXNG's npm dependencies locally
  env.dev   : download & install developer and CI tools
  clean     : drop locally npm installations
weblate.:
  push.translations: push translation changes from SearXNG to Weblate's counterpart
  to.translations: Update 'translations' branch with last additions from Weblate.
container.:
  build     : build container image
data.:
  all           : update searx/sxng_locales.py and searx/data/*
  traits        : update searx/data/engine_traits.json & searx/sxng_locales.py
  useragents    : update searx/data/useragents.json with the most recent versions of Firefox
  gsa_useragents: update searx/data/gsa_useragents.txt with compatible useragents
  locales       : update searx/data/locales.json from babel
  currencies    : update searx/data/currencies.json from wikidata
test.:
  yamllint  : lint YAML files (YAMLLINT_FILES)
  pylint    : lint ./searx, ./searxng_extra and ./tests
  pyright   : check Python types
  black     : check Python code format
  shfmt     : check Shell script code format
  unit      : run unit tests
  coverage  : run unit tests with coverage
  robot     : run robot test
  rst       : test .rst files incl. README.rst
  clean     : clean intermediate test stuff
themes.:
  all       : test & build all themes
  simple    : test & build simple theme
  lint      : lint JS & CSS (LESS) files
  fix       : fix JS & CSS (LESS) files
  test      : test all themes
static.build.:  [build] /static
  commit    : build & commit /static folder
  drop      : drop last commit if it was previously done by static.build.commit
  restore   : git restore of the /static folder (after themes.all)
vite.:  .. to be done ..
  simple.:
    build: build static files of the simple theme
    fix:   run prettiers on simple theme
    lint:  run linters on simple theme
    dev:   start development server
dev.:
  env: enter developer environment (or exec a command in)
environment ...
  SEARXNG_VALKEY_URL : 
----
run            - run developer instance
install        - developer install of SearxNG into virtualenv
uninstall      - uninstall developer installation
clean          - clean up working tree
test           - run shell & CI tests
test.shell     - test shell scripts
ci.test        - run CI tests

```

The Makefile targets are implemented for comfort, if you can do without tab-completion and need to have a more granular control, use [git://manage](https://github.com/searxng/searxng/blob/master/manage) without the Makefile wrappers.
```
$ ./manage help

```

## Python environment (`make install`)
activate environment
`source ./local/py3/bin/activate`
We do no longer need to build up the virtualenv manually. Jump into your git working tree and release a `make install` to get a virtualenv with a _developer install_ of SearXNG ([git://setup.py](https://github.com/searxng/searxng/blob/master/setup.py)).
```
$ cd ~/searxng-clone
$ make install
PYENV     [virtualenv] installing ./requirements*.txt into local/py3
...
PYENV     [install] pip install --use-pep517 --no-build-isolation -e 'searx[test]'
...
Successfully installed searxng-2023.7.19+a446dea1b

```

If you release `make install` multiple times the installation will only rebuild if the sha256 sum of the _requirement files_ fails. With other words: the check fails if you edit the requirements listed in [git://requirements-dev.txt](https://github.com/searxng/searxng/blob/master/requirements-dev.txt) and [git://requirements.txt](https://github.com/searxng/searxng/blob/master/requirements.txt)).
```
$ make install
PYENV     OK
PYENV     [virtualenv] requirements.sha256 failed
          [virtualenv] - 6cea6eb6def9e14a18bf32f8a3e...  ./requirements-dev.txt
          [virtualenv] - 471efef6c73558e391c3adb35f4...  ./requirements.txt
...
PYENV     [virtualenv] installing ./requirements*.txt into local/py3
...
PYENV     [install] pip install --use-pep517 --no-build-isolation -e 'searx[test]'
...
Successfully installed searxng-2023.7.19+a446dea1b

```

drop environment
To get rid of the existing environment before re-build use [clean target](https://docs.searxng.org/dev/makefile.html#make-clean) first.
If you think, something goes wrong with your ./local environment or you change the [git://setup.py](https://github.com/searxng/searxng/blob/master/setup.py) file, you have to call [make clean](https://docs.searxng.org/dev/makefile.html#make-clean).
## Node.js environment (`make node.env`)
[Node.js](https://nodejs.org/) version 24.3.0 or higher is required to build the themes. If the requirement is not met, the build chain uses [nvm](https://github.com/nvm-sh) (Node Version Manager) to install [Node.js](https://nodejs.org/) locally: there is no need to install [nvm](https://github.com/nvm-sh) or [npm](https://www.npmjs.com/) on your system.
To install [NVM](https://github.com/nvm-sh) and [Node.js](https://nodejs.org/) in once you can use [make nvm.nodejs](https://docs.searxng.org/dev/makefile.html#make-nvm-nodejs).
### NVM `make nvm.install nvm.status`
Use `make nvm.status` to get the current status of your [Node.js](https://nodejs.org/) and [nvm](https://github.com/nvm-sh) setup.
nvm.installnvm.status (ubu2004)
```
$ LANG=C make nvm.install
INFO:  install (update) NVM at ./searxng/.nvm
INFO:  clone: https://github.com/nvm-sh/nvm.git
  || Cloning into './searxng/.nvm'...
INFO:  checkout v0.39.4
  || HEAD is now at 8fbf8ab v0.39.4

```

Here is the output you will typically get on a Ubuntu 20.04 system which serves only a [no longer active](https://nodejs.org/en/about/releases/) Release [Node.js v10.19.0](https://packages.ubuntu.com/focal/nodejs).
```
$ make nvm.status
INFO:  Node.js is installed at /usr/bin/node
INFO:  Node.js is version v10.19.0
WARN:  minimal Node.js version is 16.13.0
INFO:  npm is installed at /usr/bin/npm
INFO:  npm is version 6.14.4
WARN:  NVM is not installed

```

### `make nvm.nodejs`
Install latest [Node.js](https://nodejs.org/) locally (uses [nvm](https://github.com/nvm-sh)):
```
$ make nvm.nodejs
INFO:  install (update) NVM at /share/searxng/.nvm
INFO:  clone: https://github.com/nvm-sh/nvm.git
...
Downloading and installing node v16.13.0...
...
INFO:  Node.js is installed at searxng/.nvm/versions/node/v16.13.0/bin/node
INFO:  Node.js is version v16.13.0
INFO:  npm is installed at searxng/.nvm/versions/node/v16.13.0/bin/npm
INFO:  npm is version 8.1.0
INFO:  NVM is installed at searxng/.nvm

```

## `make run`
To get up a running a developer instance simply call `make run`. This enables _debug_ option in [git://searx/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml), starts a `./searx/webapp.py` instance and opens the URL in your favorite WEB browser ([xdg-open](https://manpages.debian.org/jump?q=xdg-open)):
```
$ make run

```

Changes to theme’s HTML templates (jinja2) are instant. Changes to the CSS & JS sources of the theme need to be rebuild. You can do that by running:
```
$ make themes.all

```

## `make format`
  * Format Python source code using [Black code style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html). See `$BLACK_OPTIONS` and `$BLACK_TARGETS` in [git://Makefile](https://github.com/searxng/searxng/blob/master/Makefile).
  * Format Shell scripts using [shfmt](https://github.com/mvdan/sh?tab=readme-ov-file#shfmt). The formatter `shfmt` reads the rules from the [EditorConfig](https://github.com/patrickvane/shfmt?tab=readme-ov-file#description) files.

## `make clean`
Drops all intermediate files, all builds, but keep sources untouched. Before calling `make clean` stop all processes using the [Python environment (make install)](https://docs.searxng.org/dev/makefile.html#make-install) or [Node.js environment (make node.env)](https://docs.searxng.org/dev/makefile.html#make-node-env).
```
$ make clean
CLEAN     pyenv
PYENV     [virtualenv] drop local/py3
CLEAN     docs -- build/docs dist/docs
CLEAN     themes -- locally installed npm dependencies
...
CLEAN     test stuff
CLEAN     common files

```

## `make docs`
Target `docs` builds the documentation:
```
$ make docs
HTML ./docs --> file://
DOCS      build build/docs/includes
...
The HTML pages are in dist/docs.

```

### `make docs.clean docs.live`
We describe the usage of the `doc.*` targets in the [How to contribute / Documentation](https://docs.searxng.org/dev/contribution_guide.html#contrib-docs) section. If you want to edit the documentation read our [Live build](https://docs.searxng.org/dev/contribution_guide.html#make-docs-live) section. If you are working in your own brand, adjust your [brand:](https://docs.searxng.org/admin/settings/settings_brand.html#settings-brand).
### `make docs.gh-pages`
To deploy on github.io first adjust your [brand:](https://docs.searxng.org/admin/settings/settings_brand.html#settings-brand). For any further read [deploy on github.io](https://docs.searxng.org/dev/contribution_guide.html#deploy-on-github-io).
## `make test`
Runs a series of tests: [make test.pylint](https://docs.searxng.org/dev/makefile.html#make-test-pylint), `test.pep8`, `test.unit` and `test.robot`. You can run tests selective, e.g.:
```
$ make test.pep8 test.unit test.shell
TEST      test.pep8 OK
...
TEST      test.unit OK
...
TEST      test.shell OK

```

### `make test.shell`
[Lint shell scripts](https://docs.searxng.org/admin/buildhosts.html#sh-lint) / if you have changed some bash scripting run this test before commit.
### `make test.pylint`
[Pylint](https://www.pylint.org/) is known as one of the best source-code, bug and quality checker for the Python programming language. The pylint profile used in the SearXNG project is found in project’s root folder [git://.pylintrc](https://github.com/searxng/searxng/blob/master/.pylintrc).
## `make themes.*`
**Further reading:**
  * [Development Quickstart](https://docs.searxng.org/dev/quickstart.html#devquickstart)

The [git://Makefile](https://github.com/searxng/searxng/blob/master/Makefile) targets `make theme.*` cover common tasks to build the theme(s). The `./manage themes.*` command line can be used to convenient run common theme build tasks.
```
INFO:  sourced NVM environment from /home/runner/.nvm
themes.:
  all       : test & build all themes
  simple    : test & build simple theme
  lint      : lint JS & CSS (LESS) files
  fix       : fix JS & CSS (LESS) files
  test      : test all themes

```

To get live builds while modifying CSS & JS use ([make run](https://docs.searxng.org/dev/makefile.html#make-run)):
```
$ LIVE_THEME=simple make run

```

## `make static.build.*`
**Further reading:**
  * [Development Quickstart](https://docs.searxng.org/dev/quickstart.html#devquickstart)

The [git://Makefile](https://github.com/searxng/searxng/blob/master/Makefile) targets `static.build.*` cover common tasks to build (a commit of) the static files. The `./manage static.build..*` command line can be used to convenient run common build tasks of the static files.
```
INFO:  sourced NVM environment from /home/runner/.nvm
static.build.:  [build] /static
  commit    : build & commit /static folder
  drop      : drop last commit if it was previously done by static.build.commit
  restore   : git restore of the /static folder (after themes.all)

```

## `./manage go.help`
The `./manage go.*` command line can be used to convenient run common [go (wiki)](https://en.wikipedia.org/wiki/Go_\(programming_language\)) tasks.
```
INFO:  sourced NVM environment from /home/runner/.nvm
go:           GOROOT=/home/runner/work/searxng/searxng/.govm/go1.24.5
  install   : compiles and installs packages

```
