<!-- source: https://docs.searxng.org/utils/index.html -->

# DevOps tooling box
In the folder [git://utils/](https://github.com/searxng/searxng/blob/master/utils/) we maintain some tools useful for administrators and developers.
  * [`utils/searxng.sh`](https://docs.searxng.org/utils/searxng.sh.html)
## Common command environments
The scripts in our tooling box often dispose of common environments: 

`FORCE_TIMEOUT`environment 
    
Sets timeout for interactive prompts. If you want to run a script in batch job, with defaults choices, set `FORCE_TIMEOUT=0`. By example; to install a SearXNG server and nginx proxy use:
```
$ FORCE_TIMEOUT=0 ./utils/searxng.sh install all
$ FORCE_TIMEOUT=0 ./utils/searxng.sh install nginx

```
