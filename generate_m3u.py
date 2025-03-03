def generate_m3u_playlist(streams):
    """Generate an M3U playlist from the stream data."""
    if not streams:
        print("No streams available to generate M3U file!")
        return

    m3u_content = "#EXTM3U\n"

    for stream in streams:
        m3u8_url = fetch_m3u8_link(stream["id"])
        if not m3u8_url:
            print(f"Skipping {stream['name']} (No M3U8 link found)")
            continue

        start_time = format_timestamp(stream["start_time"])
        end_time = format_timestamp(stream["end_time"])

        m3u_content += f'#EXTINF:-1 tvg-id="{stream["id"]}" tvg-name="{stream["name"]}" tvg-logo="{stream["poster"]}" tvg-start="{start_time}" tvg-end="{end_time}",{stream["name"]}\n'
        m3u_content += f"{m3u8_url}\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✅ M3U Playlist generated successfully: {OUTPUT_FILE}")
