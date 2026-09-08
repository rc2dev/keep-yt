import json
import shlex
import subprocess


class YtConnectorError(Exception):
    def __init__(self, command: list[str], stderr: str | None) -> None:
        detail = stderr.strip() if stderr else "no details"
        message = f"Command failed: {shlex.join(command)}\n{detail}"
        super().__init__(message)
        self.command = command
        self.stderr = stderr


def _run_yt_dlp(yt_dlp: list[str], args: list[str]) -> subprocess.CompletedProcess:
    command = yt_dlp + args
    try:
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise YtConnectorError(command, e.stderr) from e


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
