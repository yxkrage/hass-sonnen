import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import SENSORS_LIST, CONF_NAME_IS_DEFAULT, DATA_TYPE_FLAG_GROUP
from .sonnen_host import SonnenBatterieHost
from .utils import get_sonnen_host_by_entry_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry:ConfigEntry, async_add_entities):
    """Set up sensors from a config entry."""
    sonnen_host: SonnenBatterieHost = get_sonnen_host_by_entry_id(hass=hass, entry_id=config_entry.entry_id)

    # Create a sensor for each sensor in the list
    entities = [
        SonnenBatterieEntity(
            hass=hass,
            sonnen_host=sonnen_host,
            sensor_config=sensor_config,
            config_entry=config_entry
        )
        for sensor_config in SENSORS_LIST
    ]
    async_add_entities(entities)

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
        # Give a name to the sensor
        self._measurement_name = sensor_config[0]
        if self._config_entry.data[CONF_NAME_IS_DEFAULT]:
            # If the name is default, use the serial number of the SonnenBatterie in the name
            self._name = f"sonnen_batterie_{self._sonnen_host.serial_number}_{self._measurement_name}"
        else:
            # If the name is not default, use the name from the config entry
            name = self._config_entry.data.get("name")
            # Remove all chars that are not letters or numbers and make lowercase
            name_normalized = "".join([c for c in name if c.isalnum()]).lower()
            self._name = f"sonnen_batterie_{name_normalized}_{self._measurement_name}"

        self._friendly_name = sensor_config[1]
        self._data_path = sensor_config[2]
        self._data_type = sensor_config[3]
        self._uom = sensor_config[4]
        self._icon = sensor_config[5]
        self._unique_id = f"sonnen_{self._sonnen_host.serial_number}_{self._name}"

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._friendly_name

    @property
    def friendly_name(self):
        """Return the friendly name of the sensor."""
        return self._friendly_name

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
                return "Unknown"

            # Simple data type. Return data as is.
            else:
                return data

        except KeyError:
            _LOGGER.error(f"Could not find data for sensor {self._name} in data from host {self._sonnen_host.host}" )
            return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this sensor."""
        return self._uom

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def device_info(self):
        """Return information to link this entity to a device."""
        return self._sonnen_host.device_info
