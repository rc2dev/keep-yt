#!/usr/bin/env python3

import sys
import argparse
import sqlite3
from keep_yt.config import load_config, ConfigError
from keep_yt.db.schema import init_db
from keep_yt.collect import refresh_collection
from keep_yt.report import print_report


def ensure_db_dir(cfg) -> None:
    cfg.db_path.parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="keep-yt: Keep track of videos on your YouTube playlists"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("collect", help="Collect videos from playlists")
    subparsers.add_parser("report", help="Generate report")
    return parser.parse_args()


def main() -> None:
    try:
        cfg = load_config()
    except ConfigError as e:
        print(e)
        sys.exit(1)

    args = parse_args()

    ensure_db_dir(cfg)

    with sqlite3.connect(cfg.db_path) as conn:
        init_db(conn)

        match args.command:
            case "collect":
                refresh_collection(conn, cfg.playlists_url, cfg.yt_dlp)
            case "report":
                print_report(conn, cfg.ignorelist_path)
            case _:
                print(f"Unknown command: {args.command}")
                sys.exit(1)
