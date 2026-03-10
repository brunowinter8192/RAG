<!-- source: https://docs.searxng.org/admin/installation-nginx.html -->

# NGINX
This section explains how to set up a SearXNG instance using the HTTP server [nginx](https://docs.nginx.com/nginx/admin-guide/). If you have used the [Installation Script](https://docs.searxng.org/admin/installation-scripts.html#installation-scripts) and do not have any special preferences you can install the [SearXNG site](https://docs.searxng.org/admin/installation-nginx.html#nginx-searxng-site) using [searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh-overview):
```
$ sudo -H ./utils/searxng.sh install nginx

```

If you have special interests or problems with setting up nginx, the following section might give you some guidance.
further reading
  * [nginx](https://docs.nginx.com/nginx/admin-guide/)
  * [nginx beginners guide](https://nginx.org/en/docs/beginners_guide.html)
  * [nginx server configuration](https://docs.nginx.com/nginx/admin-guide/web-server/web-server/#setting-up-virtual-servers)
  * [Getting Started wiki](https://www.nginx.com/resources/wiki/start/)
  * [uWSGI support from nginx](https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html)

## The nginx HTTP server
If [nginx](https://docs.nginx.com/nginx/admin-guide/) is not installed, install it now.
Ubuntu / debianArch LinuxFedora / RHEL
```
sudo -H apt-get install nginx

```

```
sudo -H pacman -S nginx-mainline
sudo -H systemctl enable nginx
sudo -H systemctl start nginx

```

```
sudo -H dnf install nginx
sudo -H systemctl enable nginx
sudo -H systemctl start nginx

```

Now at <http://localhost> you should see a _Welcome to nginx!_ page, on Fedora you see a _Fedora Webserver - Test Page_. The test page comes from the default [nginx server configuration](https://docs.nginx.com/nginx/admin-guide/web-server/web-server/#setting-up-virtual-servers). How this default site is configured, depends on the linux distribution:
Ubuntu / debianArch LinuxFedora / RHEL
```
less /etc/nginx/nginx.conf

```

There is one line that includes site configurations from:
```
include /etc/nginx/sites-enabled/*;

```

```
less /etc/nginx/nginx.conf

```

There is a configuration section named `server`:
```
server {
    listen       80;
    server_name  localhost;
    # ...
}

```

```
less /etc/nginx/nginx.conf

```

There is one line that includes site configurations from:
```
include /etc/nginx/conf.d/*.conf;

```

## NGINX’s SearXNG site
Now you have to create a configuration file (`searxng.conf`) for the SearXNG site. If [nginx](https://docs.nginx.com/nginx/admin-guide/) is new to you, the [nginx beginners guide](https://nginx.org/en/docs/beginners_guide.html) is a good starting point and the [Getting Started wiki](https://www.nginx.com/resources/wiki/start/) is always a good resource _to keep in the pocket_.
Depending on what your SearXNG installation is listening on, you need a http or socket communication to upstream.
sockethttp
```
location /searxng {

    uwsgi_pass unix:///usr/local/searxng/run/socket;

    include uwsgi_params;

    uwsgi_param    HTTP_HOST             $host;
    uwsgi_param    HTTP_CONNECTION       $http_connection;

    # see flaskfix.py
    uwsgi_param    HTTP_X_FORWARDED_PROTO  $scheme;
    uwsgi_param    HTTP_X_SCRIPT_NAME    /searxng;

    # see botdetection/trusted_proxies.py
    uwsgi_param    HTTP_X_REAL_IP        $remote_addr;
    uwsgi_param    HTTP_X_FORWARDED_FOR  $proxy_add_x_forwarded_for;
}

# To serve the static files via the HTTP server
#
# location /searxng/static/ {
#     alias /usr/local/searxng/searxng-src/searx/static/;
# }

```

```
location /searxng {

    proxy_pass http://127.0.0.1:8888;

    proxy_set_header   Host             $host;
    proxy_set_header   Connection       $http_connection;

    # see flaskfix.py
    proxy_set_header   X-Forwarded-Proto $scheme;
    proxy_set_header   X-Script-Name    /searxng;

    # see botdetection/trusted_proxies.py
    proxy_set_header   X-Real-IP        $remote_addr;
    proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;

    # proxy_buffering  off;
    # proxy_request_buffering off;
    # proxy_buffer_size 8k;

}

# To serve the static files via the HTTP server
#
# location /searxng/static/ {
#     alias /usr/local/searxng/searxng-src/searx/static/;
# }

```

The [Installation Script](https://docs.searxng.org/admin/installation-scripts.html#installation-scripts) installs the [reference setup](https://docs.searxng.org/admin/installation-searxng.html#use-default-settings-yml) and a [uWSGI setup](https://docs.searxng.org/admin/installation-uwsgi.html#uwsgi-setup) that listens on a socket by default.
Ubuntu / debianArch LinuxFedora / RHEL
Create configuration at `/etc/nginx/sites-available/` and place a symlink to `sites-enabled`:
```
sudo -H ln -s /etc/nginx/sites-available/searxng.conf \
              /etc/nginx/sites-enabled/searxng.conf

```

In the `/etc/nginx/nginx.conf` file, in the `server` section add a [include](https://nginx.org/en/docs/ngx_core_module.html#include) directive:
```
server {
    # ...
    include /etc/nginx/default.d/*.conf;
    # ...
}

```

Create two folders, one for the _available sites_ and one for the _enabled sites_ :
```
mkdir -p /etc/nginx/default.d
mkdir -p /etc/nginx/default.apps-available

```

Create configuration at `/etc/nginx/default.apps-available` and place a symlink to `default.d`:
```
sudo -H ln -s /etc/nginx/default.apps-available/searxng.conf \
              /etc/nginx/default.d/searxng.conf

```

Create a folder for the _available sites_ :
```
mkdir -p /etc/nginx/default.apps-available

```

Create configuration at `/etc/nginx/default.apps-available` and place a symlink to `conf.d`:
```
sudo -H ln -s /etc/nginx/default.apps-available/searxng.conf \
              /etc/nginx/conf.d/searxng.conf

```

Restart services:
Ubuntu / debianArch LinuxFedora / RHEL
```
sudo -H systemctl restart nginx
sudo -H service uwsgi restart searxng

```

```
sudo -H systemctl restart nginx
sudo -H systemctl restart uwsgi@searxng

```

```
sudo -H systemctl restart nginx
sudo -H touch /etc/uwsgi.d/searxng.ini

```

## Disable logs
For better privacy you can disable nginx logs in `/etc/nginx/nginx.conf`.
```
http {
    # ...
    access_log /dev/null;
    error_log  /dev/null;
    # ...
}

```
