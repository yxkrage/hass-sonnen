import asyncio
import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_API_TOKEN,
    CONF_HOST_URL,
    CONF_NAME,
    CONF_NAME_IS_DEFAULT,
    DOMAIN,
)
from .sonnen_host import SonnenBatterieHost

_LOGGER = logging.getLogger(__name__)


class SonnenBatterieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sonnen Batterie."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the config flow."""
        super().__init__()
        self.user_input = {}
        self.sonnen_batterie_host = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        if user_input is not None:
            _LOGGER.debug("Testing connection to Sonnen Batterie at %s", user_input[CONF_HOST_URL])
            await self._create_sonnen_batterie_host(user_input[CONF_HOST_URL], user_input[CONF_API_TOKEN])
            await self.sonnen_batterie_host.get_data_from_host()
            if self.sonnen_batterie_host.data:
                _LOGGER.info("Connection to Sonnen Batterie at %s successful", user_input[CONF_HOST_URL])
                self.user_input = user_input  # Store the user input for the next step
                return await self.async_step_name()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                vol.Required(CONF_HOST_URL): str,
                vol.Required(CONF_API_TOKEN): str
                }
            ),
        )

    async def async_step_name(self, user_input=None):
        """Handle the step to enter a name for the entity."""
        default_name = f"Sonnen Batterie (s/n {self.sonnen_batterie_host.serial_number})"

        if user_input is not None:
            self.user_input[CONF_NAME] = user_input[CONF_NAME]
            self.user_input[CONF_NAME_IS_DEFAULT] = user_input[CONF_NAME] == default_name  # Set flag to indicate if the name was changed from the default
            # return self.async_create_entry(title=self.user_input[CONF_NAME], data=self.user_input)
            return await self.async_step_finish()

        return self.async_show_form(
            step_id="name",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=default_name): str
                }
            ),
        )

    async def async_step_finish(self):
        """Finish the config flow and create the entry."""
        await self.sonnen_batterie_host.close_session()  # Close the session
        return self.async_create_entry(title=self.user_input[CONF_NAME], data=self.user_input)

    async def async_abort(self, reason):
        """Abort the config flow."""
        if self.sonnen_batterie_host:
            await self.sonnen_batterie_host.close()  # Close the session if the flow is aborted
        return await super().async_abort(reason)


    # # # Sonnen Batterie Host methods # # #

    async def _create_sonnen_batterie_host(self, host_url, api_token) -> SonnenBatterieHost:
        """Create a SonnenBatterieHost object."""
        # aiohttp_session = async_get_clientsession(hass=self.hass)
        self.sonnen_batterie_host = await SonnenBatterieHost.create(
            host=host_url,
            api_token=api_token,
            # aiohttp_session=aiohttp_session
        )
        return self.sonnen_batterie_host
