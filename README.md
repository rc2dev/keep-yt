# keep-yt

Never lose track of videos in your YouTube playlists. Save their metadata and automatically detect when they go missing.

## Motivation

If a video becomes unavailable on YouTube, its data, such as title and duration, is often lost.

You've probably run into this before: you saved videos to a playlists, only to come back later and find that some are deleted or set to private, with no clue what they used to be.

This application aims to tackle this, storing video data and telling the user which videos went missing.

## Installation

- Clone the repository.

- Write your config copying `config.sample.json` to `config.json`.

## Usage

Run the `collect` command periodically.

It saves metadata for all videos in your playlists.

Over time, the application will detect videos that have become unavailable. Generate a report with the `report` command. Obviously, this becomes more useful after a few runs.

If you notice any missing one that weren't detected, simply browse the database, as all the metadata has been preserved since the first run.

### Ignoring videos

You may want to exclude some videos from the report.

Just add their IDs, one per line, to the `ignore_ids` file. Lines starting with "#" are ignored.

## License

Copyright (C) 2026 [Rafael Cavalcanti](https://rafaelc.org/dev)
