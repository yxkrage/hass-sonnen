"""Helper functions for the SonnenBatterie integration."""

from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENTRY_SERIAL_NUMBER
from .sonnen_host import SonnenBatterieHost


def get_sonnen_host_by_entry_id(hass: HomeAssistant, entry_id: str) -> SonnenBatterieHost | None:
    """Get the config entry by entry_id."""
    for host in hass.data[DOMAIN]:
        if host.entry_id == entry_id:
            return host
    return None


def check_entries_for_duplicate_name(hass: HomeAssistant, name: str):
    """Check if a config entry with the same name already exists."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.title == name:
            return True
    return False


def check_entries_for_duplicate_serial_number(hass: HomeAssistant, serial_number: str):
    """Check if a config entry with the same serial number already exists."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(ENTRY_SERIAL_NUMBER) == serial_number:
            return True
    return False
