"""Home Assistant Bluetooth routing, including connectable ESPHome proxies."""

from __future__ import annotations

import asyncio

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import MODELS
from .lib.client import SessionError, SessionManager


def advertised_model(name: str | None, prefix: str) -> str | None:
    if not name or not name.startswith(prefix):
        return None
    return MODELS.get(name.rsplit("_", 1)[-1]) if "_" in name else None


def supported_name(name: str | None, prefix: str) -> bool:
    """A name match is model evidence, not authentication."""
    return advertised_model(name, prefix) is not None


def make_session(hass: HomeAssistant, address: str, prefix: str, model: str) -> SessionManager:
    async def connect():
        info = bluetooth.async_last_service_info(hass, address, connectable=True)
        device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
        if info is None or device is None:
            raise SessionError("No connectable Bluetooth advertisement for this toilet")
        if advertised_model(info.name, prefix) != model:
            raise SessionError("Unsupported advertised model")
        return await asyncio.wait_for(
            establish_connection(
                BleakClientWithServiceCache,
                device,
                "JOMOO BLE",
                max_attempts=2,
                disconnected_callback=lambda client: session.connection_lost(client),
                ble_device_callback=lambda: (
                    bluetooth.async_ble_device_from_address(hass, address, connectable=True)
                    or device
                ),
            ),
            timeout=90,
        )

    session = SessionManager(connect, model=model)
    return session
