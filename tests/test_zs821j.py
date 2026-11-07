"""Synthetic ZS821J status burst through the same BLE session used by HA."""

import unittest

from jomoo_ble.client import CommandRefused, Mechanical, SessionManager
from jomoo_ble.protocol import (
    DEVICE,
    STATE,
    WORK,
    LID_RING,
    ZS800J,
    ZS821J,
    ProtocolError,
    build_frame,
    parse_frame,
    state_query,
    validate_status,
)


class StatusClient:
    is_connected = True

    def __init__(self):
        self.requests = []

    async def start_notify(self, characteristic, callback):
        self.notify = callback

    async def write_gatt_char(self, characteristic, data, response):
        self.requests.append(data)
        frames = [
            build_frame(cmd, bytes.fromhex(payload), DEVICE, 0x92)
            for cmd, payload in (
                (STATE, "3650b435000000"),
                (LID_RING, "09000000000000"),
                (WORK, "80000001000000"),
            )
        ]
        burst = b"".join(frames)
        self.notify(None, bytearray(burst[:4]))
        self.notify(None, bytearray(burst[4:]))

    async def disconnect(self):
        self.is_connected = False


class ProfileTests(unittest.IsolatedAsyncioTestCase):
    async def test_status_session(self):
        device = StatusClient()

        async def connect():
            return device

        session = SessionManager(connect, settle_time=0, model=ZS821J)
        with self.assertRaises(CommandRefused):
            await session.command(Mechanical.OPEN_LID)
        snap = await session.poll()
        self.assertEqual(device.requests, [state_query()])
        self.assertTrue(snap.mechanism.lid_open)
        self.assertFalse(snap.mechanism.ring_open)
        self.assertTrue(snap.runtime.seated)
        self.assertTrue(snap.runtime.standby)
        self.assertEqual(
            (
                snap.settings.water_temperature,
                snap.settings.seat_temperature,
                snap.settings.air_temperature,
            ),
            (3, 0, 4),
        )
        self.assertFalse(snap.settings.auto_cover)
        self.assertTrue(snap.settings.auto_flush)
        self.assertFalse(device.is_connected)

    def test_profiles_reject_other_model_lengths(self):
        for cmd, old_len in ((LID_RING, 13), (WORK, 6)):
            for model, wrong_length in ((ZS821J, old_len), (ZS800J, 7)):
                frame = parse_frame(build_frame(cmd, bytes(wrong_length), DEVICE, 0x92))
                with self.assertRaises(ProtocolError):
                    validate_status(frame, model)
