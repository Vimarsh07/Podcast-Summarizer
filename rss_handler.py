import feedparser
import requests

def parse_feed(feed_url):
    return feedparser.parse(feed_url).entries

def extract_transcript_if_present(entry):
    for link in entry.get("links", []):
        if 'transcript' in link.get('rel', ''):
            try:
                return requests.get(link["href"]).text
            except:
                pass

    if entry.get("summary_detail"):
        text = entry["summary_detail"].get("value", "")
        if len(text.split()) > 100:
            return text

    if entry.get("content"):
        content_val = entry["content"][0].get("value", "")
        if len(content_val.split()) > 100:
            return content_val

    return None