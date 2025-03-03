import requests
from datetime import datetime

# Base URLs
STREAMS_API = "https://ppv.land/api/streams"
STREAM_DETAILS_API = "https://ppv.land/api/streams/{}"
OUTPUT_FILE = "ppvland_playlist.m3u"

def fetch_streams():
    """Fetch the list of available streams."""
    response = requests.get(STREAMS_API)
    if response.status_code != 200:
        print("Failed to fetch streams.")
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
                "start_time": stream["starts_at"],
                "end_time": stream["ends_at"]
            })
    
    return streams

def fetch_m3u8_link(stream_id):
    """Fetch the M3U8 link for a given stream ID."""
    response = requests.get(STREAM_DETAILS_API.format(stream_id))
    if response.status_code != 200:
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
    m3u_content = "#EXTM3U\n"

    for stream in streams:
        m3u8_url = fetch_m3u8_link(stream["id"])
        if not m3u8_url:
            continue

        start_time = format_timestamp(stream["start_time"])
        end_time = format_timestamp(stream["end_time"])

        m3u_content += f'#EXTINF:-1 tvg-id="{stream["id"]}" tvg-name="{stream["name"]}" tvg-logo="{stream["poster"]}" tvg-start="{start_time}" tvg-end="{end_time}",{stream["name"]}\n'
        m3u_content += f"{m3u8_url}\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"M3U Playlist generated: {OUTPUT_FILE}")

def main():
    print("Fetching latest streams...")
    streams = fetch_streams()

    if not streams:
        print("No streams available.")
        return

    print("Generating M3U playlist with start/end times...")
    generate_m3u_playlist(streams)
    print("Done! You can now use the playlist in Kodi, VLC, or any IPTV player.")

if __name__ == "__main__":
    main()