"""Live-editable simulated wattage, for `simulate`-mode sources. Set
once at setup, but changeable afterward like everything else here --
no need to remove and re-add the source just to correct the load
figure.
"""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_WATTS, DOMAIN, INTEGRATION_TITLE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SimulatedWattsNumber(hass, entry)])


class SimulatedWattsNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Simulierte Leistung"
    _attr_icon = "mdi:flash-outline"
    _attr_native_min_value = 0
    _attr_native_max_value = 20000
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "W"
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_simulated_watts"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="dr-apple",
            model=INTEGRATION_TITLE,
        )

    @property
    def native_value(self) -> float:
        return self._entry.data.get(CONF_WATTS, 0)

    async def async_set_native_value(self, value: float) -> None:
        new_data = dict(self._entry.data)
        new_data[CONF_WATTS] = value
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        self.async_write_ha_state()
