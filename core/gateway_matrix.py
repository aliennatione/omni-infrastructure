#!/usr/bin/env python3
"""NanoClaw Matrix Backend — Matrix.org messaging via matrix-nio."""

import os
import sys
import asyncio
from nio import AsyncClient, RoomMessageText, SyncResponse
from gateway_base import MessagingBackend


class MatrixBackend(MessagingBackend):
    """Matrix messaging backend using matrix-nio async client."""

    def __init__(self):
        self.homeserver = os.environ.get("MATRIX_HOMESERVER", "https://matrix.org")
        self.user = os.environ.get("MATRIX_USER", "")
        self.password = os.environ.get("MATRIX_PASSWORD", "")
        self.room_id = os.environ.get("MATRIX_ROOM_ID", "")
        self.device_id = os.environ.get("MATRIX_DEVICE_ID", "omni-agent")
        self.client = None
        self._loop = None
        self._seen_events = set()

        if not self.user or not self.password:
            print("[-] MATRIX_USER e MATRIX_PASSWORD non configurati.")
            sys.exit(1)

    def start(self):
        self._loop = asyncio.new_event_loop()
        self.client = AsyncClient(self.homeserver, self.user, device_id=self.device_id)
        login_result = self._loop.run_until_complete(
            self.client.login(self.password, device_name=self.device_id)
        )
        if hasattr(login_result, "error") and login_result.error:
            print(f"[-] Matrix login fallito: {login_result.error}")
            sys.exit(1)
        print(f"[+] Matrix connesso come {self.user}")
        if self.room_id:
            print(f"[*] Room: {self.room_id}")

    def poll(self):
        sync_result = self._loop.run_until_complete(
            self.client.sync(timeout=30000)
        )
        events = []

        if not isinstance(sync_result, SyncResponse):
            return events

        for room_id, room_info in sync_result.rooms.join.items():
            for event in room_info.timeline.events:
                if not isinstance(event, RoomMessageText):
                    continue
                if event.event_id in self._seen_events:
                    continue
                self._seen_events.add(event.event_id)

                if event.sender == self.user:
                    continue

                events.append((room_id, event.body))

        return events

    def send(self, room_id, text):
        self._loop.run_until_complete(
            self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": text}
            )
        )
