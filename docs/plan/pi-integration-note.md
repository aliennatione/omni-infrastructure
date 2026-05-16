# Pi Integration Note

## Cos'è Pi

[Pi](https://pi.dev/) (50K ★) è un coding agent CLI di Armin Ronacher (mitsuhiko).
Fornisce un'interfaccia unificata per hosted API (Anthropic, OpenAI, Google, Ollama...)
e modelli locali via **ds4.c** (antirez) — DeepSeek V4 Flash su Mac 128GB+ RAM.

## Modalità di integrazione possibili

### 1. Pi come provider LLM (via RPC)

Pi supporta `--mode rpc` — JSONL su stdin/stdout. Potremmo aggiungere un nuovo
provider type `pi_api` in inference.py che:
- Spawn `pi --mode rpc --provider <X> --model <Y>` come subprocess
- Invia `{"type": "prompt", "message": "..."}` su stdin
- Legge eventi da stdout, estrae `text_delta` chunks
- Supporta streaming nativo

**Pro**: streaming built-in, tool calling, session management
**Contro**: richiede Node.js/npm, overhead di un coding agent intero per fare inference
**Stato**: ⏳ Da valutare se utile

### 2. Pi come coding agent alternativo

Pi ha un SDK TypeScript (`@earendil-works/pi-coding-agent`) con `createAgentSession()`.
Potremmo usarlo come alternativa al nostro bridge per task complessi che richiedono
tool calling nativo (bash, file edit, grep).

**Pro**: tool calling robusto, session persistence, compaction automatica
**Contro**: TypeScript/Node.js, diverso dal nostro stack Python
**Stato**: ⏳ Da valutare

### 3. ds4.c come modello locale

[ds4.c](https://github.com/antirez/ds4) è l'inference engine di antirez per
DeepSeek V4 Flash su Mac con 128GB+ RAM. Espone un server API compatibile.

**Pro**: modello grande (MoE, sparse), contesto ampio, ottimizzato per Metal
**Contro**: richiede hardware specifico (Mac 128GB+), non disponibile per noi
**Stato**: ❌ Non fattibile con hardware attuale

## Decisione

Per ora **non integrare Pi**. Motivi:
1. ds4.c richiede hardware che non abbiamo (Mac 128GB+ RAM)
2. Pi come provider RPC aggiunge complessità (Node.js dependency) senza beneficio chiaro
3. Il nostro stack Python + inference.py copre già tutti i provider necessari

## Quando rivalutare

- Se otteniamo hardware compatibile con ds4.c
- Se Pi diventa un provider "standard" con API semplice (non subprocess)
- Se serve tool calling più sofisticato di quanto offrano i provider attuali

## Riferimenti

- [Blog post di Armin Ronacher](https://lucumr.pocoo.org/2026/5/8/local-models/)
- [pi-ds4 GitHub](https://github.com/mitsuhiko/pi-ds4)
- [ds4.c GitHub](https://github.com/antirez/ds4)
- [Pi RPC docs](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md)
