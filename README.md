# Find My iPhone Location Server

A minimal FastAPI service that fetches your iPhone’s current GPS coordinates from iCloud’s Find My network and returns them (along with a reverse‑geocoded address) via a single JSON endpoint.

## Features

- Authenticates to your Apple ID (using an app‑specific password).
- Retrieves your iPhone’s latest latitude/longitude.
- Reverse‑geocodes those coordinates into a human‑readable address via Nominatim.
- Exposes one endpoint:
  - **GET /location** → Returns JSON with `latitude`, `longitude`, `city`, `state`, `country` and `timestamp`.

## Setup

### Prerequisites

Make sure you have the following installed:
- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- Docker (optional, for containerized deployment)

### Clone the Repository

Clone the repository and install the dependencies:

```bash
git clone https://github.com/rayhanadev/find-my-api.git
cd find-my-api
```

```bash
uv venv
source .venv/bin/activate
uv install
```

### Environment Variables

Create a `.env` file in the project root (or set environment variables directly) with the following:

```
APPLE_ICLOUD_ID=
APPLE_ICLOUD_PASSWORD=
APPLE_DEVICE_NAME=
```

### iCloud Session Initialization

Run the following command to initialize your iCloud session and store the session data:

```bash
uv run scripts/init.py
```

## Running Locally

1. **Start the server**:

   ```bash
   uv run src/server.py
   ```

2. **Test the endpoint**:

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

To run the service as a Docker container, I have provided a `Dockerfile` and `docker-compose.yml`. You can
build the container or run `docker compose up -d` after setting the environment variables in a `.env` file
and initializing the iCloud session as described above.
