<!-- source: https://docs.searxng.org/dev/engines/online/repology.html -->

# Repology
[Repology](https://repology.org/docs/about) monitors a huge number of package repositories and other sources comparing packages versions across them and gathering other information.
[Repology](https://repology.org/docs/about) shows you in which repositories a given project is packaged, which version is the latest and which needs updating, who maintains the package, and other related information.
## Configuration
The engine is inactive by default, meaning it is not available in the service. If you want to offer the engine, the `inactive` flag must be set to `false`.
```
- name: repology
  inactive: false

```
