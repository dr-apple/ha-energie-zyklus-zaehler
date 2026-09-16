"""Simulated constant-power energy sensor.

For a device with no real power measurement but a known, steady draw
(e.g. a satellite distributor running 24/7 at a fixed wattage): accumulates
kWh over time from a configured constant watt figure, so it behaves like a
real total_increasing energy sensor and can feed the same
Tag/Woche/Monat/Jahr counters a real sensor would.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .const import CONF_WATTS, DOMAIN, INTEGRATION_TITLE, SIMULATE_UPDATE_SECONDS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SimulatedEnergySensor(hass, entry)])


class SimulatedEnergySensor(SensorEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Simulierte Energie"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:power-plug-outline"
    _attr_should_poll = False
    _attr_suggested_display_precision = 3

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_simulated_energy"
        self._total_kwh = 0.0
        self._last_update: datetime | None = None

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
        return round(self._total_kwh, 4)

    @property
    def extra_state_attributes(self) -> dict:
        return {"simulierte_leistung_w": self._entry.data.get(CONF_WATTS, 0)}

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._total_kwh = float(last_state.state)
            except (TypeError, ValueError):
                self._total_kwh = 0.0
        self._last_update = dt_util.utcnow()
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._tick, timedelta(seconds=SIMULATE_UPDATE_SECONDS)
            )
        )

    async def _tick(self, now: datetime) -> None:
        watts = self._entry.data.get(CONF_WATTS, 0)
        elapsed = (now - self._last_update).total_seconds() if self._last_update else 0
        self._last_update = now
        if elapsed > 0 and watts:
            self._total_kwh += watts * elapsed / 3600 / 1000
            self.async_write_ha_state()
