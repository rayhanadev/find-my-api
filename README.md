# Find My iPhone Location Server

A minimal FastAPI service that fetches your iPhone’s current GPS coordinates from iCloud’s Find My network and returns them (along with a reverse‑geocoded address) via a single JSON endpoint.

## Features

- Authenticates to your Apple ID (using an app‑specific password).
- Retrieves your iPhone’s latest latitude/longitude.
- Reverse‑geocodes those coordinates into a human‑readable address via Nominatim.
- Exposes one endpoint:
  - **GET /location** → Returns JSON with `latitude`, `longitude`, `city`, `state`, `country` and `timestamp`.

## Setup

Create a `.env` file in the project root (or set environment variables directly) with the following:

```
APPLE_ICLOUD_ID=
APPLE_ICLOUD_PASSWORD=
APPLE_DEVICE_NAME=
```

## Running Locally

1. **Install dependencies** (assuming you have Python 3.12+):

   ```bash
   uv venv
   source .venv/bin/activate
   uv install
   ```

   This installs everything listed in `pyproject.toml` into your virtual environment.

2. **Start the server**:

   ```bash
   uv run src/server.py
   ```

3. **Test the endpoint**:

   ```bash
   curl http://localhost:8000/location
   ```

   You’ll get back JSON, for example:

   ```json
   {
    "latitude": 40.42777585,
    "longitude": -86.91698799389519,
    "city": "West Lafayette",
    "state": "Indiana",
    "country": "US",
    "timestamp": 1748901582170
   }
   ```

## Running with Docker

1. **Build the image** (from the project root):

   ```bash
   docker build -t find-my-api .
   ```
2. **Run the container**, passing in your credentials:

   ```bash
   docker run -d \
     -e APPLE_ICLOUD_ID="example@icloud.com" \
     -e APPLE_ICLOUD_APP_SPECIFIC_PASSWORD="abcd-efgh-ijkl-mnop" \
     -e APPLE_DEVICE_NAME="iPhone 14 Pro" \
     -p 8000:8000 \
     find-my-api
   ```
3. **Verify and test**:

   ```bash
   docker logs -f <container_id>
   curl http://localhost:8000/location
   ```
