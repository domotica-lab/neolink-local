"""End-to-end tests of the integration against a fake Neolink Local add-on."""

from datetime import timedelta

from homeassistant import config_entries
from homeassistant.components.camera import async_get_image, async_get_stream_source
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.neolink_local.const import DOMAIN

API = "http://127.0.0.1:8559/api"


def camera(name, connected=False, viewers=0, last=None):
    return {
        "name": name,
        "enabled": True,
        "connect_mode": "on_demand",
        "connected": connected,
        "viewers": viewers,
        "streams": [
            {"stream": "main", "path": f"/{name}/main", "viewers": viewers,
             "streaming": viewers > 0, "last_frame_at": last},
            {"stream": "sub", "path": f"/{name}/sub", "viewers": 0,
             "streaming": False, "last_frame_at": None},
        ],
    }


def status(*cams):
    return {"version": "0.7.19-local2", "rtsp_port": 8558, "cameras": list(cams)}


async def setup(hass, aioclient_mock, payload, data=None, options=None):
    aioclient_mock.get(f"{API}/status", json=payload)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Neolink Local",
        unique_id="127.0.0.1:8559",
        data=data or {"host": "127.0.0.1", "api_port": 8559, "rtsp_host": "",
                      "username": "", "password": ""},
        options=options or {},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_flow_creates_entry_with_defaults(hass: HomeAssistant, aioclient_mock):
    aioclient_mock.get(f"{API}/status", json=status(camera("Giardino")))
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"host": "127.0.0.1", "api_port": 8559}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Neolink Local"
    assert result["result"].unique_id == "127.0.0.1:8559"


async def test_flow_reports_unreachable_addon(hass: HomeAssistant, aioclient_mock):
    aioclient_mock.get(f"{API}/status", status=500)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"host": "127.0.0.1", "api_port": 8559}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_flow_refuses_duplicates(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Giardino")))
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"host": "127.0.0.1", "api_port": 8559}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_entities_for_each_camera(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(
        camera("Giardino", connected=True, viewers=2, last=1_790_000_000),
        camera("Portone"),
    ))
    assert hass.states.get("binary_sensor.giardino_connected").state == STATE_ON
    assert hass.states.get("binary_sensor.portone_connected").state == STATE_OFF
    assert hass.states.get("sensor.giardino_viewers").state == "2"
    assert hass.states.get("sensor.portone_viewers").state == "0"
    assert hass.states.get("sensor.giardino_last_image").state.startswith("2026-")
    assert hass.states.get("sensor.portone_last_image").state == "unknown"
    cam = hass.states.get("camera.giardino")
    assert cam.state == "streaming"
    assert cam.attributes["viewers"] == 2
    assert hass.states.get("camera.portone").state == "idle"


async def test_stream_source_is_the_addon_rtsp(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Porta Nord")))
    src = await async_get_stream_source(hass, "camera.porta_nord")
    assert src == "rtsp://127.0.0.1:8558/Porta%20Nord/main"


async def test_stream_source_with_credentials_and_sub(hass: HomeAssistant, aioclient_mock):
    await setup(
        hass, aioclient_mock, status(camera("Giardino")),
        data={"host": "127.0.0.1", "api_port": 8559, "rtsp_host": "192.168.1.10",
              "username": "ha", "password": "p@ss:w"},
        options={"stream": "sub"},
    )
    src = await async_get_stream_source(hass, "camera.giardino")
    assert src == "rtsp://ha:p%40ss%3Aw@192.168.1.10:8558/Giardino/sub"


async def test_missing_stream_falls_back(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Giardino")), options={"stream": "extern"})
    src = await async_get_stream_source(hass, "camera.giardino")
    assert src.endswith("/Giardino/main")


async def test_snapshot_comes_from_the_addon(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Giardino")))
    aioclient_mock.get(f"{API}/cameras/Giardino/snapshot.jpg", content=b"\xff\xd8jpeg")
    image = await async_get_image(hass, "camera.giardino")
    assert image.content == b"\xff\xd8jpeg"
    call = aioclient_mock.mock_calls[-1]
    assert str(call[1]).endswith("/api/cameras/Giardino/snapshot.jpg?stream=main")


async def test_new_camera_appears_on_refresh(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Giardino")))
    assert hass.states.get("camera.cancello") is None
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{API}/status", json=status(camera("Giardino"), camera("Cancello")))
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=11))
    await hass.async_block_till_done()
    assert hass.states.get("camera.cancello") is not None
    assert hass.states.get("binary_sensor.cancello_connected").state == STATE_OFF


async def test_addon_down_makes_entities_unavailable(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Giardino")))
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{API}/status", status=500)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=11))
    await hass.async_block_till_done()
    assert hass.states.get("binary_sensor.giardino_connected").state == STATE_UNAVAILABLE
    assert hass.states.get("camera.giardino").state == STATE_UNAVAILABLE


async def test_options_switch_stream(hass: HomeAssistant, aioclient_mock):
    entry = await setup(hass, aioclient_mock, status(camera("Giardino")))
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"stream": "sub"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    src = await async_get_stream_source(hass, "camera.giardino")
    assert src.endswith("/Giardino/sub")


async def test_battery_entities_appear_after_first_reading(hass: HomeAssistant, aioclient_mock):
    await setup(hass, aioclient_mock, status(camera("Giardino")))
    assert hass.states.get("sensor.giardino_battery") is None
    cam = camera("Giardino")
    cam["battery"] = {"percent": 76, "charging": True, "charge_status": "charging",
                      "adapter": "solarPanel", "temperature": 18, "low": False,
                      "updated_at": 1_790_000_000}
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{API}/status", json=status(cam))
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=11))
    await hass.async_block_till_done()
    bat = hass.states.get("sensor.giardino_battery")
    assert bat.state == "76"
    assert bat.attributes["unit_of_measurement"] == "%"
    assert bat.attributes["adapter"] == "solarPanel"
    assert bat.attributes["updated_at"].startswith("2026-")
    assert hass.states.get("binary_sensor.giardino_charging").state == STATE_ON
