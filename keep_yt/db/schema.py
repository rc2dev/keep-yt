import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    # Prevent invalid references (SQLite does not enforce FK constraints unless enabled)
    conn.execute("PRAGMA foreign_keys = ON")

    version = conn.execute("PRAGMA user_version").fetchone()[0]

    if version == 0:
        conn.executescript(
            """--sql
            CREATE TABLE IF NOT EXISTS playlists (
                playlist_id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                raw_json TEXT,
                last_updated TEXT
            );

            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                uploader TEXT,
                uploader_url TEXT,
                duration INTEGER,
                raw_json TEXT,
                last_updated TEXT,
                seems_unavailable INTEGER DEFAULT 0 CHECK (seems_unavailable IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS videos_snapshot (
                video_id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                uploader TEXT,
                uploader_url TEXT,
                duration INTEGER,
                raw_json TEXT,
                last_updated TEXT
            );

            CREATE TABLE IF NOT EXISTS playlist_videos (
                playlist_id TEXT NOT NULL
                    REFERENCES playlists (playlist_id) ON DELETE CASCADE,
                video_id TEXT NOT NULL
                    REFERENCES videos (video_id) ON DELETE CASCADE,
                PRIMARY KEY (playlist_id, video_id)
            );


            -- videos_snapshot protections
            CREATE TRIGGER IF NOT EXISTS prevent_update_videos_snapshot
            BEFORE UPDATE ON videos_snapshot
            BEGIN
                SELECT RAISE(FAIL, 'videos_snapshot is read-only');
            END;

            CREATE TRIGGER prevent_delete_videos_snapshot
            BEFORE DELETE ON videos_snapshot
            BEGIN
                SELECT RAISE(FAIL, 'cannot delete from videos_snapshot');
            END;
            """
        )

        conn.execute("PRAGMA user_version = 1")
        version = 1

    conn.commit()
