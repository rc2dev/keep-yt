#!/usr/bin/env python3

import sys
import sqlite3
from keep_yt.config import load_config, ConfigError
from keep_yt.db.schema import init_db
from keep_yt.collect import refresh_collection
from keep_yt.report import write_report


def main() -> None:
    try:
        cfg = load_config()
    except ConfigError as e:
        print(e)
        sys.exit(1)

    db_path = cfg.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        init_db(conn)
        refresh_collection(conn, cfg.playlists_url, cfg.yt_dlp)

    # Read-only step. Run in a separate connection so that the previous transaction is committed first.
    with sqlite3.connect(db_path) as conn:
        write_report(conn, cfg.ignorelist_path, cfg.report_path)
