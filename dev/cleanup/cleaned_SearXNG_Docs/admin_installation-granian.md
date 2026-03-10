<!-- source: https://docs.searxng.org/admin/installation-granian.html -->

# Granian
further reading
  * [Options](https://github.com/emmett-framework/granian/blob/master/README.md#options)
  * [Workers and threads](https://github.com/emmett-framework/granian/blob/master/README.md#workers-and-threads)
  * [Backpressure](https://github.com/emmett-framework/granian/blob/master/README.md#backpressure)
  * [Runtime mode](https://github.com/emmett-framework/granian/blob/master/README.md#runtime-mode)

Note
Granian will be the future replacement for [uWSGI](https://docs.searxng.org/admin/installation-uwsgi.html#searxng-uwsgi) in SearXNG. At the moment, it’s only officially supported in the [Installation container](https://docs.searxng.org/admin/installation-docker.html#installation-container).
## Installation
We only recommend installing Granian with pip, as officially documented. Run the following command in the Python environment of the SearXNG installation:
```
$ pip install granian

```

## Configuration
Note
It’s not advised to modify the amount of workers, expect increased resource usage and potential issues with [Bot Detection](https://docs.searxng.org/src/searx.botdetection.html#botdetection).
Granian can be configured via option parameters and environment variables (`$GRANIAN_*`).
We provide sane defaults that should fit most use cases, however if you feel you should change something, Granian documents all available parameters in the [Options](https://github.com/emmett-framework/granian/blob/master/README.md#options) section.
