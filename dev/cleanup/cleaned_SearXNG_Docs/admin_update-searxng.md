<!-- source: https://docs.searxng.org/admin/update-searxng.html -->

# SearXNG maintenance
**Further reading:**
## How to update
How to update depends on the [Installation](https://docs.searxng.org/admin/installation.html#installation) method. If you have used the [Installation Script](https://docs.searxng.org/admin/installation-scripts.html#installation-scripts), use the `update` command from the [utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh) script.
```
sudo -H ./utils/searxng.sh instance update

```

## How to inspect & debug
How to debug depends on the [Installation](https://docs.searxng.org/admin/installation.html#installation) method. If you have used the [Installation Script](https://docs.searxng.org/admin/installation-scripts.html#installation-scripts), use the `inspect` command from the [utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh) script.
```
sudo -H ./utils/searxng.sh instance inspect

```

## Migrate and stay tuned!
> **Info:**
  * [PR 1332](https://github.com/searxng/searxng/pull/1332)
  * [PR 456](https://github.com/searxng/searxng/pull/456)
  * [A comment about rolling release](https://github.com/searxng/searxng/pull/446#issuecomment-954730358)

SearXNG is a _rolling release_ ; each commit to the master branch is a release. SearXNG is growing rapidly, the services and opportunities are change every now and then, to name just a few:
  * Bot protection has been switched from filtron to SearXNG’s [limiter](https://docs.searxng.org/admin/searx.limiter.html#limiter), this requires a [Valkey](https://docs.searxng.org/admin/settings/settings_valkey.html#settings-valkey) database.

To stay tuned and get in use of the new features, instance maintainers have to update the SearXNG code regularly (see [How to update](https://docs.searxng.org/admin/update-searxng.html#update-searxng)). As the above examples show, this is not always enough, sometimes services have to be set up or reconfigured and sometimes services that are no longer needed should be uninstalled.
Here you will find a list of changes that affect the infrastructure. Please check to what extent it is necessary to update your installations: 

[PR 1595](https://github.com/searxng/searxng/pull/1595): `[fix] uWSGI: increase buffer-size` 
    
Re-install uWSGI ([utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh)) or fix your uWSGI `searxng.ini` file manually.
### Check after Installation
Once you have done your installation, you can run a SearXNG _check_ procedure, to see if there are some left overs. In this example there exists a _old_ `/etc/searx/settings.yml`:
```
$ sudo -H ./utils/searxng.sh instance check

SearXNG checks
--------------
ERROR: settings.yml in /etc/searx/ is deprecated, move file to folder /etc/searxng/
...
INFO    searx.valkeydb                 : connecting to Valkey db=0 path='/usr/local/searxng-valkey/run/valkey.sock'
INFO    searx.valkeydb                 : connected to Valkey

```
