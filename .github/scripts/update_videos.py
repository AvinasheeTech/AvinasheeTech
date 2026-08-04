"""
Fetches the latest uploads from the Avinashee Tech YouTube channel via the
public RSS feed (no API key required) and rewrites the section of README.md
between <!-- START_YOUTUBE_SECTION --> and <!-- END_YOUTUBE_SECTION -->.
"""

import re
import urllib.request
import xml.etree.ElementTree as ET

CHANNEL_ID = "UCnGAbDT2-M_of7o2Wc3Ur5g"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
README_PATH = "README.md"
MAX_VIDEOS = 5

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
}


def fetch_latest_videos():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    entries = root.findall("atom:entry", NS)[:MAX_VIDEOS]

    videos = []
    for entry in entries:
        title = entry.find("atom:title", NS).text
        video_id = entry.find("{http://www.youtube.com/xml/schemas/2015}videoId")
        if video_id is None:
            link_el = entry.find("atom:link", NS)
            url = link_el.get("href") if link_el is not None else "#"
        else:
            url = f"https://www.youtube.com/watch?v={video_id.text}"
        thumb_el = entry.find("media:group/media:thumbnail", NS)
        thumb = thumb_el.get("url") if thumb_el is not None else ""
        videos.append({"title": title, "url": url, "thumb": thumb})
    return videos


def build_markdown(videos):
    if not videos:
        return "_Couldn't fetch videos this run — check back soon._"

    rows = []
    for v in videos:
        rows.append(
            f'<a href="{v["url"]}"><img src="{v["thumb"]}" width="200" alt="{v["title"]}"></a><br>'
            f'<a href="{v["url"]}"><b>{v["title"]}</b></a>'
        )

    cells = "\n\n".join(f"<td align=\"center\">{row}</td>" for row in rows)
    table = f'<table><tr>\n{cells}\n</tr></table>'
    return table


def update_readme(markdown_block):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(<!-- START_YOUTUBE_SECTION -->)(.*?)(<!-- END_YOUTUBE_SECTION -->)",
        re.DOTALL,
    )
    replacement = f"\\1\n{markdown_block}\n\\3"
    new_content, count = pattern.subn(replacement, content)

    if count == 0:
        raise RuntimeError(
            "Markers not found in README.md — expected "
            "<!-- START_YOUTUBE_SECTION --> ... <!-- END_YOUTUBE_SECTION -->"
        )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    videos = fetch_latest_videos()
    markdown_block = build_markdown(videos)
    update_readme(markdown_block)
    print(f"Updated README with {len(videos)} videos.")
