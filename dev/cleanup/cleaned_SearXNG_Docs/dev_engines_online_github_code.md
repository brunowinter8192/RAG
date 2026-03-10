<!-- source: https://docs.searxng.org/dev/engines/online/github_code.html -->

# Github Code
GitHub code search with [search syntax](https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax) as described in [Constructing a search query](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#constructing-a-search-query) in the documentation of GitHub’s REST API.
## Configuration
The engine has the following mandatory setting:
  * [`ghc_auth`](https://docs.searxng.org/dev/engines/online/github_code.html#searx.engines.github_code.ghc_auth "searx.engines.github_code.ghc_auth") Change the authentication method used when using the API, defaults to none.

Optional settings are:
  * 

[`ghc_highlight_matching_lines`](https://docs.searxng.org/dev/engines/online/github_code.html#searx.engines.github_code.ghc_highlight_matching_lines "searx.engines.github_code.ghc_highlight_matching_lines")
    
Control the highlighting of the matched text (turns off/on).
  * 

[`ghc_strip_new_lines`](https://docs.searxng.org/dev/engines/online/github_code.html#searx.engines.github_code.ghc_strip_new_lines "searx.engines.github_code.ghc_strip_new_lines")
    
Strip new lines at the start or end of each code fragment.
  * 

[`ghc_strip_whitespace`](https://docs.searxng.org/dev/engines/online/github_code.html#searx.engines.github_code.ghc_strip_whitespace "searx.engines.github_code.ghc_strip_whitespace")
    
Strip any whitespace at the start or end of each code fragment.
  * 

[`ghc_insert_block_separator`](https://docs.searxng.org/dev/engines/online/github_code.html#searx.engines.github_code.ghc_insert_block_separator "searx.engines.github_code.ghc_insert_block_separator")
    
Add a … between each code fragment before merging them.

```
- name: github code
  engine: github_code
  shortcut: ghc
  ghc_auth:
    type: "none"

- name: github code
  engine: github_code
  shortcut: ghc
  ghc_auth:
    type: "personal_access_token"
    token: "<token>"
  ghc_highlight_matching_lines: true
  ghc_strip_whitespace: true
  ghc_strip_new_lines: true

- name: github code
  engine: github_code
  shortcut: ghc
  ghc_auth:
    type: "bearer"
    token: "<token>"

```

## Implementation
GitHub does not return the code line indices alongside the code fragment in the search API. Since these are not super important for the user experience all the code lines are just relabeled (starting from 1) and appended (a disjoint set of code blocks in a single file might be returned from the API). 

**engines.github_code.ghc_auth** = `{'token': '', 'type': 'none'}`
Change the method of authenticating to the github API.
`type` needs to be one of `none`, `personal_access_token`, or `bearer`. When type is not none a token is expected to be passed as well in `auth.token`.
If there is any privacy concerns about generating a token, one can use the API without authentication. The calls will be heavily rate limited, this is what the API returns on such calls:
```
API rate limit exceeded for <redacted ip>.
(But here's the good news: Authenticated requests get a higher rate limit)

```

The personal access token or a bearer for an org or a group can be generated [in the [GitHub settings](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-code--fine-grained-access-tokens). 

**engines.github_code.ghc_highlight_matching_lines** = `True`
Highlight the matching code lines. 

**engines.github_code.ghc_strip_new_lines** = `True`
Strip leading and trailing newlines for each returned fragment. Single file might return multiple code fragments. 

**engines.github_code.ghc_strip_whitespace** = `False`
Strip all leading and trailing whitespace for each returned fragment. Single file might return multiple code fragments. Enabling this might break code indentation. 

**engines.github_code.ghc_api_version** = `'2022-11-28'`
The version of the GitHub REST API. 

**engines.github_code.ghc_insert_block_separator** = `False`
Each file possibly consists of more than one code block that matches the search, if this is set to true, the blocks will be separated with `...` line. This might break the lexer and thus result in the lack of code highlighting. 

searx.engines.github_code.extract_code(_code_matches :[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]]_) → [tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")],[set](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)")[[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")]] 
    
Iterate over multiple possible matches, for each extract a code fragment. Github additionally sends context for _word_ highlights; pygments supports highlighting lines, as such we calculate which lines to highlight while traversing the text.
