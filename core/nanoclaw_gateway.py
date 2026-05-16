#!/usr/bin/env python3
"""NanoClaw Gateway — Telegram backend for mobile interaction with Omni-Agent."""

import os
import sys
import argparse
import requests
from gateway_base import MessagingBackend, GatewayRunner


class TelegramBackend(MessagingBackend):
    """Telegram messaging backend using Bot API polling."""

    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0

    def start(self):
        pass

    def poll(self):
        resp = requests.get(
            f"{self.base_url}/getUpdates",
            params={"offset": self.offset, "timeout": 30},
            timeout=35
        )
        resp.raise_for_status()
        updates = resp.json().get("result", [])

        events = []
        for update in updates:
            self.offset = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue
            chat_id = str(message["chat"]["id"])
            text = message.get("text", "")
            if text:
                events.append((chat_id, text))

        return events

    def send(self, chat_id, text):
        requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NanoClaw Chat Gateway")
    parser.add_argument("--config", default="./config", help="Directory config")
    parser.add_argument("--state", default="../agent-state", help="Directory agent-state")
    parser.add_argument("--workspace", default="../project-source", help="Directory project-source")
    parser.add_argument("--test", help="Test mode: invia un messaggio e mostra la risposta")
    args = parser.parse_args()

    telegram_token = os.environ.get("TELEGRAM_TOKEN", "")
    if not telegram_token:
        print("[-] TELEGRAM_TOKEN non configurato. Imposta la variabile d'ambiente.")
        sys.exit(1)

    backend = TelegramBackend(telegram_token)
    runner = GatewayRunner(backend, args.config, args.state, args.workspace)

    if args.test:
        response = runner.call_bridge(args.test)
        print(response)
    else:
        runner.run()
