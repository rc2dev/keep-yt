from pathlib import Path
import sqlite3
from datetime import datetime, UTC
from keep_yt.db.queries import find_unavailable_videos, db_is_initialized


def print_report(conn: sqlite3.Connection, ignorelist_path: Path) -> None:
    if not db_is_initialized(conn):
        print("Database is not initialized. Run 'collect' command first.")
        return

    rows = find_unavailable_videos(conn)
    rows = exclude_ignored_videos(rows, ignorelist_path)

    lines: list[str] = []

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    lines.append(f"Report generated at: {now}")
    lines.append("")

    if not rows:
        lines.append(
            "No unavailable videos in your playlists (excluding ignored entries)."
        )
        lines.append("")
    else:
        count = len(rows)
        video_word = "video" if count == 1 else "videos"

        lines.append(f"{count} unavailable {video_word} in your playlists:")
        lines.append("-" * 72)
        lines.append("")

        for idx, row in enumerate(rows, start=1):
            video_id, url, title, uploader, uploader_url, playlists = row
            lines.append(f"{idx}. {title or '(no title)'}")
            lines.append(
                f"   Video: {url or f'https://www.youtube.com/watch?v={video_id}'}"
            )
            lines.append(f"   Uploader: {uploader or '(unknown)'}")
            lines.append(f"   Uploader URL: {uploader_url or '(unknown)'}")
            lines.append(f"   Playlists: {playlists or '(none)'}")
            lines.append("")

        ids = {video_id for video_id, *_ in rows if video_id}
        lines.append("-" * 72)
        lines.append("List of video IDs:")
        lines.append(
            "Add them to your ignore list to exclude them from future reports."
        )
        lines.append("")
        for video_id in ids:
            lines.append(video_id)

    print("\n".join(lines) + "\n")


def exclude_ignored_videos(rows: list, ignorelist_path: Path) -> list:
    ignored_ids = load_ignored_ids(ignorelist_path)

    filtered_rows = [row for row in rows if (video_id := row[0]) not in ignored_ids]

    return filtered_rows


def load_ignored_ids(ignorelist_path: Path) -> set:
    if not ignorelist_path.exists():
        return set()

    with open(ignorelist_path, encoding="utf-8") as f:
        ignored_ids = {
            line.strip() for line in f if line.strip() and not line.startswith("#")
        }
        return ignored_ids
