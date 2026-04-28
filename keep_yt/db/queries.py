import sqlite3


def find_unavailable_videos(conn: sqlite3.Connection):
    """
    Lists unavailable videos with their initial data and the playlists they belong to.
    """
    cur = conn.execute("""---sql
        SELECT
            v.video_id,
            v.url,
            s.title,
            s.uploader,
            s.uploader_url,
            GROUP_CONCAT(p.title, ' | ') AS playlists
        FROM videos v
        JOIN videos_snapshot s ON s.video_id = v.video_id
        JOIN playlist_videos pv ON pv.video_id = v.video_id
        JOIN playlists p ON p.playlist_id = pv.playlist_id
        WHERE v.seems_unavailable = 1
        GROUP BY v.video_id
        ORDER BY s.title
        """)
    return cur.fetchall()
