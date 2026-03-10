<!-- source: https://docs.searxng.org/dev/engines/offline/command-line-engines.html -->

# Command Line Engines
> **Info:**
  * [command.py](https://github.com/searxng/searxng/blob/master/searx/engines/command.py)
> **Info:**
Initial sponsored by [Search and Discovery Fund](https://nlnet.nl/discovery) of [NLnet Foundation](https://nlnet.nl/).
With _command engines_ administrators can run engines to integrate arbitrary shell commands.
Attention
When creating and enabling a `command` engine on a public instance, you must be careful to avoid leaking private data.
The easiest solution is to limit the access by setting `tokens` as described in section [Private Engines (tokens)](https://docs.searxng.org/admin/settings/settings_engines.html#private-engines). The engine base is flexible. Only your imagination can limit the power of this engine (and maybe security concerns).
## Configuration
The following options are available: 

`command`:
    
A comma separated list of the elements of the command. A special token `{{QUERY}}` tells where to put the search terms of the user. Example:
```
['ls', '-l', '-h', '{{QUERY}}']

```

`delimiter`:
    
A mapping containing a delimiter `char` and the _titles_ of each element in `keys`. 

`parse_regex`:
    
A dict containing the regular expressions for each result key.
`query_type`:
> The expected type of user search terms. Possible values: `path` and `enum`. 

`path`:
    
> Checks if the user provided path is inside the working directory. If not, the query is not executed. 

`enum`:
    
> Is a list of allowed search terms. If the user submits something which is not included in the list, the query returns an error. 

`query_enum`:
    
A list containing allowed search terms if `query_type` is set to `enum`. 

`working_dir`:
    
The directory where the command has to be executed. Default: `./`. 

`result_separator`:
    
The character that separates results. Default: `\n`.
## Example
The example engine below can be used to find files with a specific name in the configured working directory:
```
- name: find
  engine: command
  command: ['find', '.', '-name', '{{QUERY}}']
  query_type: path
  shortcut: fnd
  delimiter:
      chars: ' '
      keys: ['line']

```

## Implementations
**engines.command.check_parsing_options(_engine_settings_)**
Checks if delimiter based parsing or regex parsing is configured correctly
