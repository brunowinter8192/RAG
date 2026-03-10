<!-- source: https://docs.searxng.org/admin/installation-uwsgi.html -->

# uWSGI
further reading
  * [systemd.unit](https://www.freedesktop.org/software/systemd/man/systemd.unit.html)
  * [uWSGI Emperor](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html)

## Origin uWSGI
How uWSGI is implemented by distributors varies. The uWSGI project itself recommends two methods:
  1. [systemd.unit](https://www.freedesktop.org/software/systemd/man/systemd.unit.html) template file as described here [One service per app in systemd](https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html#one-service-per-app-in-systemd):

> There is one [systemd unit template](http://0pointer.de/blog/projects/instances.html) on the system installed and one [uwsgi ini file](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#ini-files) per uWSGI-app placed at dedicated locations. Take archlinux and a `searxng.ini` as example:
> ```
systemd template unit: /usr/lib/systemd/system/uwsgi@.service
        contains: [Service]
                  ExecStart=/usr/bin/uwsgi --ini /etc/uwsgi/%I.ini

SearXNG application:   /etc/uwsgi/searxng.ini
        links to: /etc/uwsgi/apps-available/searxng.ini

```

> The SearXNG app (template `/etc/uwsgi/%I.ini`) can be maintained as known from common systemd units:
> ```
$ systemctl enable  uwsgi@searxng
$ systemctl start   uwsgi@searxng
$ systemctl restart uwsgi@searxng
$ systemctl stop    uwsgi@searxng

```

  1. The [uWSGI Emperor](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html) which fits for maintaining a large range of uwsgi apps and there is a [Tyrant mode](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting) to secure multi-user hosting.

> The Emperor mode is a special uWSGI instance that will monitor specific events. The Emperor mode (the service) is started by a (common, not template) systemd unit.
> The Emperor service will scan specific directories for [uwsgi ini file](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#ini-files)s (also know as _vassals_). If a _vassal_ is added, removed or the timestamp is modified, a corresponding action takes place: a new uWSGI instance is started, reload or stopped. Take Fedora and a `searxng.ini` as example:
> ```
to install & start SearXNG instance create --> /etc/uwsgi.d/searxng.ini
to reload the instance edit timestamp      --> touch /etc/uwsgi.d/searxng.ini
to stop instance remove ini                --> rm /etc/uwsgi.d/searxng.ini

```

## Distributors
The [uWSGI Emperor](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html) mode and [systemd unit template](http://0pointer.de/blog/projects/instances.html) is what the distributors mostly offer their users, even if they differ in the way they implement both modes and their defaults. Another point they might differ in is the packaging of plugins (if so, compare [Install packages](https://docs.searxng.org/admin/installation-searxng.html#install-packages)) and what the default python interpreter is (python2 vs. python3).
While archlinux does not start a uWSGI service by default, Fedora (RHEL) starts a Emperor in [Tyrant mode](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting) by default (you should have read [Pitfalls of the Tyrant mode](https://docs.searxng.org/admin/installation-uwsgi.html#uwsgi-tyrant-mode-pitfalls)). Worth to know; debian (ubuntu) follow a complete different approach, read see [Debian’s uWSGI layout](https://docs.searxng.org/admin/installation-uwsgi.html#debian-s-uwsgi-layout).
### Debian’s uWSGI layout
Be aware, Debian’s uWSGI layout is quite different from the standard uWSGI configuration. Your are familiar with [Debian’s Apache layout](https://docs.searxng.org/admin/installation-apache.html#debian-s-apache-layout)? .. they do a similar thing for the uWSGI infrastructure. The folders are:
```
/etc/uwsgi/apps-available/
/etc/uwsgi/apps-enabled/

```

The [uwsgi ini file](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#ini-files) is enabled by a symbolic link:
```
ln -s /etc/uwsgi/apps-available/searxng.ini /etc/uwsgi/apps-enabled/

```

More details can be found in the [uwsgi.README.Debian](https://salsa.debian.org/uwsgi-team/uwsgi/-/raw/debian/latest/debian/uwsgi.README.Debian) (`/usr/share/doc/uwsgi/README.Debian.gz`). Some commands you should know on Debian:
```
Commands recognized by init.d script
====================================

You can issue to init.d script following commands:
  * start        | starts daemon
  * stop         | stops daemon
  * reload       | sends to daemon SIGHUP signal
  * force-reload | sends to daemon SIGTERM signal
  * restart      | issues 'stop', then 'start' commands
  * status       | shows status of daemon instance (running/not running)

'status' command must be issued with exactly one argument: '<confname>'.

Controlling specific instances of uWSGI
=======================================

You could control specific instance(s) by issuing:

    SYSTEMCTL_SKIP_REDIRECT=1 service uwsgi <command> <confname> <confname>...

where:
  * <command> is one of 'start', 'stop' etc.
  * <confname> is the name of configuration file (without extension)

For example, this is how instance for /etc/uwsgi/apps-enabled/hello.xml is
started:

    SYSTEMCTL_SKIP_REDIRECT=1 service uwsgi start hello

```

## uWSGI maintenance
Ubuntu / debianArch LinuxFedora / RHEL
```
# init.d --> /usr/share/doc/uwsgi/README.Debian.gz
# For uWSGI debian uses the LSB init process, this might be changed
# one day, see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=833067

create     /etc/uwsgi/apps-available/searxng.ini
enable:    sudo -H ln -s /etc/uwsgi/apps-available/searxng.ini /etc/uwsgi/apps-enabled/
start:     sudo -H service uwsgi start   searxng
restart:   sudo -H service uwsgi restart searxng
stop:      sudo -H service uwsgi stop    searxng
disable:   sudo -H rm /etc/uwsgi/apps-enabled/searxng.ini

```

```
# systemd --> /usr/lib/systemd/system/uwsgi@.service
# For uWSGI archlinux uses systemd template units, see
# - http://0pointer.de/blog/projects/instances.html
# - https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html#one-service-per-app-in-systemd

create:    /etc/uwsgi/searxng.ini
enable:    sudo -H systemctl enable   uwsgi@searxng
start:     sudo -H systemctl start    uwsgi@searxng
restart:   sudo -H systemctl restart  uwsgi@searxng
stop:      sudo -H systemctl stop     uwsgi@searxng
disable:   sudo -H systemctl disable  uwsgi@searxng

```

```
# systemd --> /usr/lib/systemd/system/uwsgi.service
# The unit file starts uWSGI in emperor mode (/etc/uwsgi.ini), see
# - https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html

create:    /etc/uwsgi.d/searxng.ini
restart:   sudo -H touch /etc/uwsgi.d/searxng.ini
disable:   sudo -H rm /etc/uwsgi.d/searxng.ini

```

## uWSGI setup
Create the configuration ini-file according to your distribution and restart the uwsgi application. As shown below, the [Installation Script](https://docs.searxng.org/admin/installation-scripts.html#installation-scripts) installs by default a uWSGI setup that listens on a socket.
Ubuntu / debianArch LinuxFedora / RHEL
```
# -*- mode: conf; coding: utf-8  -*-
[uwsgi]

# uWSGI core
# ----------
#
# https://uwsgi-docs.readthedocs.io/en/latest/Options.html#uwsgi-core

# Who will run the code / Hint: in emperor-tyrant mode uid & gid setting will be
# ignored [1].  Mode emperor-tyrant is the default on fedora (/etc/uwsgi.ini).
#
# [1] https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting
#
uid = searxng
gid = searxng

# set (python) default encoding UTF-8
env = LANG=C.UTF-8
env = LANGUAGE=C.UTF-8
env = LC_ALL=C.UTF-8

# chdir to specified directory before apps loading
chdir = /usr/local/searxng/searxng-src/searx

# SearXNG configuration (settings.yml)
env = SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml

# disable logging for privacy
disable-logging = true

# The right granted on the created socket
chmod-socket = 666

# Plugin to use and interpreter config
single-interpreter = true

# enable master process
master = true

# load apps in each worker instead of the master
lazy-apps = true

# load uWSGI plugins
plugin = python3,http

# By default the Python plugin does not initialize the GIL.  This means your
# app-generated threads will not run.  If you need threads, remember to enable
# them with enable-threads.  Running uWSGI in multithreading mode (with the
# threads options) will automatically enable threading support. This *strange*
# default behaviour is for performance reasons.
enable-threads = true

# Number of workers (usually CPU count)
workers = %k
threads = 4

# plugin: python
# --------------
#
# https://uwsgi-docs.readthedocs.io/en/latest/Options.html#plugin-python

# load a WSGI module
module = searx.webapp

# set PYTHONHOME/virtualenv
virtualenv = /usr/local/searxng/searx-pyenv

# add directory (or glob) to pythonpath
pythonpath = /usr/local/searxng/searxng-src

# speak to upstream
# -----------------

socket = /usr/local/searxng/run/socket
buffer-size = 8192

offload-threads = %k

```

```
# -*- mode: conf; coding: utf-8  -*-
[uwsgi]

# uWSGI core
# ----------
#
# https://uwsgi-docs.readthedocs.io/en/latest/Options.html#uwsgi-core

# Who will run the code
uid = searxng
gid = searxng

# set (python) default encoding UTF-8
env = LANG=C.UTF-8
env = LANGUAGE=C.UTF-8
env = LC_ALL=C.UTF-8

# chdir to specified directory before apps loading
chdir = /usr/local/searxng/searxng-src/searx

# SearXNG configuration (settings.yml)
env = SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml

# disable logging for privacy
logger = systemd
disable-logging = true

# The right granted on the created socket
chmod-socket = 666

# Plugin to use and interpreter config
single-interpreter = true

# enable master process
master = true

# load apps in each worker instead of the master
lazy-apps = true

# load uWSGI plugins
plugin = python

# By default the Python plugin does not initialize the GIL.  This means your
# app-generated threads will not run.  If you need threads, remember to enable
# them with enable-threads.  Running uWSGI in multithreading mode (with the
# threads options) will automatically enable threading support. This *strange*
# default behaviour is for performance reasons.
enable-threads = true

# Number of workers (usually CPU count)
workers = %k
threads = 4

# plugin: python
# --------------
#
# https://uwsgi-docs.readthedocs.io/en/latest/Options.html#plugin-python

# load a WSGI module
module = searx.webapp

# set PYTHONHOME/virtualenv
virtualenv = /usr/local/searxng/searx-pyenv

# add directory (or glob) to pythonpath
pythonpath = /usr/local/searxng/searxng-src

# speak to upstream
# -----------------

socket = /usr/local/searxng/run/socket
buffer-size = 8192

offload-threads = %k

```

```
# -*- mode: conf; coding: utf-8  -*-
[uwsgi]

# uWSGI core
# ----------
#
# https://uwsgi-docs.readthedocs.io/en/latest/Options.html#uwsgi-core

# Who will run the code / Hint: in emperor-tyrant mode uid & gid setting will be
# ignored [1].  Mode emperor-tyrant is the default on fedora (/etc/uwsgi.ini).
#
# [1] https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting
#
uid = searxng
gid = searxng

# set (python) default encoding UTF-8
env = LANG=C.UTF-8
env = LANGUAGE=C.UTF-8
env = LC_ALL=C.UTF-8

# chdir to specified directory before apps loading
chdir = /usr/local/searxng/searxng-src/searx

# SearXNG configuration (settings.yml)
env = SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml

# disable logging for privacy
disable-logging = true

# The right granted on the created socket
chmod-socket = 666

# Plugin to use and interpreter config
single-interpreter = true

# enable master process
master = true

# load apps in each worker instead of the master
lazy-apps = true

# load uWSGI plugins
plugin = python3,http

# By default the Python plugin does not initialize the GIL.  This means your
# app-generated threads will not run.  If you need threads, remember to enable
# them with enable-threads.  Running uWSGI in multithreading mode (with the
# threads options) will automatically enable threading support. This *strange*
# default behaviour is for performance reasons.
enable-threads = true

# Number of workers (usually CPU count)
workers = %k
threads = 4

# plugin: python
# --------------
#
# https://uwsgi-docs.readthedocs.io/en/latest/Options.html#plugin-python

# load a WSGI module
module = searx.webapp

# set PYTHONHOME/virtualenv
virtualenv = /usr/local/searxng/searx-pyenv

# add directory (or glob) to pythonpath
pythonpath = /usr/local/searxng/searxng-src

# speak to upstream
# -----------------

socket = /usr/local/searxng/run/socket
buffer-size = 8192

offload-threads = %k

```

## Pitfalls of the Tyrant mode
The implementation of the process owners and groups in the [Tyrant mode](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting) is somewhat unusual and requires special consideration. In [Tyrant mode](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting) mode the Emperor will run the vassal using the UID/GID of the vassal configuration file (user and group of the app `.ini` file).
Without option `emperor-tyrant-initgroups=true` in `/etc/uwsgi.ini` the process won’t get the additional groups, but this option is not available in 2.0.x branch (see [#2099@uWSGI](https://github.com/unbit/uwsgi/issues/2099)) the feature [#752@uWSGI](https://github.com/unbit/uwsgi/pull/752) has been merged (on Oct. 2014) to the master branch of uWSGI but had never been released; the last major release is from Dec. 2013, since the there had been only bugfix releases (see [#2425uWSGI](https://github.com/unbit/uwsgi/issues/2425)). To shorten up:
> **In Tyrant mode, there is no way to get additional groups, and the uWSGI process misses additional permissions that may be needed.**
For example on Fedora (RHEL): If you try to install a valkey DB with socket communication and you want to connect to it from the SearXNG uWSGI, you will see a _Permission denied_ in the log of your instance:
```
ERROR:searx.valkeydb: [searxng (993)] can't connect valkey DB ...
ERROR:searx.valkeydb:   Error 13 connecting to unix socket: /usr/local/searxng-valkey/run/valkey.sock. Permission denied.
ERROR:searx.plugins.limiter: init limiter DB failed!!!

```

Even if your _searxng_ user of the uWSGI process is added to additional groups to give access to the socket from the valkey DB:
```
$ groups searxng
searxng : searxng searxng-valkey

```

To see the effective groups of the uwsgi process, you have to look at the status of the process, by example:
```
$ ps -aef | grep '/usr/sbin/uwsgi --ini searxng.ini'
searxng       93      92  0 12:43 ?        00:00:00 /usr/sbin/uwsgi --ini searxng.ini
searxng      186      93  0 12:44 ?        00:00:01 /usr/sbin/uwsgi --ini searxng.ini

```

Here you can see that the additional “Groups” of PID 186 are unset (missing gid of `searxng-valkey`):
```
$ cat /proc/186/task/186/status
...
Uid:      993     993     993     993
Gid:      993     993     993     993
FDSize:   128
Groups:
...

```
