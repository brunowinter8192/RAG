<!-- source: https://docs.searxng.org/dev/engines/online/mrs.html -->

# Matrix Rooms Search (MRS)
Contents
Matrix Rooms Search - a fully-featured, standalone, matrix rooms search service.
## Configuration
The engine has the following mandatory settings:
  * `base_url`

```
- name: MRS
  engine: mrs
  base_url: https://mrs-host
  ...

```

## Implementation
**engines.mrs.init(_engine_settings_)**
The `base_url` must be set in the configuration, if `base_url` is not set, a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") is raised during initialization.
