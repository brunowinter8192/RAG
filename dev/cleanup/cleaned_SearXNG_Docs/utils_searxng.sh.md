<!-- source: https://docs.searxng.org/utils/searxng.sh.html -->

#  `utils/searxng.sh`
To simplify the installation and maintenance of a SearXNG instance you can use the script [git://utils/searxng.sh](https://github.com/searxng/searxng/blob/master/utils/searxng.sh).
further reading
## Install
In most cases you will install SearXNG simply by running the command:
```
sudo -H ./utils/searxng.sh install all

```

The installation is described in chapter [Step by step installation](https://docs.searxng.org/admin/installation-searxng.html#installation-basic).
## Command Help
The `--help` output of the script is largely self-explanatory:
```
usage:
  searxng.sh install    [all|user|pyenv|settings|uwsgi|valkey|nginx|apache|searxng-src|packages|buildhost]
  searxng.sh remove     [all|user|pyenv|settings|uwsgi|valkey|nginx|apache]
  searxng.sh instance   [cmd|update|check|localtest|inspect]
install|remove:
  all           : complete (de-) installation of the SearXNG service
  user          : service user 'searxng' (/usr/local/searxng)
  pyenv         : virtualenv (python) in /usr/local/searxng/searx-pyenv
  settings      : settings from /etc/searxng/settings.yml
  uwsgi         : SearXNG's uWSGI app searxng.ini
  nginx         : HTTP site /searxng.conf
  apache        : HTTP site /searxng.conf
install:
  valkey        : install a local valkey server
remove:
  redis         : remove a local redis server /run/redis.sock
install:
  searxng-src   : clone https://github.com/searxng/searxng into /usr/local/searxng/searxng-src
  packages      : installs packages from OS package manager required by SearXNG
  buildhost     : installs packages from OS package manager required by a SearXNG buildhost
instance:
  update        : update SearXNG instance (git fetch + reset & update settings.yml)
  check         : run checks from utils/searxng_check.py in the active installation
  inspect       : run some small tests and inspect SearXNG's server status and log
  get_setting   : get settings value from running SearXNG instance
  cmd           : run command in SearXNG instance's environment (e.g. bash)
uWSGI:
  SEARXNG_UWSGI_SOCKET : /usr/local/searxng/run/socket
environment:
  GIT_URL              : https://github.com/searxng/searxng
  GIT_BRANCH           : master
  SEARXNG_URL          : http://runnervm95407/searxng
  SEARXNG_PORT         : 8888
  SEARXNG_BIND_ADDRESS : 127.0.0.1

```
