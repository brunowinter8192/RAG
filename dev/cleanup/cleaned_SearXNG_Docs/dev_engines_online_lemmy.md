<!-- source: https://docs.searxng.org/dev/engines/online/lemmy.html -->

# Lemmy
Contents
This engine uses the Lemmy API (<https://lemmy.ml/api/v3/search>), which is documented at [lemmy-js-client](https://join-lemmy.org/api/modules.html) / [Interface Search](https://join-lemmy.org/api/interfaces/Search.html). Since Lemmy is federated, results are from many different, independent lemmy instances, and not only the official one.
## Configuration
The engine has the following additional settings:
This implementation is used by different lemmy engines in the [settings.yml](https://docs.searxng.org/admin/settings/settings_engines.html#settings-engines):
```
- name: lemmy communities
  lemmy_type: Communities
  ...
- name: lemmy users
  lemmy_type: Users
  ...
- name: lemmy posts
  lemmy_type: Posts
  ...
- name: lemmy comments
  lemmy_type: Comments
  ...

```

## Implementations
**engines.lemmy.base_url** = `'https://lemmy.ml/'`
By default, <https://lemmy.ml> is used for providing the results. If you want to use a different lemmy instance, you can specify `base_url`. 

**engines.lemmy.lemmy_type** = `'Communities'`
Any of `Communities`, `Users`, `Posts`, `Comments`
