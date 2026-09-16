"""Energie Zyklus Zähler.

For one tracked energy source, exposes a Tag/Woche/Monat/Jahr switch
each. Rather than reimplementing reset-cycle math (month lengths, week
start, leap years, source resets) this delegates the actual counting to
Home Assistant's own built-in utility_meter integration -- one
utility_meter config entry per active switch, created and removed
automatically as switches are toggled, with the resulting sensor
folded onto this source's own device page.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import SOURCE_USER, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import CONF_METERS, CONF_SOURCE, CYCLES, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    manager = MeterManager(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager
    await manager.sync()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove every utility_meter entry this source's manager created."""
    for meter_entry_id in entry.options.get(CONF_METERS, {}).values():
        if hass.config_entries.async_get_entry(meter_entry_id) is not None:
            await hass.config_entries.async_remove(meter_entry_id)


class MeterManager:
    """Keeps one utility_meter entry alive per switch that's on."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

    def _switch_active(self, cycle_key: str) -> bool:
        registry = er.async_get(self.hass)
        unique_id = f"{self.entry.entry_id}_{cycle_key}_aktiv"
        entity_id = registry.async_get_entity_id("switch", DOMAIN, unique_id)
        if entity_id is None:
            return True  # not resolvable yet -- new switches default on
        state = self.hass.states.get(entity_id)
        return state is None or state.state != "off"

    async def sync(self) -> None:
        meters = dict(self.entry.options.get(CONF_METERS, {}))
        changed = False

        for key in CYCLES:
            active = self._switch_active(key)
            existing_id = meters.get(key)
            existing_entry = (
                self.hass.config_entries.async_get_entry(existing_id)
                if existing_id
                else None
            )

            if active and existing_entry is None:
                new_id = await self._create_meter(key)
                if new_id:
                    meters[key] = new_id
                    changed = True
            elif not active and existing_entry is not None:
                await self.hass.config_entries.async_remove(existing_entry.entry_id)
                meters.pop(key, None)
                changed = True

        if changed:
            new_options = dict(self.entry.options)
            new_options[CONF_METERS] = meters
            self.hass.config_entries.async_update_entry(self.entry, options=new_options)

    async def _create_meter(self, key: str) -> str | None:
        meta = CYCLES[key]
        name = f"{self.entry.title} {meta['suffix']}"
        result = await self.hass.config_entries.flow.async_init(
            "utility_meter",
            context={"source": SOURCE_USER},
            data={
                "name": name,
                "source": self.entry.data[CONF_SOURCE],
                "cycle": meta["cycle"],
                "offset": 0,
                "tariffs": [],
                "net_consumption": False,
                "delta_values": False,
                "periodically_resetting": True,
                "always_available": False,
            },
        )
        if result.get("type") != "create_entry":
            _LOGGER.error(
                "Energie Zyklus Zähler: utility_meter für %s (%s) konnte nicht angelegt werden: %s",
                self.entry.data[CONF_SOURCE],
                key,
                result,
            )
            return None

        meter_entry = result["result"]
        self._attach_to_device(meter_entry.entry_id)
        return meter_entry.entry_id

    def _attach_to_device(self, meter_entry_id: str) -> None:
        """Fold the utility_meter's own sensor onto this source's device page."""
        device_registry = dr.async_get(self.hass)
        device = device_registry.async_get_device(identifiers={(DOMAIN, self.entry.entry_id)})
        if device is None:
            return
        entity_registry = er.async_get(self.hass)
        for ent in er.async_entries_for_config_entry(entity_registry, meter_entry_id):
            entity_registry.async_update_entity(ent.entity_id, device_id=device.id)
