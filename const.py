"""Constants for the Sonnen Batterie integration."""

DOMAIN = 'sonnen_batterie'
CONST_COMPONENT_TYPES = ["sensor"]  # ["sensor","select","number","switch"]

# Configuration flow keys
ENTRY_URL = 'host_url'
ENTRY_NAME = 'name'
ENTRY_API_TOKEN = 'api_token'
ENTRY_SERIAL_NUMBER = 'serial_number'

POLL_FREQUENCY = 2  # Polling frequency in seconds

DATA_TYPE_FLAG_GROUP = "flag_group"  # Custom data type for to indicate that the data is a group of boolean flags

SENSORS_LIST = [
    # ["name", "friendly name", "path in host data", "data type", "uom", "icon", "default value"]
    ["serial_number", "Serial Number", "host.serial_number", "int", None, "mdi:identifier", None],
    ["battery_charging", "Battery Charging", "status.BatteryCharging", "bool", None, "mdi:battery-charging", None],
    ["battery_discharging", "Battery Discharging", "status.BatteryDischarging", "bool", None, "mdi:battery-charging", None],
    ["consumption_avg", "Consumption Average", "status.Consumption_Avg", "int", "W", "mdi:flash", None],
    ["consumption_w", "Consumption", "status.Consumption_W", "int", "W", "mdi:flash", None],
    ["fac", "Frequency", "status.Fac", "float", "Hz", "mdi:sine-wave", None],
    ["grid_feed_in_w", "Grid Feed-In", "status.GridFeedIn_W", "int", "W", "mdi:transmission-tower", None],
    ["operating_mode", "Operating Mode", "status.OperatingMode", "str", None, "mdi:cog", None],
    ["pac_total_w", "Total Power Consumption", "status.Pac_total_W", "int", "W", "mdi:flash", None],
    ["production_w", "Production", "status.Production_W", "int", "W", "mdi:solar-panel", None],
    ["rsoc", "Relative State of Charge", "status.RSOC", "int", "%", "mdi:battery", None],
    ["remaining_capacity_wh", "Remaining Capacity", "status.RemainingCapacity_Wh", "int", "Wh", "mdi:battery", None],
    ["system_status", "System Status", "status.SystemStatus", "str", None, "mdi:information", None],
    # ["timestamp", "Timestamp", "status.Timestamp", "str", None, "mdi:clock", None],
    ["usoc", "Usable State of Charge", "status.USOC", "int", "%", "mdi:battery", None],
    ["uac", "AC Voltage", "status.Uac", "int", "V", "mdi:flash", None],
    ["ubat", "Battery Voltage", "status.Ubat", "int", "V", "mdi:flash", None],
    ["discharge_not_allowed", "Discharge Not Allowed", "status.dischargeNotAllowed", "bool", None, "mdi:alert", None],
    ["full_charge_capacity", "Full Charge Capacity", "data.FullChargeCapacity", "int", "Wh", "mdi:battery", None],
    ["set_point_w", "Set Point", "data.SetPoint_W", "int", "W", "mdi:flash", None],
    ["utc_offset", "UTC Offset", "data.UTC_Offet", "int", "h", "mdi:clock", None],
    ["eclipse_led_brightness", "Eclipse Led Brightness", "data.ic_status.Eclipse Led.Brightness", "int", "%", "mdi:brightness-6", None],
    ["number_of_battery_modules", "Number of Battery Modules", "data.ic_status.nrbatterymodules", "int", None, "mdi:battery", None],
    ["number_of_battery_modules_in_parallel", "Battery Modules in Parallel", "data.ic_status.nrbatterymodulesinparallel", "int", None, "mdi:battery", None],
    ["number_of_battery_modules_in_series", "Battery Modules in Series", "data.ic_status.nrbatterymodulesinseries", "int", None, "mdi:battery", None],
    ["seconds_since_full_charge", "Seconds Since Full Charge", "data.ic_status.secondssincefullcharge", "int", "s", "mdi:clock", None],
    ["bms_state", "BMS State", "data.ic_status.statebms", "str", None, "mdi:information", None],
    ["core_control_module_state", "Core Control Module State", "data.ic_status.statecorecontrolmodule", "str", None, "mdi:information", None],
    ["inverter_state", "Inverter State", "data.ic_status.stateinverter", "str", None, "mdi:information", None],

    ["dc_shutdown_reason", "DC Shutdown Reason", "data.ic_status.DC Shutdown Reason", DATA_TYPE_FLAG_GROUP, None, "mdi:alert", "Not shutdown"],
    # ["droop_mode_status", "Droop mode status", "data.ic_status.Droop mode status", DATA_TYPE_FLAG_GROUP, None, "mdi:information", "Unknown"],
    ["eclipse_led_mode", "Eclipse Led Mode", "data.ic_status.Eclipse Led", DATA_TYPE_FLAG_GROUP, None, "mdi:led-on", None, "Unknown"],
    # ["microgrid_status", "Microgrid Status", "data.ic_status.Microgrid Status", DATA_TYPE_FLAG_GROUP, None, "mdi:led-on", None, "Unknown"]
    ["setpoint_priority", "Setpoint Priority", "data.ic_status.Setpoint Priority", DATA_TYPE_FLAG_GROUP, None, "mdi:priority-high", None, "Unknown"]
]
