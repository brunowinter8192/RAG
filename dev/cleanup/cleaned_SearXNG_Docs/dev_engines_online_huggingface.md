<!-- source: https://docs.searxng.org/dev/engines/online/huggingface.html -->

# Hugging Face
[Hugging Face](https://huggingface.co) search engine for SearXNG.
## Configuration
The engine has the following additional settings:
  * [`huggingface_endpoint`](https://docs.searxng.org/dev/engines/online/huggingface.html#searx.engines.huggingface.huggingface_endpoint "searx.engines.huggingface.huggingface_endpoint")

Configurations for endpoints:
```
- name: huggingface
  engine: huggingface
  shortcut: hf

- name: huggingface datasets
  huggingface_endpoint: datasets
  engine: huggingface
  shortcut: hfd

- name: huggingface spaces
  huggingface_endpoint: spaces
  engine: huggingface
  shortcut: hfs

```

## Implementations 

**engines.huggingface.huggingface_endpoint** = `'models'`
Hugging Face supports datasets, models, spaces as search endpoint.
  * `datasets`: search for datasets
  * `models`: search for models
  * `spaces`: search for spaces
