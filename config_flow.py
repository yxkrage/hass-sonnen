"""Config flow for Sonnen Batterie integration."""

import logging

from aiohttp.client_exceptions import ClientConnectorError
import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, ENTRY_API_TOKEN, ENTRY_NAME, ENTRY_SERIAL_NUMBER, ENTRY_URL
from .sonnen_host import SonnenBatterieHost
from .utils import (
    check_entries_for_duplicate_name,
    check_entries_for_duplicate_serial_number,
)

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

        errors = {}
        if user_input is not None:
            _LOGGER.debug("Testing connection to Sonnen Batterie at %s", user_input[ENTRY_URL])
            try:
                await self._create_sonnen_batterie_host(user_input[ENTRY_URL], user_input[ENTRY_API_TOKEN])
                await self.sonnen_batterie_host.update(update_static_data=True, update_current_data=False)

                # If no exception was raised, the connection was successful
                _LOGGER.info("Connection to Sonnen Batterie at %s successful", user_input[ENTRY_URL])
                user_input[ENTRY_SERIAL_NUMBER] = self.sonnen_batterie_host.serial_number
                self.user_input = user_input  # Store the user input for the next step

                # Check that no other entry exists for this host name or serial number
                if check_entries_for_duplicate_name(hass=self.hass, name=user_input[ENTRY_NAME]):
                    errors["base"] = "duplicate_name"
                elif check_entries_for_duplicate_serial_number(hass=self.hass, serial_number=self.sonnen_batterie_host.serial_number):
                    errors["base"] = "duplicate_serial_number"
                else:
                    return await self.async_step_finish()
            except ClientConnectorError as e:
                _LOGGER.warning("Unable to connect to Sonnen Batterie at %s: %s", user_input[ENTRY_URL], e)
                errors["base"] = "failed_to_connect"
            except Exception as e:
                _LOGGER.error("Unknown error connecting to Sonnen Batterie at %s: %s", user_input[ENTRY_URL], e)
                errors["base"] = "failed_to_connect_unknown"


        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(ENTRY_NAME, default="My Sonnen Batterie"): str,
                    vol.Required(ENTRY_URL): str,
                    vol.Required(ENTRY_API_TOKEN): str
                }
            ),
            errors=errors,
        )

    async def async_step_finish(self):
        """Finish the config flow and create the entry."""
        await self.sonnen_batterie_host.close_session()  # Close the session
        return self.async_create_entry(title=self.user_input[ENTRY_NAME], data=self.user_input)

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
            url=host_url,
            api_token=api_token,
            # aiohttp_session=aiohttp_session
        )
        return self.sonnen_batterie_host
