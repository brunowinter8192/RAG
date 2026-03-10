<!-- source: https://docs.searxng.org/dev/engines/online/tagesschau.html -->

# Tagesschau API
ARD: [Tagesschau API](https://github.com/AndreasFischer1985/tagesschau-api/blob/main/README_en.md)
The Tagesschau is a news program of the ARD. Via the [Tagesschau API](https://github.com/AndreasFischer1985/tagesschau-api/blob/main/README_en.md), current news and media reports are available in JSON format. The [Bundesstelle für Open Data](https://github.com/bundesAPI) offers a [OpenAPI](https://swagger.io/specification/) portal at [bundDEV](https://bund.dev/apis) where APIs are documented an can be tested.
This SearXNG engine uses the [/api2u/search](http://tagesschau.api.bund.dev/) API. 

**engines.tagesschau.use_source_url** = `True`
When set to false, display URLs from Tagesschau, and not the actual source (e.g. NDR, WDR, SWR, HR, …)
Note
The actual source may contain additional content, such as commentary, that is not displayed in the Tagesschau.
