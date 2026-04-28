import sqlite3
from keep_yt.db.writes import (
    clear_refreshable_data,
    insert_playlist,
    insert_playlist_video,
    insert_video_snapshot,
    insert_video,
)
from keep_yt.yt import fetch_playlists, fetch_playlist_videos


def refresh_collection(
    conn: sqlite3.Connection, playlists_url: str, yt_dlp: list[str]
) -> None:
    clear_refreshable_data(conn)

    playlists = fetch_playlists(yt_dlp, playlists_url)
    for playlist in playlists:
        videos = fetch_playlist_videos(playlist["url"], yt_dlp)
        _save_playlist(conn, playlist, videos)


def _save_playlist(
    conn: sqlite3.Connection,
    playlist: dict,
    videos: list[dict],
) -> None:
    insert_playlist(conn, playlist)

    for video in videos:
        if not video.get("id"):
            continue

        # Since 'video_snapshot' is never wiped and we use INSERT OR IGNORE,
        # this will only insert data the first time the video is seen.
        insert_video_snapshot(conn, video)

        insert_video(conn, video, _video_seems_unavailable(video))

        insert_playlist_video(conn, playlist["id"], video["id"])


def _video_seems_unavailable(video: dict) -> bool:
    return video.get("title") in ("[Deleted video]", "[Private video]")
