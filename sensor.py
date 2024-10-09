"""Sensor platform for Sonnen Batterie integration. This platform creates sensors for the Sonnen Batterie integration."""

from collections.abc import Coroutine
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DATA_TYPE_FLAG_GROUP, SENSORS_LIST
from .sonnen_host import SonnenBatterieHost
from .utils import get_sonnen_host_by_entry_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry:ConfigEntry, async_add_entities):
    """Set up sensors from a config entry."""
    sonnen_host: SonnenBatterieHost = get_sonnen_host_by_entry_id(hass=hass, entry_id=config_entry.entry_id)

    # Create a sensor for each sensor in the list and 
    # add them to the host object for reference (to be able
    # to update the state of the sensors later)
    sonnen_host.entities = [
        SonnenBatterieEntity(
            hass=hass,
            sonnen_host=sonnen_host,
            sensor_config=sensor_config,
            config_entry=config_entry
        )
        for sensor_config in SENSORS_LIST
    ]

    # Add the entities to Home Assistant
    async_add_entities(sonnen_host.entities)

    # Register the device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        **sonnen_host.device_info  # Unpack the device info
    )


class SonnenBatterieEntity(SensorEntity):
    """Sensor for Sonnen Batterie data.

    Data is retrieved from the SonnenBatterieHost object
    and is presented in the Home Assistant UI as a sensor.
    """

    def __init__(
            self,
            hass:HomeAssistant,
            sonnen_host:SonnenBatterieHost,
            sensor_config:dict,
            config_entry:ConfigEntry
        ) -> None:
        """Initialize the sensor."""
        self._hass = hass
        self._sonnen_host = sonnen_host
        self._config_entry = config_entry

        # Elements in sensor_config are: name, friendly name, path in host data, data type, uom and icon
        self._measurement_name = sensor_config[0]
        self._data_path = sensor_config[2]
        self._data_type = sensor_config[3]
        self._default_value = sensor_config[6]  # Default value for sensor data cannot be retrieved

        self.host_name = self._sonnen_host.name
        self.host_name_normalized = "".join([c for c in self.host_name.replace(" ", "_") if c.isalnum() or c == '_']).lower()

        self._attr_name = sensor_config[1]
        self._attr_unit_of_measurement = sensor_config[4]
        self._attr_icon = sensor_config[5]
        self._attr_unique_id = f"sonnen_batterie_{self._sonnen_host.serial_number}_{self._measurement_name}"
        self._attr_entity_id = f"sensor.{self.host_name_normalized}_{self._measurement_name}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return self._attr_unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._attr_icon

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._attr_unique_id

    @property
    def entity_id(self):
        """Return the entity ID of this entity."""
        return self._attr_entity_id

    @entity_id.setter
    def entity_id(self, value):
        """Set the entity ID of this entity."""
        self._attr_entity_id = value

    @property
    def state(self):
        """Return the state of the sensor."""

        # Use self._data_path to retrieve the data from the host's data property (dict).
        # The data_path is a string with keys separated by periods.
        try:
            data = self._sonnen_host.data
            for key in self._data_path.split("."):
                data = data[key]

            # If the data type is a flag group, the data path will be a group of boolean flags. The
            # flag set to True will be the state of the sensor.
            if self._data_type == DATA_TYPE_FLAG_GROUP:
                for flag, value in data.items():
                    if value is True:  # Ensure that only keys with booleans are considered
                        return flag
                # If no flag is set, return Default
                return self._default_value

            # Simple data type. Return data as is.
            else:
                return data

        except KeyError:
            _LOGGER.error("Could not find data for sensor %s in data from host %s. Returning default value.", self._attr_name, self._sonnen_host.url)
            return self._default_value

    @property
    def device_info(self):
        """Return information to link this entity to a device."""
        return self._sonnen_host.device_info

    def async_update_ha_state(self, force_refresh: bool = False) -> Coroutine[Any, Any, None]:
        """Update the state of the sensor."""
        # Added only to see that it exists
        return super().async_update_ha_state(force_refresh)
