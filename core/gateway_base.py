#!/usr/bin/env python3
"""NanoClaw Gateway Base — Abstract messaging backend + gateway runner."""

import os
import sys
import subprocess
from abc import ABC, abstractmethod
from typing import List, Tuple


class MessagingBackend(ABC):
    """Abstract base for chat platform backends (Telegram, Matrix, etc.)."""

    @abstractmethod
    def start(self):
        """Initialize connection to the chat platform."""
        pass

    @abstractmethod
    def poll(self) -> List[Tuple[str, str]]:
        """Return list of (chat_id, text) tuples from new messages."""
        pass

    @abstractmethod
    def send(self, chat_id, text):
        """Send text response to the given chat_id."""
        pass


class GatewayRunner:
    """Main loop: poll backend, route messages through bridge, send replies."""

    def __init__(self, backend, config_dir, state_dir, workspace_dir):
        self.backend = backend
        self.config_dir = config_dir
        self.state_dir = state_dir
        self.workspace_dir = workspace_dir
        self.default_provider = os.environ.get("NANOCLAW_PROVIDER", "local_openhands")
        self.default_mode = os.environ.get("NANOCLAW_MODE", "local")

    def call_bridge(self, message, provider=None, mode=None):
        provider = provider or self.default_provider
        mode = mode or self.default_mode

        cmd = [
            sys.executable, "core/bridge.py",
            "--state", self.state_dir,
            "--workspace", self.workspace_dir,
            "--config", self.config_dir,
            "--event", "chat_message",
            "--payload", message,
            "--mode", mode,
            "--provider", provider,
        ]

        env = os.environ.copy()
        env["PYTHONPATH"] = "./core"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=600
        )

        if result.returncode != 0:
            return f"Errore: {result.stderr.strip()}"

        return result.stdout.strip()

    def handle_message(self, text, chat_id):
        print(f"[*] Messaggio da chat_id={chat_id}: {text[:100]}...")
        response = self.call_bridge(text)
        print(f"[+] Risposta per chat_id={chat_id}: {response[:200]}...")
        return response

    def run(self):
        self.backend.start()
        print(f"[*] NanoClaw Gateway avviato. Backend: {self.backend.__class__.__name__}")

        while True:
            try:
                events = self.backend.poll()
                for chat_id, text in events:
                    if not text:
                        continue
                    response = self.handle_message(text, chat_id)
                    self.backend.send(chat_id, response[:4096])
            except KeyboardInterrupt:
                print("\n[*] NanoClaw Gateway arrestato.")
                break
            except Exception as e:
                print(f"[-] Errore: {e}")
                import time
                time.sleep(5)
