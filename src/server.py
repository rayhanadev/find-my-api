import os
import sys
import logging
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyicloud import PyiCloudService
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderServiceError
import uvicorn
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger("uvicorn.error")


class LocationResponse(BaseModel):
    latitude: float
    longitude: float
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    timestamp: Optional[int]


@asynccontextmanager
async def lifespan(app: FastAPI):
    APPLE_ICLOUD_ID = os.environ.get("APPLE_ICLOUD_ID")
    APPLE_ICLOUD_PASSWORD = os.environ.get("APPLE_ICLOUD_PASSWORD")
    APPLE_DEVICE_NAME = os.environ.get("APPLE_DEVICE_NAME")

    if not APPLE_ICLOUD_ID or not APPLE_ICLOUD_PASSWORD:
        logger.error(
            "Environment variables APPLE_ICLOUD_ID and APPLE_ICLOUD_PASSWORD must be set"
        )
        sys.exit(1)

    if not APPLE_DEVICE_NAME:
        logger.error("Environment variable APPLE_DEVICE_NAME must be set")
        sys.exit(1)

    logger.info("Authenticating to iCloud…")

    cookie_directory = os.path.join(os.getcwd(), ".icloud/")
    if not os.path.exists(cookie_directory):
        os.makedirs(cookie_directory)

    try:
        api = PyiCloudService(
            APPLE_ICLOUD_ID,
            APPLE_ICLOUD_PASSWORD,
            cookie_directory=cookie_directory,
        )

        if api.requires_2fa:
            print("Two-factor authentication required. Did you run scripts/init.py?")
            sys.exit(1)
        elif api.requires_2sa:
            print("Two-step authentication required. Did you run scripts/init.py?")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to authenticate to iCloud: {e}")
        sys.exit(1)

    geolocator = Nominatim(user_agent="rayhanadev_iphone_tracker")

    app.state.cache = {"data": None, "fetched_at": None}

    app.state.api = api
    app.state.geolocator = geolocator
    app.state.apple_device_name = APPLE_DEVICE_NAME

    yield


app = FastAPI(title="Find My iPhone Location API", lifespan=lifespan)


@app.get("/location", response_model=LocationResponse)
def get_device_location():
    cache = app.state.cache
    now = datetime.utcnow()

    if cache["data"] is not None and cache["fetched_at"] is not None:
        age = now - cache["fetched_at"]
        if age < timedelta(hours=1):
            logger.info("Returning cached location data (age: %s)", str(age))
            return cache["data"]

    api: PyiCloudService = app.state.api
    geolocator: Nominatim = app.state.geolocator

    iphone = None
    for device in api.devices:
        if device.get("name") == app.state.apple_device_name:
            iphone = device
            break

    if iphone is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{app.state.apple_device_name}' not found in iCloud account.",
        )

    try:
        loc = iphone.location()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch location from iCloud: {e}",
        )

    if not loc:
        raise HTTPException(
            status_code=404,
            detail="No location data available (device might be offline).",
        )

    latitude = loc.get("latitude")
    longitude = loc.get("longitude")

    if latitude is None or longitude is None:
        raise HTTPException(
            status_code=502, detail="Location payload missing latitude/longitude."
        )

    try:
        address_obj = geolocator.reverse((latitude, longitude), timeout=None)
        address = address_obj.raw.get("address", {})

        if not address:
            raise HTTPException(
                status_code=502, detail="Could not reverse geocode the location."
            )

        city = address.get("town")
        state = address.get("state")
        country = address.get("country_code").upper()
    except (GeocoderUnavailable, GeocoderServiceError) as e:
        logger.error(f"Geocoding error: {e}")
        city = state = country = None

    response = LocationResponse(
        latitude=latitude,
        longitude=longitude,
        city=city,
        state=state,
        country=country,
        timestamp=loc.get("timeStamp"),
    )

    cache["data"] = response
    cache["fetched_at"] = now
    logger.info("Fetched new location data and updated cache.")

    return response


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
