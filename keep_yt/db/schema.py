import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    # Prevent invalid references (SQLite does not enforce FK constraints unless enabled)
    conn.execute("PRAGMA foreign_keys = ON")

    version = conn.execute("PRAGMA user_version").fetchone()[0]

    match version:
        case 0:
            create_schema_v3(conn)
        case 1:
            migrate_v1_to_v2(conn)
            migrate_v2_to_v3(conn)
        case 2:
            migrate_v2_to_v3(conn)
        case 3:
            pass
        case _:
            raise RuntimeError(f"Unsupported database version: {version}")

    conn.commit()


def create_schema_v3(conn: sqlite3.Connection) -> None:
    conn.executescript("""--sql
        CREATE TABLE IF NOT EXISTS playlists (
            playlist_id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            metadata_json TEXT
        );

        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            uploader TEXT,
            uploader_url TEXT,
            duration INTEGER,
            metadata_json TEXT,
            seems_unavailable INTEGER DEFAULT 0 CHECK (seems_unavailable IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS videos_snapshot (
            video_id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            uploader TEXT,
            uploader_url TEXT,
            duration INTEGER,
            metadata_json TEXT,
            inserted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS playlist_videos (
            playlist_id TEXT NOT NULL
                REFERENCES playlists (playlist_id) ON DELETE CASCADE,
            video_id TEXT NOT NULL
                REFERENCES videos (video_id) ON DELETE CASCADE,
            PRIMARY KEY (playlist_id, video_id)
        );

        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );


        -- videos_snapshot protections
        CREATE TRIGGER IF NOT EXISTS prevent_update_videos_snapshot
        BEFORE UPDATE ON videos_snapshot
        BEGIN
            SELECT RAISE(FAIL, 'videos_snapshot is read-only');
        END;

        CREATE TRIGGER IF NOT EXISTS prevent_delete_videos_snapshot
        BEFORE DELETE ON videos_snapshot
        BEGIN
            SELECT RAISE(FAIL, 'cannot delete from videos_snapshot');
        END;
        """)
    conn.execute("PRAGMA user_version = 3")


def migrate_v1_to_v2(conn: sqlite3.Connection) -> None:
    # SQLite 3.35+ supports DROP COLUMN; use that to keep this migration simple.
    conn.execute("ALTER TABLE playlists DROP COLUMN last_updated")
    conn.execute("ALTER TABLE videos DROP COLUMN last_updated")
    conn.execute(
        "ALTER TABLE videos_snapshot RENAME COLUMN last_updated TO inserted_at"
    )
    conn.execute("""CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
    conn.execute("PRAGMA user_version = 2")


def migrate_v2_to_v3(conn: sqlite3.Connection) -> None:
    conn.execute("SAVEPOINT migrate_v2_to_v3")
    try:
        for table in ("playlists", "videos", "videos_snapshot"):
            conn.execute(f"ALTER TABLE {table} RENAME COLUMN raw_json TO metadata_json")
        conn.execute("PRAGMA user_version = 3")
    except Exception:
        conn.execute("ROLLBACK TO migrate_v2_to_v3")
        conn.execute("RELEASE migrate_v2_to_v3")
        raise
    conn.execute("RELEASE migrate_v2_to_v3")
