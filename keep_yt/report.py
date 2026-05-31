from pathlib import Path
import sqlite3
from datetime import datetime
from keep_yt.db.queries import find_unavailable_videos, db_is_initialized


def print_report(conn: sqlite3.Connection, ignorelist_path: Path) -> None:
    if not db_is_initialized(conn):
        print("Database is not initialized. Run 'collect' command first.")
        return

    rows = find_unavailable_videos(conn)
    filtered_rows = exclude_ignored_videos(rows, ignorelist_path)

    report_lines = format_report(filtered_rows)
    print("\n".join(report_lines))


def format_report(rows: list) -> list[str]:
    SEPARATOR = "-" * 72
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    report = [f"Report generated at: {now}", ""]

    if not rows:
        report.append(
            "No unavailable videos in your playlists (excluding ignored entries)."
        )
        return report

    count = len(rows)
    video_word = "video" if count == 1 else "videos"

    report.append(f"{count} unavailable {video_word} in your playlists:")
    report.append(SEPARATOR)
    report.append("")

    for idx, row in enumerate(rows, start=1):
        video_id, url, title, uploader, uploader_url, playlists = row
        report.append(f"{idx}. {title or '(no title)'}")
        report.append(
            f"   Video: {url or f'https://www.youtube.com/watch?v={video_id}'}"
        )
        report.append(f"   Uploader: {uploader or '(unknown)'}")
        report.append(f"   Uploader URL: {uploader_url or '(unknown)'}")
        report.append(f"   Playlists: {playlists or '(none)'}")
        report.append("")

    ids = {video_id for video_id, *_ in rows if video_id}
    report.append(SEPARATOR)
    report.append("List of video IDs:")
    report.append("Add them to your ignore list to exclude them from future reports.")
    report.append("")
    for video_id in ids:
        report.append(video_id)

    return report


def exclude_ignored_videos(rows: list, ignorelist_path: Path) -> list:
    ignored_ids = load_ignored_ids(ignorelist_path)

    filtered_rows = [row for row in rows if (video_id := row[0]) not in ignored_ids]

    return filtered_rows


def load_ignored_ids(ignorelist_path: Path) -> set[str]:
    if not ignorelist_path.exists():
        return set()

    ignored_ids: set[str] = set()
    with ignorelist_path.open(encoding="utf-8") as f:
        for line in f:
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("#"):
                continue
            ignored_ids.add(cleaned)

    return ignored_ids
