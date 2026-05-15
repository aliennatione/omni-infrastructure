#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime
from inference import InferenceRouter


class OmniBridge:
    def __init__(self, state_dir, workspace_dir, config_dir, mode="cloud"):
        self.state_dir = os.path.abspath(state_dir)
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.mode = mode

        with open(os.path.join(config_dir, "matrix.json")) as f:
            self.matrix = json.load(f)
        with open(os.path.join(config_dir, "providers.json")) as f:
            self.providers = json.load(f)["providers"]
        self.router = InferenceRouter(self.providers)

    def resolve_event(self, event_type):
        route = self.matrix["routing_rules"].get(event_type)
        if not route:
            print(f"Errore: Nessuna regola per l'evento '{event_type}'")
            sys.exit(1)
        return route

    def dispatch(self, event_type, payload):
        route = self.resolve_event(event_type)
        provider = route["provider"]

        if self.mode == "local":
            override = os.environ.get("LLM_PROVIDER", "")
            if override:
                provider = override
                print(f"[*] Modalità locale: forzatura provider a '{provider}'")
            endpoint_override = os.environ.get("LLM_ENDPOINT_URL", "")
            if endpoint_override:
                if provider in self.providers:
                    self.providers[provider]["endpoint"] = endpoint_override
                    print(f"[*] Endpoint sovrascritto: {endpoint_override}")

        print(f"[*] Routing task '{event_type}' a '{provider}' (mode={self.mode})...")

        context_path = os.path.join(self.state_dir, "CONTEXT.md")
        context_data = open(context_path).read() if os.path.exists(context_path) else "Nessun contesto disponibile."

        prompt = f"""
SYSTEM: You are an autonomous GitOps AI agent.
CONTEXT: {context_data}
TASK: {payload}
Execute the task modifying the code in {self.workspace_dir} if needed.
"""
        try:
            result = self.router.run(provider, prompt)
            print("[+] Inferenza completata.")

            journal_dir = os.path.join(self.state_dir, "journal")
            os.makedirs(journal_dir, exist_ok=True)
            log_file = os.path.join(journal_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

            with open(log_file, "a") as lf:
                lf.write(f"\n--- {datetime.now().isoformat()} ---\nMode: {self.mode}\nTask: {payload}\nResult: {str(result.get('result'))[:500]}...\n")

        except Exception as e:
            print(f"[-] Errore: {e}")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omni-Agent Bridge")
    parser.add_argument("--state", required=True, help="Percorso alla directory agent-state")
    parser.add_argument("--workspace", required=True, help="Percorso alla directory project-source")
    parser.add_argument("--config", required=True, help="Percorso alla directory config")
    parser.add_argument("--event", required=True, help="Tipo di evento (routing key)")
    parser.add_argument("--payload", required=True, help="Testo del task da eseguire")
    parser.add_argument("--mode", choices=["cloud", "local"], default=os.environ.get("LLM_MODE", "cloud"),
                        help="Modalità di esecuzione: cloud (default) o local")
    args = parser.parse_args()

    bridge = OmniBridge(args.state, args.workspace, args.config, mode=args.mode)
    bridge.dispatch(args.event, args.payload)
