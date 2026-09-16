"""Per-cycle on/off switches. Toggling one creates or removes the
matching utility_meter entry for this source via the MeterManager.
"""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CYCLES, DOMAIN, INTEGRATION_TITLE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(CycleSwitch(hass, entry, key) for key in CYCLES)


class CycleSwitch(SwitchEntity, RestoreEntity):
    """One reset-cycle's on/off switch. Defaults on -- a newly added
    source gets all four counters immediately, matching the common case;
    turn off the ones you don't want for that particular plug.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, cycle_key: str) -> None:
        self.hass = hass
        self._entry = entry
        self._cycle_key = cycle_key
        meta = CYCLES[cycle_key]
        self._attr_unique_id = f"{entry.entry_id}_{cycle_key}_aktiv"
        self._attr_icon = meta["icon"]
        self._name = meta["switch_name"]
        self._is_on = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="dr-apple",
            model=INTEGRATION_TITLE,
        )

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        self._is_on = True
        self.async_write_ha_state()
        await self._sync()

    async def async_turn_off(self, **kwargs) -> None:
        self._is_on = False
        self.async_write_ha_state()
        await self._sync()

    async def _sync(self) -> None:
        manager = self.hass.data[DOMAIN][self._entry.entry_id]
        await manager.sync()
