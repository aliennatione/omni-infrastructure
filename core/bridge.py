#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime
from inference import InferenceRouter
from doclingest import DocIngester


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
        self.ingester = DocIngester(state_dir, config_dir)
        self.config_dir = config_dir

    def resolve_event(self, event_type):
        route = self.matrix["routing_rules"].get(event_type)
        if not route:
            raise ValueError(f"Nessuna regola per l'evento '{event_type}'")
        return route

    def load_event_prompt(self, event_type):
        prompt_path = os.path.join(self.config_dir, "prompts", f"{event_type}.json")
        if os.path.exists(prompt_path):
            with open(prompt_path) as f:
                return json.load(f)
        return None

    def build_system_prompt(self, event_type, compact_mode):
        event_prompt = self.load_event_prompt(event_type)

        if compact_mode:
            if event_prompt:
                return (
                    f"{event_prompt['system_directive']} "
                    "RESPOND IN CAVEMAN MODE: drop filler words, use fragments, "
                    "keep substance, no pleasantries, be direct and terse. "
                    "Technical accuracy must remain 100%."
                )
            return (
                "You are an autonomous GitOps AI agent. "
                "RESPOND IN CAVEMAN MODE: drop filler words, use fragments, "
                "keep substance, no pleasantries, be direct and terse. "
                "Technical accuracy must remain 100%."
            )

        if event_prompt:
            behavior_lines = "\n".join(f"- {b}" for b in event_prompt.get("behavior", []))
            return (
                f"{event_prompt['system_directive']}\n\n"
                f"Behavior rules:\n{behavior_lines}"
            )

        return "You are an autonomous GitOps AI agent."

    def dispatch(self, event_type, payload, provider_override=None, stream=False):
        if provider_override:
            provider = provider_override
        else:
            route = self.resolve_event(event_type)
            provider = route["provider"]

        if provider == "doclingest":
            self._run_ingestion(payload)
            return

        if self.mode == "local":
            endpoint_override = os.environ.get("LLM_ENDPOINT_URL", "")
            if endpoint_override and provider in self.providers:
                self.providers = {**self.providers}
                self.providers[provider] = {**self.providers[provider], "endpoint": endpoint_override}
                print(f"[*] Endpoint sovrascritto: {endpoint_override}")

        print(f"[*] Routing task '{event_type}' a '{provider}' (mode={self.mode})...")

        context_path = os.path.join(self.state_dir, "CONTEXT.md")
        if os.path.exists(context_path):
            with open(context_path) as f:
                context_data = f.read()
        else:
            context_data = "Nessun contesto disponibile."

        compact_mode = os.environ.get("CAVEMAN_MODE", "")
        if compact_mode:
            context_data = self._compress_context(context_data)

        system_directive = self.build_system_prompt(event_type, bool(compact_mode))

        prompt = f"""
SYSTEM: {system_directive}
CONTEXT: {context_data}
TASK: {payload}
Execute the task modifying the code in {self.workspace_dir} if needed.
"""
        try:
            if stream:
                full_response = ""
                for chunk in self.router.stream(provider, prompt):
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print()
                result_text = full_response
            else:
                result = self.router.run(provider, prompt)
                result_text = str(result.get("result", ""))
                print("[+] Inferenza completata.")

            journal_dir = os.path.join(self.state_dir, "journal")
            os.makedirs(journal_dir, exist_ok=True)
            log_file = os.path.join(journal_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

            with open(log_file, "a") as lf:
                lf.write(f"\n--- {datetime.now().isoformat()} ---\nMode: {self.mode}\nTask: {payload}\nResult: {result_text[:500]}...\n")

        except Exception as e:
            print(f"[-] Errore: {e}")
            sys.exit(1)

    def _compress_context(self, text):
        lines = text.split("\n")
        compressed = []
        skip_next_blank = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if skip_next_blank:
                    continue
                skip_next_blank = True
                compressed.append("")
                continue
            skip_next_blank = False
            if stripped.startswith("# ") or stripped.startswith("## "):
                compressed.append(line)
            elif stripped.startswith("> ") or stripped.startswith("<!--"):
                continue
            elif stripped.startswith("- "):
                compressed.append(line)
            elif len(stripped) > 200:
                compressed.append(line[:200] + "...")
            else:
                compressed.append(line)
        return "\n".join(compressed)

    def _run_ingestion(self, payload):
        print(f"[*] Avvio documentazione ingestion...")
        try:
            if payload == "__all__":
                self.ingester.ingest_all()
            else:
                self.ingester.crawl_source({"name": payload, "url": payload, "crawl": True})
            self.ingester.rebuild_context()
            print("[+] Ingestion completata. CONTEXT.md aggiornato.")
        except Exception as e:
            print(f"[-] Errore durante ingestion: {e}")
            sys.exit(1)


def validate_dir(path, label):
    if not os.path.isdir(path):
        print(f"[-] Errore: {label} '{path}' non esiste o non è una directory.")
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
    parser.add_argument("--provider", default=None,
                        help="Provider LLM (es. local_llamacpp, google_gemini_flash). "
                             "Se omesso, usa matrix.json in base a --event")
    parser.add_argument("--list-providers", action="store_true",
                        help="Elenca i provider disponibili ed esce")
    parser.add_argument("--compact", action="store_true",
                        help="Modalità concisa (caveman): riduce token output del ~65%%")
    parser.add_argument("--stream", action="store_true",
                        help="Stampa tokens in real-time durante l'inferenza")
    args = parser.parse_args()

    if args.compact:
        os.environ["CAVEMAN_MODE"] = "1"

    if args.list_providers:
        providers_path = os.path.join(args.config, "providers.json")
        with open(providers_path) as f:
            providers = json.load(f)["providers"]
        print("Provider disponibili:")
        for name, cfg in providers.items():
            print(f"  {name:30s} type={cfg['type']:15s} endpoint={cfg['endpoint']}")
        sys.exit(0)

    validate_dir(args.state, "--state")
    validate_dir(args.workspace, "--workspace")
    validate_dir(args.config, "--config")

    bridge = OmniBridge(args.state, args.workspace, args.config, mode=args.mode)
    bridge.dispatch(args.event, args.payload, provider_override=args.provider, stream=args.stream)
