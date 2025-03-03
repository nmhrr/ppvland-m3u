import requests
import subprocess
from datetime import datetime, timezone, timedelta

# API Endpoints
STREAMS_API = "https://ppv.land/api/streams"
STREAM_DETAILS_API = "https://ppv.land/api/streams/{}"
OUTPUT_FILE = "ppvland_playlist.m3u"
GITHUB_COMMIT_MESSAGE = "Auto-update M3U playlist"
GITHUB_BRANCH = "main"

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://ppv.land/",
    "Origin": "https://ppv.land"
}

# Define ET timezone (UTC-5 or UTC-4 for daylight saving time)
ET_OFFSET = timedelta(hours=-5)  # Eastern Standard Time (EST)

# Category Emojis
CATEGORY_EMOJIS = {
    "Basketball": "🏀",
    "Football": "🏈",
    "Baseball": "⚾",
    "Hockey": "🏒",
    "Soccer": "⚽",
    "Tennis": "🎾",
    "Wrestling": "🤼",
    "Motorsports": "🏎️",
    "Darts": "🎯",
    "Cricket": "🏏",
    "Arm Wrestling": "💪"
}

def fetch_streams():
    """Fetch the list of available streams from PPV.LAND."""
    print("📡 Fetching streams from PPV.LAND...")
    
    try:
        response = requests.get(STREAMS_API, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to fetch streams! HTTP Status: {response.status_code}")
            return []

        data = response.json()
        streams = []
        for category in data.get("streams", []):
            for stream in category.get("streams", []):
                streams.append({
                    "id": stream["id"],
                    "name": stream["name"],
                    "tag": stream.get("tag", ""),
                    "poster": stream["poster"],
                    "category": category["category"],
                    "start_time": stream.get("starts_at", 0),
                    "end_time": stream.get("ends_at", 0)
                })
        
        streams.sort(key=lambda x: x["start_time"] if x["start_time"] > 0 else float('inf'))
        print(f"✅ Found {len(streams)} streams.")
        return streams
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

def fetch_m3u8_link(stream_id):
    """Fetch the M3U8 link for a given stream ID."""
    print(f"🔍 Fetching M3U8 link for stream ID: {stream_id}")
    
    try:
        response = requests.get(STREAM_DETAILS_API.format(stream_id), headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to fetch details for stream {stream_id}. HTTP {response.status_code}")
            return None

        data = response.json()
        return data["data"].get("m3u8")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for stream {stream_id}: {e}")
        return None

def push_to_github():
    """Commit and push the M3U file to GitHub."""
    print("🚀 Pushing updated M3U file to GitHub...")
    try:
        subprocess.run(["git", "add", OUTPUT_FILE], check=True)
        subprocess.run(["git", "commit", "-m", GITHUB_COMMIT_MESSAGE], check=True)
        subprocess.run(["git", "push", "origin", GITHUB_BRANCH], check=True)
        print("✅ Successfully pushed to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push to GitHub: {e}")

def format_stream_title(category, name, tag, start_time, end_time):
    """Format the stream title with category emoji, name, start/end times, and tag. If the event ended more than a month ago, mark it as 24/7."""
    """Format the stream title with category emoji, name, start/end times, and tag."""
    event_time = datetime.utcfromtimestamp(start_time).replace(tzinfo=timezone.utc) + ET_OFFSET if start_time else None
    end_time_et = datetime.utcfromtimestamp(end_time).replace(tzinfo=timezone.utc) + ET_OFFSET if end_time else None

    current_time = datetime.now(timezone.utc)
    if end_time_et and (current_time - end_time_et) > timedelta(days=30):
        time_label = "24/7"
    elif event_time and end_time_et:
        time_label = f"{event_time.strftime('%I:%M%p')} to {end_time_et.strftime('%I:%M%p')} {event_time.strftime('%m/%d/%y')}"
    else:
        time_label = "Unknown Time"

    emoji = CATEGORY_EMOJIS.get(category, "")
    category_part = f"{emoji} " if emoji else ""
    tag_part = f"- {tag}" if tag else ""
    return f"{category_part}{name} - {time_label} {tag_part}".strip()

def generate_m3u_playlist():
    """Fetch streams, generate M3U, save it to a file, and push to GitHub."""
    streams = fetch_streams()
    if not streams:
        print("❌ No streams available. Exiting.")
        return

    print("📝 Generating M3U playlist...")
    m3u_content = "#EXTM3U\n"
    total_added = 0

    for stream in streams:
        m3u8_url = fetch_m3u8_link(stream["id"])
        if not m3u8_url:
            continue

        stream_title = format_stream_title(stream["category"], stream["name"], stream["tag"], stream["start_time"], stream["end_time"])

        m3u_content += f'#EXTINF:-1 tvg-id="{stream["id"]}" tvg-name="{stream_title}" tvg-logo="{stream["poster"]}",{stream_title}\n'
        m3u_content += f"{m3u8_url}\n"
        total_added += 1

    if total_added == 0:
        print("❌ No valid streams with M3U8 links were found. Exiting.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✅ M3U Playlist generated successfully with {total_added} streams: {OUTPUT_FILE}")
    push_to_github()

if __name__ == "__main__":
    generate_m3u_playlist()
