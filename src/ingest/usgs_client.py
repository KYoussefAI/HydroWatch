import requests
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
import json


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

BASE_URL = "https://api.waterdata.usgs.gov/ogcapi/v1/"

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504
}


def fetch_url(endpoint_or_url, params=None):
    url = endpoint_or_url if endpoint_or_url.startswith("https://") else BASE_URL + endpoint

    max_retries = 3
    for attempt in range(1, max_retries + 1):

        try:
            logger.info(
                f"Requesting {endpoint_or_url} - attempt {attempt}"
            )

            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code in RETRYABLE_STATUS_CODES:

                if attempt < max_retries:

                    wait_seconds = 2 ** (attempt - 1)

                    logger.warning(
                        f"HTTP {response.status_code} - "
                        f"retrying in {wait_seconds}s"
                    )

                    time.sleep(wait_seconds)
                    continue

            response.raise_for_status()

            logger.info(
                f"Request succeeded - HTTP {response.status_code}"
            )

            return response.json()

        except (requests.Timeout, requests.ConnectionError) as error:

            if attempt == max_retries:
                logger.error(
                    f"Request failed after {max_retries} attempts: {error}"
                )
                raise

            wait_seconds = 2 ** (attempt - 1)

            logger.warning(
                f"Network error: {error} - "
                f"retrying in {wait_seconds}s"
            )

            time.sleep(wait_seconds)


def save_raw_json(data,batch_id):

    raw_dir = Path("data/raw/observations")
    raw_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    file_path = raw_dir / f"observations_{timestamp}_{batch_id}.json"

    with file_path.open("w",encoding="utf-8") as file :
        json.dump(data,file,indent=2)

    logger.info(
        f"Raw response saved to {file_path}"
    )


# batch_id = str(uuid.uuid4())
# params = {
#     "monitoring_location_id": "USGS-06115200",
#     "parameter_code": "00060",
#     "limit": 1
# }

# data = fetch_url(
#     "collections/continuous/items",
#     params
# )
# extracted_at = datetime.now(timezone.utc)

# save_raw_json(data)