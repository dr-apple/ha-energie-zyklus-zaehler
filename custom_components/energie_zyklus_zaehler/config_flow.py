"""Config flow: pick the energy source to track. Nothing else is asked
here -- which cycles (day/week/month/year) get tracked is a live switch
on the device page afterward, not a one-time setup choice.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_SOURCE, DOMAIN


class EnergieZyklusZaehlerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            source = user_input[CONF_SOURCE]
            await self.async_set_unique_id(source)
            self._abort_if_unique_id_configured()

            name = (user_input.get("name") or "").strip()
            if not name:
                state = self.hass.states.get(source)
                name = state.attributes.get("friendly_name", source) if state else source

            return self.async_create_entry(title=name, data={CONF_SOURCE: source})

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="energy")
                ),
                vol.Optional("name"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
