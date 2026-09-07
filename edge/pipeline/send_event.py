"""Edge Pipeline Event Sender Client.

Provides functionality to transmit generated event payloads to the FastAPI backend
endpoint POST /events over HTTP.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any


class EventSubmissionError(Exception):
    """Custom exception raised when event transmission to backend fails."""
    def __init__(self, message: str, status_code: int = 500, detail: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


def send_event(
    event_data: Dict[str, Any],
    api_url: str = "http://127.0.0.1:8000/events",
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    Sends an event JSON payload to the backend POST /events endpoint.

    :param event_data: Standardized EventCreate dictionary payload
    :param api_url: Target backend events API endpoint URL
    :param timeout: HTTP request timeout in seconds
    :return: Response dictionary returned by the backend API upon creation
    :raises EventSubmissionError: If connection fails or HTTP response status indicates an error
    """
    json_bytes = json.dumps(event_data).encode("utf-8")
    
    req = urllib.request.Request(
        url=api_url,
        data=json_bytes,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_bytes = response.read()
            response_json = json.loads(response_bytes.decode("utf-8"))
            return response_json

    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            pass
        raise EventSubmissionError(
            message=f"HTTP error occurred while posting event to {api_url}: Status {e.code}",
            status_code=e.code,
            detail=error_body
        ) from e

    except urllib.error.URLError as e:
        raise EventSubmissionError(
            message=f"Failed to connect to backend API at {api_url}: {e.reason}",
            status_code=503,
            detail=str(e.reason)
        ) from e

    except Exception as e:
        raise EventSubmissionError(
            message=f"Unexpected error during event transmission: {str(e)}",
            status_code=500,
            detail=str(e)
        ) from e
