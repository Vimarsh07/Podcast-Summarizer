from db import already_processed, save_episode
from rss_handler import parse_feed, extract_transcript_if_present
from downloader import download_audio
from transcriber import transcribe
from summarizer import summarize_with_openai
from pathlib import Path

with open("feeds.txt") as f:
    feeds = f.readlines()

Path("audio").mkdir(exist_ok=True)

for feed_url in feeds:
    for entry in parse_feed(feed_url.strip()):
        guid = entry.get('id') or entry.get('guid') or entry.get('link')
        if already_processed(guid):
            continue

        title = entry.title
        podcast = entry.get('itunes_author', '')
        pub_date = entry.get('published', '')
        audio_url = entry.enclosures[0].href

        transcript_text = extract_transcript_if_present(entry)

        if transcript_text:
            print("Transcript found in feed.")
            summary = summarize_with_openai(transcript_text)
        else:
            print("No transcript found. Downloading and transcribing...")
            audio_file = f"audio/{guid[:10]}.mp3"
            download_audio(audio_url, audio_file)
            transcript = transcribe(audio_file)
            transcript_text = "\n".join(f"[{s['speaker']}] {s['text']}" for s in transcript)
            summary = summarize_with_openai(transcript_text)

        save_episode(guid, podcast, title, pub_date, audio_url, transcript_text, summary)
        print(f"✅ Processed: {title}\n")
