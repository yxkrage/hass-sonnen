"""Setting up the Sonnen Batterie component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_API_TOKEN, CONF_HOST_URL, CONST_COMPONENT_TYPES, DOMAIN
from .sonnen_host import SonnenBatterieHost

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component."""
    # hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up my_component from a config entry."""

    # Get the config entry data
    config = dict(entry.data)  # Extract the data from the config entry

    # Create the SonnenBatterie object
    # aiohttp_session = async_get_clientsession(hass=hass)
    _LOGGER.info(f"Creating Sonnen Batterie host connection for {config[CONF_HOST_URL]}")
    sonnen_host:SonnenBatterieHost = await SonnenBatterieHost.create(
        host=config[CONF_HOST_URL],
        api_token=config[CONF_API_TOKEN],
        entry_id=entry.entry_id,
        # aiohttp_session=aiohttp_session
    )

    # Check if the SonnenBatterie is connected
    await sonnen_host.get_data_from_host()
    if not sonnen_host.data:
        _LOGGER.error(f"SonnenBatterie at {config[CONF_HOST_URL]} is not connected.")
        return False

    # data = await sonnen_host.get_data()
    # # Save data to file
    # import json
    # with open("sonnen_batterie_data.json", "w") as file:
    #     json.dump(data, file, indent=4)


    # Store the config entry data in hass.data
    hass.data.setdefault(DOMAIN, [])  # Ensure the top-level domain list exists
    hass.data[DOMAIN].append(sonnen_host)

    # Register the platform (e.g., sensor, switch)
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # hass.data.pop(DOMAIN)
    # return True
    return await hass.config_entries.async_unload_platforms(entry, CONST_COMPONENT_TYPES)
