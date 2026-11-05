"""Setup in one step: the defaults match the Neolink Local add-on."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import NeolinkClient, NeolinkError
from .const import (
    CONF_API_PORT,
    CONF_RTSP_HOST,
    CONF_STREAM,
    DEFAULT_API_PORT,
    DEFAULT_HOST,
    DEFAULT_STREAM,
    DOMAIN,
    STREAMS,
)


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, DEFAULT_HOST)): str,
            vol.Required(
                CONF_API_PORT, default=defaults.get(CONF_API_PORT, DEFAULT_API_PORT)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Optional(
                CONF_RTSP_HOST, default=defaults.get(CONF_RTSP_HOST, "")
            ): str,
            vol.Optional(CONF_USERNAME, default=defaults.get(CONF_USERNAME, "")): str,
            vol.Optional(
                CONF_PASSWORD, default=defaults.get(CONF_PASSWORD, "")
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        }
    )


class NeolinkConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add Neolink Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_API_PORT]
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            client = NeolinkClient(async_get_clientsession(self.hass), host, port)
            try:
                status = await client.status()
            except NeolinkError:
                errors["base"] = "cannot_connect"
            else:
                count = len(status["cameras"])
                return self.async_create_entry(
                    title="Neolink Local",
                    data={**user_input, CONF_HOST: host},
                    description_placeholders={"count": str(count)},
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return NeolinkOptionsFlow()


class NeolinkOptionsFlow(OptionsFlow):
    """Choose which stream the camera entities play."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_STREAM, DEFAULT_STREAM)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STREAM, default=current): SelectSelector(
                        SelectSelectorConfig(
                            options=STREAMS,
                            translation_key="stream",
                            mode=SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )
