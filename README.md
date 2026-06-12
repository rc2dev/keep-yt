# keep-yt

Find out which videos are gone from your YouTube playlists.

## Motivation

You've probably experienced this before: you save videos to a YouTube playlist, and sometime later one or more of them become unavailable (deleted or made private).

You can see that a video is missing, but not which one it was. YouTube hides the video metadata (title, channel, etc) for those videos.

This tool solves that problem by periodically collecting metadata from your playlists. Whenever a video disappears, you'll know which one it was.

## Scope

This tool is designed to preserve metadata from YouTube videos. It does not back up playlist contents or videos themselves.

## Installation

- Make sure you have Python installed.

- Clone the repository.

- Write your config copying `config.sample.json` to `config.json`.

## Usage

### The collect command

The `collect` command saves metadata for all videos in your playlists.

It should be run periodically. I recommend scheduling it, for example using cron.

### The report command

The `report` command generates a report of all the missing videos with their metadata.

It uses the metadata collected over time. So, obviously, it becomes more useful after you run the `collect` for a while.

If you notice that a missing video wasn't detected by the report, you can inspect the database directly. Metadata is preserved from the first time a video is collected.

### Ignoring videos

You may want to exclude some videos from the report.

Add their IDs one per line to the `ignore_ids` file. Lines starting with "#" are treated as comments.

## License

Copyright (C) 2026 [Rafael Cavalcanti](https://rafaelc.org/dev)
