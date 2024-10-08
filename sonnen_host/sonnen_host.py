"""Asynchronous Python client for the SonnenBatterie API."""

import asyncio
import logging
from typing import List

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.helpers.entity import Entity

from ..const import DOMAIN

URI_STATUS = "/api/status"
URI_DATA = "/api/v2/latestdata"
URI_READY = "/api/ready"

URI_DASHBOARD = "/dash/dashboard"

_LOGGER = logging.getLogger(__name__)


class SonnenBatterieHost:
    """Asynchronous Python client for the SonnenBatterie API."""

    def __init__(
        self,
        url: str,
        api_token: str,
        name: str,
        entry_id: str,
        aiohttp_session: aiohttp.ClientSession
    ) -> None:
        """WARNING: Do not call this method directly. Use the create method instead."""
        self.url = url
        self.api_token = api_token
        self.name = name
        self.entry_id = entry_id
        self.aiohttp_session = aiohttp_session

        self.data_status = None
        self.data_latestdata = None
        self._data_dashboard_html = None
        self._serial_number_uri = None
        self.serial_number = None

        self.entities:List[Entity] = []  # List of entities that are associated with this host

    @classmethod
    async def create(
        cls,
        url: str,
        api_token: str,
        name: str = None,  # Name as given in Config Entry
        entry_id: str = None,
        aiohttp_session: aiohttp.ClientSession = None
    ) -> 'SonnenBatterieHost':
        """Create a new SonnenBatterie object."""
        if aiohttp_session is None:
            _LOGGER.debug("Creating new aiohttp session for SonnenBatterie host %s", url)
            aiohttp_session = aiohttp.ClientSession()
        return cls(url=url, api_token=api_token, name=name, entry_id=entry_id, aiohttp_session=aiohttp_session)

    async def is_connected(self) -> bool:
        """Check if the SonnenBatterie is connected."""
        try:
            async with self.aiohttp_session.get(f"{self.url}{URI_READY}", headers={'Auth-Token': self.api_token}) as response:
                return response.status == 200 and await response.text() == '"go"'
        except (TimeoutError, aiohttp.ClientResponseError) as e:
            _LOGGER.error("Failed to get data from Sonnen Batterie at %s: %s", self.url + URI_READY,  e)
            return False

    async def _get_status_from_host(self) -> None:
        try:
            async with self.aiohttp_session.get(f"{self.url}{URI_STATUS}", headers={'Auth-Token': self.api_token}) as response:
                self.data_status = await response.json()
        except (TimeoutError, aiohttp.ClientResponseError) as e:
            _LOGGER.error("Failed to get data from Sonnen Batterie at %s: %s", self.url + URI_STATUS,  e)
            self.data_status = None

    async def _get_latestdata_from_host(self) -> None:
        try:
            async with self.aiohttp_session.get(f"{self.url}{URI_DATA}", headers={'Auth-Token': self.api_token}) as response:
                self.data_latestdata = await response.json()
        except (TimeoutError, aiohttp.ClientResponseError) as e:
            _LOGGER.error("Failed to get data from Sonnen Batterie at %s: %s", self.url + URI_DATA,  e)
            self.data_latestdata = None

    async def _get_dashboard_html_from_host(self) -> None:
        """Get the dashboard from the host. Response is HTML."""
        try:
            async with self.aiohttp_session.get(f"{self.url}{URI_DASHBOARD}", headers={'Auth-Token': self.api_token}) as response:
                self._data_dashboard_html = await response.text()
        except (TimeoutError, aiohttp.ClientResponseError) as e:
            _LOGGER.error("Failed to get data from Sonnen Batterie at %s: %s", self.url + URI_DASHBOARD,  e)
            self._data_dashboard_html = None

    def _parse_dashboard_html(self) -> None:
        """Parse the dashboard HTML and return the data."""
        # Parse the HTML content
        soup = BeautifulSoup(self._data_dashboard_html, 'html.parser')

        # Find all script tags in the body
        script_tags = soup.body.find_all('script')

        # Extract the src attribute from each script tag
        script_srcs = [script.get('src') for script in script_tags if script.get('src')]

        for src in script_srcs:
            if 'device-id' in src:
                self._serial_number_uri = src
                break

    async def _get_serial_number_from_host(self) -> None:
        # Get the device ID from API URL
        try:
            async with self.aiohttp_session.get(f"{self.url}{self._serial_number_uri}", headers={'Auth-Token': self.api_token}) as response:
                serial_data = await response.text()
            try:
                self.serial_number = serial_data.split('SPREE_ID = ')[1].split(';')[0].strip("'")
            except IndexError:
                _LOGGER.error("Failed to get serial number from Sonnen Batterie at %s: %s", self.url + self._serial_number_uri,  serial_data)
                raise # Raise the exception to the caller. Cannot continue without the serial number!
        except (TimeoutError, aiohttp.ClientResponseError) as e:
            _LOGGER.error("Failed to get data from Sonnen Batterie at %s: %s", self.url + self._serial_number_uri,  e)
            raise  # Raise the exception to the caller. Cannot continue without the serial number!

    async def _get_current_data_from_host(self) -> None:
        """Get the latest data from the Sonnen Batterie."""
        # Get data from the host in parallel
        await asyncio.gather(
            self._get_status_from_host(),
            self._get_latestdata_from_host(),
        )

    async def _get_static_data_from_host(self) -> None:
        """Get the static data, e.g. Serial Number, from the Sonnen Batterie."""
        await self._get_dashboard_html_from_host()  # Get the dashboard HTML
        self._parse_dashboard_html()  # Parse the dashboard HTML to get the URI for the serial number
        await self._get_serial_number_from_host()  # Get the serial number from the host

    async def update(self, update_static_data:bool = False, update_current_data:bool = True) -> None:
        """Update the data from the Sonnen Batterie."""
        coroutines = []
        if update_static_data:
            coroutines.append(self._get_static_data_from_host())
        if update_current_data:
            coroutines.append(self._get_current_data_from_host())
        await asyncio.gather(*coroutines)

    async def update_callback(self, now) -> None:
        """Update the data from the Sonnen Batterie using the callback method
        called from e.g. `async_track_time_interval`."""
        _LOGGER.debug("Updating data from Sonnen Batterie at %s", self.url)
        await self.update(update_static_data=False, update_current_data=True)
        await self.update_entity_states()

    async def update_entity_states(self) -> None:
        """Update the states of the entities associated with this host."""
        await asyncio.gather(*(entity.async_update_ha_state(force_refresh=True) for entity in self.entities))

    @property
    def data(self) -> dict | None:
        """Get the data from the Sonnen Batterie Host."""
        return {
            "host": {
                "url": self.url,
                "serial_number": self.serial_number
            },
            "status": self.data_status,
            "data": self.data_latestdata
        }

    async def close_session(self) -> None:
        """Close the aiohttp session."""
        await self.aiohttp_session.close()

    @property
    def device_info(self) -> dict:
        """Return information to link this entity to a device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": "Sonnen Batterie",
            "manufacturer": "Sonnen GmbH",
            "model": "Unknown"  # TODO: Get the model from the host
        }
