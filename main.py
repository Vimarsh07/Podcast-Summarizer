# ======================== main.py ========================
import os
from dateutil import parser as dt_parser
from db import already_processed, save_episode
from rss_handler import parse_feed, extract_transcript_if_present
from downloader import download_audio
from transcriber import transcribe
from summarizer import summarize_with_openai
from pathlib import Path

Path("audio").mkdir(exist_ok=True)

with open("feeds.txt") as f:
    feeds = [u.strip() for u in f if u.strip()]

for feed_url in feeds:
    entries = parse_feed(feed_url)
    if not entries:
        continue

    entries.sort(key=lambda e: dt_parser.parse(e.get("published", "")), reverse=True)
    entry = entries[0]

    guid = entry.get("id") or entry.get("guid") or entry.get("link")
    if already_processed(guid):
        print(f"Skipping already-processed: {guid}")
        continue

    title = entry.title
    podcast = entry.get("itunes_author", "")
    pub_date = entry.get("published", "")
    audio_url = entry.enclosures[0].href

    transcript_text = extract_transcript_if_present(entry)
    if transcript_text:
        summary = summarize_with_openai(transcript_text)
    else:
        audio_file = f"audio/{guid[:10]}.mp3"
        download_audio(audio_url, audio_file)
        segments = transcribe(audio_file)
        transcript_text = "\n".join(f"[{s['speaker']}] {s['text']}" for s in segments)
        summary = summarize_with_openai(transcript_text)

    save_episode(guid, podcast, title, pub_date, audio_url, transcript_text, summary)
    print(f"✅ Processed only latest: {title}\n")
