#!/usr/bin/env python3
"""NanoClaw Gateway — Telegram/Signal chat gateway for mobile interaction with Omni-Agent."""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path


class NanoClawGateway:
    def __init__(self, config_dir, state_dir, workspace_dir):
        self.config_dir = config_dir
        self.state_dir = state_dir
        self.workspace_dir = workspace_dir
        self.telegram_token = os.environ.get("TELEGRAM_TOKEN", "")
        self.default_provider = os.environ.get("NANOCLAW_PROVIDER", "local_openhands")
        self.default_mode = os.environ.get("NANOCLAW_MODE", "local")

        if not self.telegram_token:
            print("[-] TELEGRAM_TOKEN non configurato. Imposta la variabile d'ambiente.")
            sys.exit(1)

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

    def handle_message(self, user_message, chat_id):
        print(f"[*] Messaggio da chat_id={chat_id}: {user_message[:100]}...")
        response = self.call_bridge(user_message)
        print(f"[+] Risposta per chat_id={chat_id}: {response[:200]}...")
        return response

    def run_polling(self):
        try:
            import requests
        except ImportError:
            print("[-] requests non installato. Run: pip install requests")
            sys.exit(1)

        base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        offset = 0

        print(f"[*] NanoClaw Gateway avviato. In ascolto messaggi Telegram...")

        while True:
            try:
                resp = requests.get(
                    f"{base_url}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                    timeout=35
                )
                resp.raise_for_status()
                updates = resp.json().get("result", [])

                for update in updates:
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if not message:
                        continue

                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")

                    if not text:
                        continue

                    response = self.handle_message(text, chat_id)

                    requests.post(
                        f"{base_url}/sendMessage",
                        json={"chat_id": chat_id, "text": response[:4096]},
                        timeout=10
                    )

            except KeyboardInterrupt:
                print("\n[*] NanoClaw Gateway arrestato.")
                break
            except Exception as e:
                print(f"[-] Errore: {e}")
                import time
                time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NanoClaw Chat Gateway")
    parser.add_argument("--config", default="./config", help="Directory config")
    parser.add_argument("--state", default="../agent-state", help="Directory agent-state")
    parser.add_argument("--workspace", default="../project-source", help="Directory project-source")
    parser.add_argument("--test", help="Test mode: invia un messaggio e mostra la risposta")
    args = parser.parse_args()

    gateway = NanoClawGateway(args.config, args.state, args.workspace)

    if args.test:
        response = gateway.handle_message(args.test, "test")
        print(response)
    else:
        gateway.run_polling()
