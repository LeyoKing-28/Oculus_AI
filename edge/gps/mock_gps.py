"""Mock GPS Provider for edge event generation layer.

Simulates GPS hardware input by returning configurable geographic coordinates.
Designed to be easily replaced by an actual hardware GPS provider implementing
the same interface (get_location / get_coordinates).
"""

from typing import Dict, Tuple


class BaseGPSProvider:
    """Abstract interface for GPS coordinate providers."""
    
    def get_location(self) -> Dict[str, float]:
        """Returns a dictionary containing 'latitude' and 'longitude'."""
        raise NotImplementedError
    
    def get_coordinates(self) -> Tuple[float, float]:
        """Returns a tuple of (latitude, longitude)."""
        raise NotImplementedError


class MockGPSProvider(BaseGPSProvider):
    """Mock implementation of GPSProvider returning configurable static or dynamic coordinates."""

    def __init__(self, latitude: float = 18.5204, longitude: float = 73.8567):
        """
        Initialize MockGPSProvider with default or custom coordinates.

        :param latitude: Default latitude coordinate (WGS84)
        :param longitude: Default longitude coordinate (WGS84)
        """
        self.latitude = latitude
        self.longitude = longitude

    def get_location(self) -> Dict[str, float]:
        """
        Retrieve current geographic coordinates as a dictionary.

        :return: Dict containing 'latitude' and 'longitude'
        """
        return {
            "latitude": float(self.latitude),
            "longitude": float(self.longitude)
        }

    def get_coordinates(self) -> Tuple[float, float]:
        """
        Retrieve current geographic coordinates as a tuple.

        :return: Tuple of (latitude, longitude)
        """
        return float(self.latitude), float(self.longitude)

    def set_location(self, latitude: float, longitude: float) -> None:
        """
        Update simulated GPS position.

        :param latitude: New latitude coordinate
        :param longitude: New longitude coordinate
        """
        self.latitude = latitude
        self.longitude = longitude
