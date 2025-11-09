"""Setting up the Sonnen Batterie component."""

from datetime import timedelta
import logging

from aiohttp.client_exceptions import ClientConnectorError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    ENTRY_API_TOKEN,
    ENTRY_NAME,
    ENTRY_URL,
    POLL_FREQUENCY,
)
from .sonnen_host import SonnenBatterieHost

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up my_component from a config entry."""

    # Get the config entry data
    config = dict(entry.data)  # Extract the data from the config entry

    # Create the SonnenBatterie object
    # aiohttp_session = async_get_clientsession(hass=hass)
    _LOGGER.info("Creating Sonnen Batterie host connection for %s", config[ENTRY_URL])
    sonnen_host:SonnenBatterieHost = await SonnenBatterieHost.create(
        url=config[ENTRY_URL],
        api_token=config[ENTRY_API_TOKEN],
        name=config[ENTRY_NAME],
        entry_id=entry.entry_id,
        # aiohttp_session=aiohttp_session
    )

    # Connect to Sonnen Batterie and update the data
    try:
        await sonnen_host.update(update_static_data=True, update_current_data=True)
    except ClientConnectorError as e:
        _LOGGER.error("Failed to connect to Sonnen Batterie at %s: %s", config[ENTRY_URL], e)
        return False

    # # Save data to file
    # import json
    # with open("sonnen_batterie_data.json", "w") as file:
    #     json.dump(sonnen_host.data, file, indent=4)

    # Store the config entry data in hass.data
    hass.data.setdefault(DOMAIN, [])  # Ensure the top-level domain list exists
    hass.data[DOMAIN].append(sonnen_host)

    # Register the platform (e.g., sensor, switch)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Schedule the update every 5 seconds
    async_track_time_interval(hass, sonnen_host.update_callback, timedelta(seconds=POLL_FREQUENCY))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
