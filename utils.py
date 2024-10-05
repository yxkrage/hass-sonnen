from homeassistant.core import HomeAssistant

from .const import DOMAIN


def get_sonnen_host_by_entry_id(hass: HomeAssistant, entry_id: str):
    """Get the config entry by entry_id."""
    for host in hass.data[DOMAIN]:
        if host.entry_id == entry_id:
            return host