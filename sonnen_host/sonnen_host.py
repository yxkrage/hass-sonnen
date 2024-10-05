"""Asynchronous Python client for the SonnenBatterie API."""

import asyncio

import aiohttp
from bs4 import BeautifulSoup

from ..const import DOMAIN

URI_STATUS = "/api/status"
URI_DATA = "/api/v2/latestdata"
URI_READY = "/api/ready"

URI_DASHBOARD = "/dash/dashboard"


class SonnenBatterieHost:
    """Asynchronous Python client for the SonnenBatterie API."""

    def __init__(
        self,
        host: str,
        api_token: str,
        entry_id: str,
        aiohttp_session: aiohttp.ClientSession
    ) -> None:
        """WARNING: Do not call this method directly. Use the create method instead."""
        self.host = host
        self.api_token = api_token
        self.entry_id = entry_id
        self.aiohttp_session = aiohttp_session

        self.have_data_from_host = False
        self.data_status = None
        self.data_latestdata = None
        self.data_dashboard_html = None
        self._serial_number_uri = None
        self.serial_number = None

    @classmethod
    async def create(
        cls,
        host: str,
        api_token: str,
        entry_id: str = None,
        aiohttp_session: aiohttp.ClientSession = None
    ) -> 'SonnenBatterieHost':
        """Create a new SonnenBatterie object."""
        if aiohttp_session is None:
            aiohttp_session = aiohttp.ClientSession()
        return cls(host=host, api_token=api_token, entry_id=entry_id, aiohttp_session=aiohttp_session)

    async def is_connected(self) -> bool:
        """Check if the SonnenBatterie is connected."""
        async with self.aiohttp_session.get(f"{self.host}{URI_READY}", headers={'Auth-Token': self.api_token}) as response:
            return response.status == 200 and await response.text() == '"go"'

    async def _get_status_from_host(self) -> None:
        async with self.aiohttp_session.get(f"{self.host}{URI_STATUS}", headers={'Auth-Token': self.api_token}) as response:
            self.data_status = await response.json()

    async def _get_latestdata_from_host(self) -> None:
        async with self.aiohttp_session.get(f"{self.host}{URI_DATA}", headers={'Auth-Token': self.api_token}) as response:
            self.data_latestdata = await response.json()

    async def _get_dashboard_html_from_host(self) -> None:
        """Get the dashboard from the host. Response is HTML."""
        async with self.aiohttp_session.get(f"{self.host}{URI_DASHBOARD}", headers={'Auth-Token': self.api_token}) as response:
            self.data_dashboard_html = await response.text()

    def _parse_dashboard_html(self, html: str) -> None:
        """Parse the dashboard HTML and return the data."""
        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')

        # Find all script tags in the body
        script_tags = soup.body.find_all('script')

        # Extract the src attribute from each script tag
        script_srcs = [script.get('src') for script in script_tags if script.get('src')]

        for src in script_srcs:
            if 'device-id' in src:
                self._serial_number_uri = src
                break

    async def _get_serial_number_from_host(self, serial_number_uri: str) -> None:
        # Get the device ID from API URL
        async with self.aiohttp_session.get(f"{self.host}{serial_number_uri}", headers={'Auth-Token': self.api_token}) as response:
            if response.status != 200:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Failed to fetch serial number from host {self.host}",
                )
            serial_data = await response.text()
        self.serial_number = serial_data.split('SPREE_ID = ')[1].split(';')[0].strip("'")

    async def get_data_from_host(self) -> None:
        """Get the latest data from the SonnenBatterie."""
        # Get data from the host in parallel
        await asyncio.gather(
            self._get_status_from_host(),
            self._get_latestdata_from_host(),
            self._get_dashboard_html_from_host()
        )

        # Parse the dashboard HTML to get the URI for the serial number
        self._parse_dashboard_html(self.data_dashboard_html)

        # Get the serial number from the host
        await self._get_serial_number_from_host(self._serial_number_uri)

        # Set the flag to indicate that we have data from the host
        self.have_data_from_host = True

    @property
    def data(self) -> dict | None:
        """Get the data from the Sonnen Batterie Host."""

        if not self.have_data_from_host:
            return None

        # Combine status and data into one dictionary
        return {
            "host": {
                "url": self.host,
                "serial_number": self.serial_number
            },
            "status": self.data_status,
            "data": self.data_latestdata
        }

    async def close_session(self) -> None:
        """Close the aiohttp session."""
        # await self.aiohttp_session.__aexit__(None, None, None)
        await self.aiohttp_session.close()

    @property
    def device_info(self) -> dict:
        """Return information to link this entity to a device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": "Sonnen Batterie",
            "manufacturer": "Sonnen",
            "model": "Unknown"  # TODO: Get the model from the host
        }

# # Usage example
# async def main():
#     sonnen = await SonnenBatterie.create("http://example.com", "your_api_token")
#     status = await sonnen._get_status()
#     print(status)
#     await sonnen.close_session()

# # Run the example
# asyncio.run(main())
