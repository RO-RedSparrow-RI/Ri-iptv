#!/usr/bin/env python3
"""
Builds one filtered M3U from public IPTV-org playlists.
Only public/community-listed streams are included. Availability and rights vary by channel/region.
"""
import csv, io, re, urllib.request
from collections import OrderedDict

BASE = "https://iptv-org.github.io/iptv"
SOURCES = {
    "india": f"{BASE}/countries/in.m3u",
    "hin": f"{BASE}/languages/hin.m3u",
    "mar": f"{BASE}/languages/mar.m3u",
    "eng": f"{BASE}/languages/eng.m3u",
    "movies": f"{BASE}/categories/movies.m3u",
    "music": f"{BASE}/categories/music.m3u",
    "news": f"{BASE}/categories/news.m3u",
    "kids": f"{BASE}/categories/kids.m3u",
    "animation": f"{BASE}/categories/animation.m3u",
    "documentary": f"{BASE}/categories/documentary.m3u",
    "sports": f"{BASE}/categories/sports.m3u",
    "general": f"{BASE}/categories/general.m3u",
    "entertainment": f"{BASE}/categories/entertainment.m3u",
}
UA = "Mozilla/5.0 (compatible; PersonalM3UBuilder/1.0)"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def parse_m3u(text):
    rows, meta, name = [], "", ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF:"):
            meta = line
            name = line.split(",", 1)[-1].strip() if "," in line else "Unknown"
        elif line and not line.startswith("#") and meta:
            rows.append({"meta": meta, "name": name, "url": line})
            meta = ""
    return rows

def lang(row):
    m = re.search(r'tvg-language="([^"]+)"', row["meta"], re.I)
    if m:
        v = m.group(1).lower()
        if "marathi" in v: return "mar"
        if "hindi" in v: return "hin"
        if "english" in v: return "eng"
    # Language playlist membership is used below when metadata is absent.
    return ""

def clean(row):
    blob = (row["meta"] + " " + row["name"]).lower()
    banned = ("relig", "worship", "prayer", "temple", "church", "mosque",
              "ministry", "devotional", "bhajan", "satsang", "gospel", "quran")
    return not any(x in blob for x in banned)

def add_group(out, group, rows, allowed_urls=None):
    seen = set()
    for r in rows:
        if allowed_urls is not None and r["url"] not in allowed_urls:
            continue
        if not clean(r) or r["url"] in seen:
            continue
        seen.add(r["url"])
        meta = re.sub(r'group-title="[^"]*"', '', r["meta"])
        meta = re.sub(r'\s{2,}', ' ', meta).rstrip()
        meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"', 1)
        if "group-title=" not in meta:
            meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"', 1)
        out.append((meta, r["url"]))

def main():
    data = {k: parse_m3u(fetch(v)) for k, v in SOURCES.items()}
    sets = {k: {r["url"] for r in v} for k, v in data.items()}
    india = sets["india"]
    hin, mar, eng = sets["hin"], sets["mar"], sets["eng"]

    # Intersections provide language-specific category sets. Indian-only groups
    # are additionally intersected with the India country playlist.
    sections = []
    sections.append(("Movies - Hindi", data["movies"], hin))
    sections.append(("Movies - Marathi", data["movies"], mar))
    sections.append(("Movies - English", data["movies"], eng))
    sections.append(("Music - Hindi", data["music"], hin))
    sections.append(("Music - Marathi", data["music"], mar))
    sections.append(("News - India Hindi", data["news"], hin & india))
    sections.append(("News - India English", data["news"], eng & india))
    sections.append(("Cartoons - Hindi", data["kids"] + data["animation"], hin))
    sections.append(("Cartoons - English", data["kids"] + data["animation"], eng))
    sections.append(("Documentary - Hindi", data["documentary"], hin))
    sections.append(("Documentary - English", data["documentary"], eng))
    sections.append(("Sports - Hindi", data["sports"], hin))
    sections.append(("Sports - English", data["sports"], eng))
    sections.append(("Indian General - Hindi", data["general"] + data["entertainment"], hin & india))
    sections.append(("Indian General - Marathi", data["general"] + data["entertainment"], mar & india))
    sections.append(("Indian General - English", data["general"] + data["entertainment"], eng & india))
    sections.append(("Marathi Channels", data["india"] + data["general"] + data["entertainment"], mar & india))

    out = []
    for group, rows, allow in sections:
        add_group(out, group, rows, allow)

    # Remove duplicate URLs across sections while preserving first matching category.
    final, seen = [], set()
    for meta, url in out:
        if url not in seen:
            final.extend([meta, url])
            seen.add(url)

    header = '#EXTM3U x-tvg-url="https://iptv-org.github.io/epg/guides/in.xml"\n'
    Path("playlist.m3u").write_text(header + "\n".join(final) + "\n", encoding="utf-8")
    print(f"Created playlist.m3u with {len(seen)} unique stream URLs.")
    print("Note: this source generally publishes a preferred stream per channel; backup URLs are not guaranteed.")

if __name__ == "__main__":
    main()
