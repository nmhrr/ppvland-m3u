import requests
import os
from datetime import datetime

STREAMS_API = "https://ppv.land/api/streams"
STREAM_DETAILS_API = "https://ppv.land/api/streams/{}"
OUTPUT_FILE = "ppvland_playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://ppv.land/",
    "Origin": "https://ppv.land"
}

def fetch_streams():
    print("📡 Fetching streams from PPV.LAND...")
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
                "poster": stream["poster"],
                "category": category["category"],
                "start_time": stream.get("starts_at", 0),
                "end_time": stream.get("ends_at", 0)
            })

    print(f"✅ Found {len(streams)} streams.")
    return streams

def fetch_m3u8_link(stream_id):
    """Fetch the M3U8 link for a given stream ID."""
    print(f"🔍 Fetching M3U8 link for stream ID: {stream_id}")
    response = requests.get(STREAM_DETAILS_API.format(stream_id), headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch details for stream {stream_id}. HTTP {response.status_code}")
        return None

    data = response.json()
    return data["data"].get("m3u8")

def format_timestamp(timestamp):
    """Convert UNIX timestamp to ISO 8601 format for M3U playlists."""
    if timestamp:
        return datetime.utcfromtimestamp(timestamp).strftime("%Y%m%dT%H%M%SZ")
    return ""

def generate_m3u_playlist(streams):
    """Generate an M3U playlist from the stream data."""
    if not streams:
        print("❌ No streams available to generate M3U file!")
        return False

    print("📝 Generating M3U playlist...")
    m3u_content = "#EXTM3U\n"
    total_added = 0

    for stream in streams:
        m3u8_url = fetch_m3u8_link(stream["id"])
        if not m3u8_url:
            continue

        start_time = format_timestamp(stream["start_time"])
        end_time = format_timestamp(stream["end_time"])

        m3u_content += f'#EXTINF:-1 tvg-id="{stream["id"]}" tvg-name="{stream["name"]}" tvg-logo="{stream["poster"]}" tvg-start="{start_time}" tvg-end="{end_time}",{stream["name"]}\n'
        m3u_content += f"{m3u8_url}\n"
        total_added += 1

    if total_added == 0:
        print("❌ No valid streams with M3U8 links were found. Exiting.")
        return False

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✅ M3U Playlist generated successfully with {total_added} streams: {OUTPUT_FILE}")
    return True

def main():
    print("🔄 Starting M3U auto-update process...")
    streams = fetch_streams()

    if not streams:
        print("❌ No streams available. Exiting...")
        return

    generate_m3u_playlist(streams)
    print("🎉 Done! Your playlist is updated.")

if __name__ == "__main__":
    main()
