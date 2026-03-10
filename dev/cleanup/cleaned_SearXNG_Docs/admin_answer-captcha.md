<!-- source: https://docs.searxng.org/admin/answer-captcha.html -->

# Answer CAPTCHA from server’s IP
With a SSH tunnel we can send requests from server’s IP and solve a CAPTCHA that blocks requests from this IP. If your SearXNG instance is hosted at `example.org` and your login is `user` you can setup a proxy simply by [ssh](https://manpages.debian.org/jump?q=ssh):
```
# SOCKS server: socks://127.0.0.1:8080

$ ssh -q -N -D 8080 user@example.org

```

The `socks://localhost:8080` from above can be tested by:
server’s IPdesktop’s IP
```
$ curl -x socks://127.0.0.1:8080 http://ipecho.net/plain
n.n.n.n

```

```
$ curl http://ipecho.net/plain
x.x.x.x

```

In the settings of the WEB browser open the _“Network Settings”_ and setup a proxy on `SOCKS5 127.0.0.1:8080` (see screenshot below). In the WEB browser check the IP from the server is used:
  * <http://ipecho.net/plain>

Now open the search engine that blocks requests from your server’s IP. If you have [issues with the qwant engine](https://github.com/searxng/searxng/issues/2011#issuecomment-1553317619), solve the CAPTCHA from [qwant.com](https://www.qwant.com/).
* * *
Firefox
![FFox proxy on SOCKS5, 127.0.0.1:8080](https://docs.searxng.org/_images/ffox-setting-proxy-socks.png)
Fig. 1 Firefox’s network settings
[ssh](https://manpages.debian.org/jump?q=ssh) manual: 

-D [bind_address:]port
    
Specifies a local “dynamic” application-level port forwarding. This works by allocating a socket to listen to port on the local side .. Whenever a connection is made to this port, the connection is forwarded over the secure channel, and the application protocol is then used to determine where to connect to from the remote machine .. ssh will act as a SOCKS server .. 

`-N`
    
Do not execute a remote command. This is useful for just forwarding ports.
