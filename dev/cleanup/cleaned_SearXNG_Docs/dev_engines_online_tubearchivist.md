<!-- source: https://docs.searxng.org/dev/engines/online/tubearchivist.html -->

# Tube Archivist
[Tube Archivist](https://www.tubearchivist.com) - _Your self hosted YouTube media server._
This engine connects with a self-hosted instance of [Tube Archivist](https://www.tubearchivist.com) to allow searching for your hosted videos.
[Tube Archivist](https://www.tubearchivist.com) (TA) requires authentication for all image loads via cookie authentication. What this means is that by default, SearXNG will have no way to pull images from TA (as there is no way to pass cookies in a URL string only).
In the meantime while work is done on the TA side, this can be worked around by bypassing auth for images in TA by altering the default TA nginx file.
This is located in the main tubearchivist docker container at:
```
/etc/nginx/sites-available/default

```

It is **strongly** recommended first setting up the intial connection and verying searching works first with broken images, and then attempting this change. This will limit any debugging to only images, rather than tokens/networking.
Steps to enable **unauthenticated** metadata access for channels and videos:
  1. Perform any backups of TA before editing core configurations.
  2. Copy the contents of the file `/etc/nginx/sites-available/default` in the TA docker container
  3. Edit `location /cache/videos` and `location /cache/channels`. Comment out the line `auth_request /api/ping/;` to `# auth_request /api/ping/;`.
  4. Save the file to wherever you normally store your docker configuration.
  5. Mount this new configuration over the default configuration. With `docker run`, this would be:
```
-v ./your-new-config.yml:/etc/nginx/sites-available/default

```

With `docker compose`, this would be:
```
- "./your-new-config.yml:/etc/nginx/sites-available/default:ro"

```

  6. Start the TA container.

After these steps, double check that TA works as normal (nothing should be different on the TA side). Searching again should now show images.
## Configuration
The engine has the following required settings:
Optional settings:
  * [`ta_link_to_mp4`](https://docs.searxng.org/dev/engines/online/tubearchivist.html#searx.engines.tubearchivist.ta_link_to_mp4 "searx.engines.tubearchivist.ta_link_to_mp4")

```
- name: tubearchivist
  engine: tubearchivist
  shortcut: tuba
  base_url:
  ta_token:
  ta_link_to_mp4: true

```

## Implementations 

**engines.tubearchivist.base_url** = `''`
Base URL of the Tube Archivist instance. Fill this in with your own Tube Archivist URL (`http://your-instance:port`). 

**engines.tubearchivist.ta_token** = `''`
The API key to use for [Authorization](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Authorization) header. Can be found under:
> Settings ‣ User ‣ Admin Interface. 

**engines.tubearchivist.ta_link_to_mp4** = `False`
Optional, if true SearXNG will link directly to the mp4 of the video to play in the browser. The default behavior is to link into TubeArchivist’s interface directly. 

searx.engines.tubearchivist.video_response(_resp_ , _results :[EngineResults](https://docs.searxng.org/dev/engines/index.html#searx.result_types.EngineResults "searx.result_types.EngineResults")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") 
    
Parse video response from Tubearchivist instances.
