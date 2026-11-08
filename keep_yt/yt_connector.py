from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class YtConnectorError(Exception):
    def __init__(self, url: str, detail: str) -> None:
        super().__init__(f"Could not extract metadata from {url}\n{detail}")
        self.url = url


class YtLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def debug(self, message: str) -> None:
        self.messages.append(message)

    def warning(self, message: str) -> None:
        self.messages.append(message)

    def error(self, message: str) -> None:
        self.messages.append(message)


def fetch_entries(url: str, ytdl_options: dict) -> list[dict]:
    # Equivalent CLI: yt-dlp <options> --flat-playlist --dump-json <url>

    logger = YtLogger()
    options = {
        **ytdl_options,
        "logger": logger,
        "extract_flat": "in_playlist",
    }

    try:
        with YoutubeDL(options) as ytdl:
            info = ytdl.extract_info(url, download=False)
            if info is None:
                detail = "\n".join([*logger.messages, "No metadata returned"])
                raise YtConnectorError(url, detail)

            # Make all entry fields JSON-serializable (we use it in the metadata_json column).
            info = ytdl.sanitize_info(info)
            return info["entries"]
    except (DownloadError, OSError) as e:
        detail = "\n".join([*logger.messages, str(e)])
        raise YtConnectorError(url, detail) from e
