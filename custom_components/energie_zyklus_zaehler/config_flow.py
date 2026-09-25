"""Config flow: either pick a real energy sensor, or describe a constant
load to simulate (a device with no power measurement that just draws a
known, steady wattage). Which cycles get tracked is a live switch on
the device page afterward either way -- not a one-time setup choice.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from homeassistant.core import callback

from .const import (
    CONF_ENABLE_ENTITY,
    CONF_MODE,
    CONF_SOURCE,
    CONF_WATTS,
    DOMAIN,
    MODE_SENSOR,
    MODE_SIMULATE,
)


class EnergieZyklusZaehlerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return EnergieZyklusZaehlerOptionsFlow()

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        return self.async_show_menu(step_id="user", menu_options=["sensor", "simulate"])

    async def async_step_sensor(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            source = user_input[CONF_SOURCE]
            await self.async_set_unique_id(source)
            self._abort_if_unique_id_configured()

            name = (user_input.get("name") or "").strip()
            if not name:
                state = self.hass.states.get(source)
                name = state.attributes.get("friendly_name", source) if state else source

            return self.async_create_entry(
                title=name, data={CONF_MODE: MODE_SENSOR, CONF_SOURCE: source}
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="energy")
                ),
                vol.Optional("name"): str,
            }
        )
        return self.async_show_form(step_id="sensor", data_schema=schema, errors=errors)

    async def async_step_simulate(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input["name"].strip()
            watts = user_input[CONF_WATTS]
            if not name:
                errors["name"] = "required"
            else:
                data = {CONF_MODE: MODE_SIMULATE, CONF_WATTS: watts}
                if user_input.get(CONF_ENABLE_ENTITY):
                    data[CONF_ENABLE_ENTITY] = user_input[CONF_ENABLE_ENTITY]
                return self.async_create_entry(title=name, data=data)

        schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required(CONF_WATTS): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=20000, step=1, unit_of_measurement="W")
                ),
                vol.Optional(CONF_ENABLE_ENTITY): selector.EntitySelector(),
            }
        )
        return self.async_show_form(step_id="simulate", data_schema=schema, errors=errors)


class EnergieZyklusZaehlerOptionsFlow(config_entries.OptionsFlow):
    """Change (or clear) the entity that gates a simulated load later on."""

    async def async_step_init(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        entry = self.config_entry
        if entry.data.get(CONF_MODE) != MODE_SIMULATE:
            return self.async_abort(reason="nur_simulation")

        if user_input is not None:
            new_data = dict(entry.data)
            gate = user_input.get(CONF_ENABLE_ENTITY)
            if gate:
                new_data[CONF_ENABLE_ENTITY] = gate
            else:
                new_data.pop(CONF_ENABLE_ENTITY, None)
            self.hass.config_entries.async_update_entry(entry, data=new_data)
            return self.async_create_entry(data=dict(entry.options))

        schema = self.add_suggested_values_to_schema(
            vol.Schema({vol.Optional(CONF_ENABLE_ENTITY): selector.EntitySelector()}),
            {CONF_ENABLE_ENTITY: entry.data.get(CONF_ENABLE_ENTITY)},
        )
        return self.async_show_form(step_id="init", data_schema=schema)
