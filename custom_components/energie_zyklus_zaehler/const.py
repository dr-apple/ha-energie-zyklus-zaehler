"""Constants for Energie Zyklus Zähler."""

DOMAIN = "energie_zyklus_zaehler"
INTEGRATION_TITLE = "Energie Zyklus Zähler"

CONF_SOURCE = "source"
CONF_METERS = "meters"
CONF_MODE = "mode"
CONF_WATTS = "watts"
CONF_ENABLE_ENTITY = "enable_entity"

MODE_SENSOR = "sensor"
MODE_SIMULATE = "simulate"

SIMULATE_UPDATE_SECONDS = 60

# One entry per selectable reset cycle. `cycle` is the value the built-in
# utility_meter config flow expects; `suffix` becomes part of that meter's
# own name (e.g. "<source name> Tag"); `switch_name` is this cycle's
# on/off switch on the device page.
CYCLES = {
    "tag": {
        "cycle": "daily",
        "suffix": "Tag",
        "switch_name": "Tageszähler aktiv",
        "icon": "mdi:calendar-today",
    },
    "woche": {
        "cycle": "weekly",
        "suffix": "Woche",
        "switch_name": "Wochenzähler aktiv",
        "icon": "mdi:calendar-week",
    },
    "monat": {
        "cycle": "monthly",
        "suffix": "Monat",
        "switch_name": "Monatszähler aktiv",
        "icon": "mdi:calendar-month",
    },
    "jahr": {
        "cycle": "yearly",
        "suffix": "Jahr",
        "switch_name": "Jahreszähler aktiv",
        "icon": "mdi:calendar",
    },
}
