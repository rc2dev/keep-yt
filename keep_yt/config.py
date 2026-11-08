from dataclasses import dataclass
from pathlib import Path
import json

APP_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = APP_ROOT / "config" / "config.json"


class ConfigError(Exception):
    pass


@dataclass
class Config:
    db_path: Path
    ignorelist_path: Path
    playlists_url: str
    ytdl_options: dict


def load_config() -> Config:
    return _parse_config(_read_config())


def _read_config() -> dict:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {CONFIG_PATH}.")
    # This includes "FileNotFoundError", but we'll treat it separately as it is common.
    except OSError as e:
        raise ConfigError(f"OS/Filesystem error reading config: {e}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Couldn't parse JSON on config: {e}")
    except UnicodeDecodeError as e:
        raise ConfigError(f"Config file must be UTF-8: {e}")


def _parse_config(cfg: dict) -> Config:
    # Replace placeholders
    try:
        cfg_fmt = _format_placeholders(cfg)
    except (KeyError, ValueError, IndexError) as e:
        raise ConfigError(f"Invalid placeholder in config file: {e}")

    # Cast to correct types
    try:
        if not isinstance(cfg_fmt["ytdl_options"], dict):
            raise TypeError("ytdl_options must be an object")
        cfg_casted = {
            "db_path": Path(cfg_fmt["db_path"]),
            "ignorelist_path": Path(cfg_fmt["ignorelist_path"]),
            "playlists_url": cfg_fmt["playlists_url"],
            "ytdl_options": cfg_fmt["ytdl_options"],
        }
    except KeyError as e:
        raise ConfigError(f"Missing key in config file: {e}")
    except (TypeError, AttributeError, ValueError) as e:
        raise ConfigError(f"Invalid data in config file: {e}")

    return Config(**cfg_casted)


def _format_placeholders(value):
    if isinstance(value, str):
        return value.format(APP_ROOT=APP_ROOT)
    if isinstance(value, dict):
        return {key: _format_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_format_placeholders(item) for item in value]
    return value
