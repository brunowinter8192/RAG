<!-- source: https://docs.searxng.org/dev/engines/online/mastodon.html -->

# Mastodon
[Mastodon](https://mastodon.social) is an open source alternative to large social media platforms like Twitter/X, Facebook, …
Since it’s federated and self-hostable, there’s a large amount of available instances, which can be chosen instead by modifying `base_url`.
We use their official [API](https://docs.joinmastodon.org/api/) for searching, but unfortunately, their Search [API](https://docs.joinmastodon.org/api/) forbids pagination without OAuth.
That’s why we use tootfinder.ch for finding posts, which doesn’t support searching for users, accounts or other types of content on Mastodon however.
