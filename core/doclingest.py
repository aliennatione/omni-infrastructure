import os
import sys
import json
import hashlib
from datetime import datetime


class DocIngester:
    def __init__(self, state_dir, config_dir):
        self.state_dir = os.path.abspath(state_dir)
        self.docs_db_path = os.path.join(self.state_dir, "docs-index.json")

        sources_path = os.path.join(config_dir, "docs.json")
        if os.path.exists(sources_path):
            with open(sources_path) as f:
                self.sources = json.load(f).get("sources", [])
        else:
            self.sources = []

    def fetch_url(self, url):
        try:
            import trafilatura
        except ImportError:
            print("[-] trafilatura non installato. Esegui: pip install trafilatura")
            sys.exit(1)

        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None

        markdown = trafilatura.extract(downloaded, output_format="markdown", include_links=True, include_images=False)
        return markdown

    def crawl_source(self, source):
        url = source.get("url", "")
        name = source.get("name", url)
        output_dir = os.path.join(self.state_dir, "docs", self._slugify(name))
        os.makedirs(output_dir, exist_ok=True)

        print(f"[*] Crawling '{name}' → {url}")

        try:
            import trafilatura
        except ImportError:
            print("[-] trafilatura non installato.")
            return

        if source.get("crawl", False):
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                print(f"[-] Impossibile scaricare {url}")
                return
            markdown = trafilatura.extract(
                downloaded, output_format="markdown", include_links=True, include_images=False,
                no_fallback=False
            )
            if markdown:
                filepath = os.path.join(output_dir, "index.md")
                with open(filepath, "w") as f:
                    f.write(f"# {name}\n\n> Fonte: {url}\n> Crawlato: {datetime.now().isoformat()}\n\n{markdown}")
                print(f"[+] Salvato: {filepath}")
        else:
            pages = source.get("pages", [url])
            for page_url in pages:
                slug = self._slugify(page_url)
                downloaded = trafilatura.fetch_url(page_url)
                if not downloaded:
                    print(f"[-] Impossibile scaricare {page_url}")
                    continue
                markdown = trafilatura.extract(
                    downloaded, output_format="markdown", include_links=True, include_images=False,
                    no_fallback=False
                )
                if markdown:
                    filepath = os.path.join(output_dir, f"{slug}.md")
                    with open(filepath, "w") as f:
                        f.write(f"> Fonte: {page_url}\n> Crawlato: {datetime.now().isoformat()}\n\n{markdown}")
                    print(f"[+] Salvato: {filepath}")

        self._update_index(name, url, output_dir)

    def _slugify(self, text):
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in text)
        return safe.strip("_").lower()[:64] or "page"

    def _update_index(self, name, url, path):
        entry = {
            "name": name,
            "url": url,
            "path": path,
            "crawled_at": datetime.now().isoformat(),
            "pages": []
        }
        for fname in sorted(os.listdir(path)):
            if fname.endswith(".md"):
                fpath = os.path.join(path, fname)
                with open(fpath) as f:
                    content = f.read()
                entry["pages"].append({
                    "file": fname,
                    "size": len(content),
                    "hash": hashlib.md5(content.encode()).hexdigest()
                })

        if os.path.exists(self.docs_db_path):
            with open(self.docs_db_path) as f:
                index = json.load(f)
        else:
            index = []

        index = [e for e in index if e["name"] != name]
        index.append(entry)

        with open(self.docs_db_path, "w") as f:
            json.dump(index, f, indent=2)
        print(f"[+] Indice aggiornato: {self.docs_db_path}")

    def list_crawled(self):
        if not os.path.exists(self.docs_db_path):
            print("[*] Nessun documento crawlato.")
            return
        with open(self.docs_db_path) as f:
            index = json.load(f)
        print(f"[*] Documenti crawlati ({len(index)} fonti):")
        for entry in index:
            print(f"  - {entry['name']} ({len(entry['pages'])} pagine, {entry['url']})")

    def ingest_all(self):
        if not self.sources:
            print("[-] Nessuna fonte configurata in config/docs.json")
            return
        for source in self.sources:
            self.crawl_source(source)

    def rebuild_context(self):
        docs_dir = os.path.join(self.state_dir, "docs")
        if not os.path.isdir(docs_dir):
            print("[-] Nessun documento in state/docs/")
            return

        context_path = os.path.join(self.state_dir, "CONTEXT.md")
        header = "# Knowledge Base — Documentazione Crawlata\n\n"
        body_parts = []

        for root, dirs, files in os.walk(docs_dir):
            for fname in sorted(files):
                if fname.endswith(".md"):
                    fpath = os.path.join(root, fname)
                    rel = os.path.relpath(fpath, self.state_dir)
                    with open(fpath) as f:
                        content = f.read()
                    body_parts.append(f"## {rel}\n\n{content}\n")

        full = header + "\n".join(body_parts)

        if os.path.exists(context_path):
            with open(context_path) as f:
                existing = f.read()
            full = existing + "\n\n---\n\n" + header + "\n".join(body_parts)

        with open(context_path, "w") as f:
            f.write(full)
        print(f"[+] CONTEXT.md aggiornato con {len(body_parts)} documenti.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Omni-Agent Documentation Ingestion")
    parser.add_argument("--state", required=True, help="Directory agent-state")
    parser.add_argument("--config", required=True, help="Directory config")
    parser.add_argument("--action", choices=["crawl", "list", "rebuild-context"], default="crawl",
                        help="Azione da eseguire")
    parser.add_argument("--source", default="", help="Nome della fonte da crawlare (opzionale)")
    args = parser.parse_args()

    ingester = DocIngester(args.state, args.config)

    if args.action == "list":
        ingester.list_crawled()
    elif args.action == "rebuild-context":
        ingester.rebuild_context()
    else:
        if args.source:
            for s in ingester.sources:
                if s.get("name") == args.source:
                    ingester.crawl_source(s)
                    break
            else:
                print(f"[-] Fonte '{args.source}' non trovata in config/docs.json")
        else:
            ingester.ingest_all()


if __name__ == "__main__":
    main()
