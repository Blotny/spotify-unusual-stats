# Unusual Spotify Stats

A Streamlit app that turns your Spotify "Extended Streaming History" export into
statistics you won't find in Spotify Wrapped - adjustable skip detection,
per-track/artist skip rates, a world map of where you listened from,
and an early preview of your yearly Wrapped including previous years.

## Features

### Upload & processing
- Upload your Spotify data export (`.zip`) directly in the browser
- ETL pipeline: parses the export, strips personal fields (IP address, username),
  filters out podcasts/audiobooks, and loads clean events into a database
- Deduplication via file hash - re-uploading the same export won't create duplicate data
- Local dev works out of the box with SQLite; production uses a free Neon (Postgres) database

### Most Skipped page
- Most skipped tracks and artists, with adjustable minimum play count to filter out noise
- Adjustable skip threshold (in seconds) - skip detection is computed dynamically, not
  baked into the database, so you can tune what counts as a "skip" on the fly
- Sort by skip count, skip rate, or a combined "dislike score" (`skips³ / plays²`) that
  balances frequency against sample size
- Year filter (multi-select pills, with a "select all" shortcut)

### Country Map page
- Header metrics: total countries visited, detected home country
- Choropleth world map showing % of listening time per country
- Click a country to drill down into its top artists and top songs, shown in a
  side panel next to the map
- Bar chart of listening % by country, with automatic home-country detection
  and a toggle to hide it (so smaller countries are easier to compare)


### Early Spotify Wrapped page
- Your top artists, tracks and new discoveries for any year in your history
- Listening patterns by month, day of week and hour of day
- Year-over-year listening history

## Why some design decisions look the way they do

- **Skip detection isn't a single boolean.** Spotify's own `skipped` field is
  inconsistently recorded (notably broken for several years in the past), so this
  app keeps the raw signals (`ms_played`, `reason_end`, `skipped`) and computes
  skip status dynamically per query, controlled by a threshold the user can adjust.
- **No audio features (energy, valence, danceability, etc.).** Spotify restricted
  API access to these in late 2024, and using them to train ML models is against
  Spotify's developer terms — so this project is built entirely from the
  streaming history export plus catalog metadata.
- **Personal data isn't retained.** IP addresses and usernames are dropped during
  the ETL step and never stored.

## Tech stack

- **Frontend:** [Streamlit](https://streamlit.io)
- **Database:** PostgreSQL via [Neon](https://neon.tech) (free tier) / SQLite for local dev
- **ORM:** SQLAlchemy
- **Data processing:** pandas
- **Visualization:** Plotly
- **Country code conversion:** pycountry

## Project structure

```
Not finished yet...
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

No additional configuration needed — without a `.env` file, the app automatically uses a local SQLite database.

### Setting up Neon (optional, for persistent/shared storage)

1. Create a free project at [neon.tech](https://neon.tech) (no card required)
2. Copy the connection string from the dashboard
3. Create a `.env` file in the project root and add:
DATABASE_URL=your_neon_connection_string_here

Keep `?sslmode=require` at the end of the connection string.

## Getting your Spotify data

1. Go to your [Spotify account privacy settings](https://www.spotify.com/account/privacy/)
2. Under "Download your data", select **only** "Extended streaming history"
   (not "Account data" - that only covers the last year)
3. Confirm via the email Spotify sends you
4. Wait for the second email with the download link (usually a few days,
   officially up to 30)

## Running the app

```bash
streamlit run app.py
```

Upload the `.zip` file from your Spotify export on the main page, then use the
sidebar to navigate to the stats pages.


## Known limitations

- `conn_country` is derived from IP address at playback time, not GPS - VPNs,
  ISP routing quirks, or remote Spotify Connect sessions can produce occasional
  "phantom" countries with very low play counts.
- No genre, mood, or audio-feature data - these are no longer available
  through Spotify's public API for new integrations.
