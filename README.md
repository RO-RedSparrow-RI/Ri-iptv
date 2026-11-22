# Custom Master IPTV Playlist Builder

This creates one M3U playlist from public IPTV-org listings, grouped around the requested categories.

## Included groups
- Hindi / Marathi / English movies
- Hindi / Marathi music
- Indian Hindi / English news
- Hindi / English cartoons
- Indian Hindi / Marathi / English general and entertainment channels
- Hindi / English documentaries and sports
- Marathi channels

Religious channels are excluded using both source categories and name-based keyword filtering.

## Important limitations
- This uses community-maintained public streams, not paid broadcaster subscriptions.
- Streams can stop working, be geo-blocked, or change without notice.
- IPTV-org's public playlists generally select a preferred stream for each channel. Multiple backup streams for every channel cannot be guaranteed by this source.
- Language/category metadata can be incomplete, so some desired channels may be missed and occasional misclassification is possible.
- Use only streams you are legally entitled to watch in your location.

## Publish one URL using GitHub (Android-friendly)
1. Create a **public** GitHub repository, for example `my-iptv`.
2. Upload `build_playlist.py` to the repository root.
3. Create `.github/workflows/build.yml` and paste the workflow file supplied in this package.
4. Commit both files.
5. Open the repository's **Actions** tab and run **Build master IPTV playlist** once (or wait for its scheduled run).
6. In repository **Settings → Pages**, set the source to **Deploy from a branch**, choose `main` and `/docs`, then Save.
7. After Pages is published, the single playlist URL is:

   `https://YOUR-USERNAME.github.io/my-iptv/playlist.m3u`

Replace `YOUR-USERNAME` and `my-iptv` with your GitHub username and repository name.

## EPG
For Televizo, you can optionally add this EPG URL:

`https://iptv-org.github.io/epg/guides/in.xml`
