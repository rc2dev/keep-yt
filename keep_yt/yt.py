import subprocess
import json


def _run_yt_dlp(yt_dlp: list[str], args: list[str]) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            yt_dlp + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr)
        raise


def fetch_playlists(yt_dlp: list[str], playlists_url: str) -> list[dict]:
    result = _run_yt_dlp(yt_dlp, ["--flat-playlist", "--dump-json", playlists_url])
    lines = result.stdout.splitlines()
    playlists = [json.loads(line) for line in lines]
    return playlists


def fetch_playlist_videos(playlist_url: str, yt_dlp: list[str]) -> list[dict]:
    result = _run_yt_dlp(yt_dlp, ["--flat-playlist", "--dump-json", playlist_url])
    lines = result.stdout.splitlines()
    videos = [json.loads(line) for line in lines]
    return videos
