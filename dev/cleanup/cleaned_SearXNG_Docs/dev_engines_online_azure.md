<!-- source: https://docs.searxng.org/dev/engines/online/azure.html -->

# Azure Resources
Engine for Azure resources. This engine mimics the standard search bar in Azure Portal (for resources and resource groups).
## Configuration
You must [register an application in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) and assign it the ‘Reader’ role in your subscription.
To use this engine, add an entry similar to the following to your engine list in `settings.yml`:
```
- name: azure
  engine: azure
  ...
  azure_tenant_id: "your_tenant_id"
  azure_client_id: "your_client_id"
  azure_client_secret: "your_client_secret"
  azure_token_expiration_seconds: 5000

```

**engines.azure.azure_token_expiration_seconds** = `5000`
Time for which an auth token is valid (sec.) 

searx.engines.azure.CACHE _:[ EngineCache](https://docs.searxng.org/dev/engines/enginelib.html#searx.enginelib.EngineCache "searx.enginelib.EngineCache")_ 
    
Persistent (SQLite) key/value cache that deletes its values after `expire` seconds. 

searx.engines.azure.setup(_engine_settings :[dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") 
    
Initialization of the engine.
  * Instantiate a cache for this engine ([`CACHE`](https://docs.searxng.org/dev/engines/online/azure.html#searx.engines.azure.CACHE "searx.engines.azure.CACHE")).
  * Checks whether the tenant_id, client_id and client_secret are set, otherwise the engine is inactive.

searx.engines.azure.authenticate(_t_id :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _c_id :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _c_secret :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") 
    
Authenticates to Azure using Oauth2 Client Credentials Flow and returns an access token.
