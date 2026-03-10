<!-- source: https://docs.searxng.org/dev/engines/online/moviepilot.html -->

# Moviepilot
Moviepilot is a German movie database, similar to IMDB or TMDB. It doesn’t have any official API, but it uses JSON requests internally to fetch search results and suggestions, that’s being used in this implementation.
Moviepilot additionally allows to discover movies by certain categories or filters, hence we provide the following syntax:
  * Any normal search query -> Fetch search results by the query
  * A query containing one of the category identifiers `fsk`, `genre`, `jahr`, `jahrzent`, `land`, `online`, `stimmung` will be used to search trending items by the provided filters, which are appended to the filter category after a `-`.

Search examples:
  * Normal: `!mp Tom Cruise`
  * By filter: `!mp person-Ryan-Gosling`
  * By filter: `!mp fsk-0 land-deutschland genre-actionfilm`
  * By filter: `!mp jahrzehnt-2020er online-netflix`

For a list of all public filters, observe the url path when browsing
  * <https://www.moviepilot.de/filme/beste>.
