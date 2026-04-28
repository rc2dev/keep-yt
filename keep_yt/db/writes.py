import json
from datetime import UTC, datetime
import sqlite3


def now_iso():
    return datetime.now(UTC).isoformat(timespec="seconds")


def clear_refreshable_data(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM playlist_videos")
    conn.execute("DELETE FROM videos")
    conn.execute("DELETE FROM playlists")


def insert_playlist(conn: sqlite3.Connection, playlist: dict) -> None:
    # OR IGNORE avoids crash if for some reason yt-dlp repeats ids.
    conn.execute(
        """--sql
        INSERT OR IGNORE INTO playlists (playlist_id, url, title, raw_json, last_updated)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            playlist["id"],
            playlist["url"],
            playlist["title"],
            json.dumps(playlist),
            now_iso(),
        ),
    )


def insert_playlist_video(
    conn: sqlite3.Connection, playlist_id: str, video_id: str
) -> None:
    conn.execute(
        """--sql
        INSERT OR IGNORE INTO playlist_videos (playlist_id, video_id)
        VALUES (?, ?)
        """,
        (playlist_id, video_id),
    )


def insert_video_snapshot(conn: sqlite3.Connection, video: dict) -> None:
    video_id = video.get("id")
    if not video_id:
        return

    conn.execute(
        """--sql
        INSERT OR IGNORE INTO videos_snapshot (
            video_id,
            url,
            title,
            uploader,
            uploader_url,
            duration,
            raw_json,
            last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            video_id,
            video.get("url"),
            video.get("title"),
            video.get("uploader"),
            video.get("uploader_url"),
            video.get("duration"),
            json.dumps(video),
            now_iso(),
        ),
    )


def insert_video(
    conn: sqlite3.Connection, video: dict, seems_unavailable: bool
) -> None:
    video_id = video.get("id")
    if not video_id:
        return

    conn.execute(
        """--sql
        INSERT OR IGNORE INTO videos (
            video_id, url, title, uploader, uploader_url, duration, raw_json, last_updated, seems_unavailable )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            video_id,
            video.get("url"),
            video.get("title"),
            video.get("uploader"),
            video.get("uploader_url"),
            video.get("duration"),
            json.dumps(video),
            now_iso(),
            int(seems_unavailable),
        ),
    )
