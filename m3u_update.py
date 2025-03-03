import os
import requests
import datetime
from pytz import timezone

# ✅ Proxy setup (Optional: Replace with your actual proxy if needed)
PROXY = {
    "http": "http://172.67.181.166:80",
    "https": "http://172.67.181.166:80"
}

# ✅ API Endpoint
API_URL = "https://ppv.land/api/streams"

# ✅ Output M3U file location
OUTPUT_FILE = "ppvland_playlist.m3u"

# ✅ Set Time Zone to Eastern Time (ET)
ET_TZ = timezone("America/New_York")
CURRENT_TIME = datetime.datetime.now(ET_TZ)

def fetch_streams():
    """Fetch live streams from PPV.LAND API using a proxy."""
    try:
        print("📡 Fetching live streams from PPV.LAND...")
        response = requests.get(API_URL, proxies=PROXY, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch streams: {e}")
        return None

def format_time(timestamp):
    """Convert UNIX timestamp to 12-hour format ET time."""
    dt = datetime.datetime.fromtimestamp(timestamp, ET_TZ)
    return dt.strftime("%I:%M %p %m/%d/%y")  # Example: 07:30 PM 03/02/25

def generate_m3u(stream_data):
    """Generate an M3U playlist from stream data."""
    if not stream_data or "streams" not in stream_data:
        print("❌ No streams available. Exiting...")
        return

    print("🎥 Generating M3U playlist...")
    m3u_content = "#EXTM3U\n"

    all_streams = []

    for category in stream_data["streams"]:
        for stream in category["streams"]:
            start_time = stream.get("starts_at")
            end_time = stream.get("ends_at")
            stream_id = stream.get("id")
            stream_name = stream.get("name")
            tag = stream.get("tag")
            category_name = category["category"]
            poster = stream.get("poster", "")
            url = f"https://ppv.land/api/streams/{stream_id}"  # Get M3U8 URL from ID

            # ✅ Determine if it's a 24/7 stream
            if start_time and end_time:
                start_dt = datetime.datetime.fromtimestamp(start_time, ET_TZ)
                if start_dt < CURRENT_TIME:
                    formatted_time = "24/7"
                else:
                    formatted_time = format_time(start_time)
            else:
                formatted_time = "24/7"

            # ✅ Format the title correctly
            title = f"({category_name}) {stream_name} - {tag} - {formatted_time}"
            
            all_streams.append((start_time, f"#EXTINF:-1 tvg-logo=\"{poster}\",{title}\n{url}\n"))

    # ✅ Sort streams by start time (earliest first)
    all_streams.sort(key=lambda x: x[0] if x[0] else float("inf"))

    # ✅ Add sorted streams to M3U content
    for _, stream_entry in all_streams:
        m3u_content += stream_entry

    # ✅ Save M3U file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"✅ M3U playlist saved to {OUTPUT_FILE}")

def main():
    """Main function to fetch data and generate the M3U file."""
    streams = fetch_streams()
    generate_m3u(streams)

if __name__ == "__main__":
    main()
