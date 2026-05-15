import os
import base64
import requests


class InferenceRouter:
    def __init__(self, providers):
        self.providers = providers
        self.timeout = 600

    def run(self, provider_name, prompt):
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} non trovato nel config.")
        ptype = provider["type"]
        endpoint = provider["endpoint"]
        model = provider.get("model", "")

        if ptype == "google_api":
            return self.google_api(endpoint, prompt)
        elif ptype == "openai_compat":
            return self.openai_compat(endpoint, model, prompt)
        elif ptype == "opencode_api":
            return self.opencode_api(endpoint, prompt)
        else:
            raise NotImplementedError(f"Tipo provider {ptype} non supportato.")

    def google_api(self, endpoint, prompt):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return {"error": "GEMINI_API_KEY non configurata."}
        authenticated_url = f"{endpoint}?key={api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096
            }
        }
        try:
            response = requests.post(authenticated_url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            return {"error": f"Errore chiamata Google API: {e}"}

        response_json = response.json()
        try:
            ai_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            return {"result": ai_text}
        except (KeyError, IndexError):
            return {"error": "Impossibile decodificare la risposta di Google", "raw": response_json}

    def openai_compat(self, base_url, model, prompt):
        api_key = os.environ.get("LLM_API_KEY", "sk-no-key-required")
        url = f"{base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 4096
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            response_json = response.json()
            ai_text = response_json["choices"][0]["message"]["content"]
            return {"result": ai_text}
        except Exception as e:
            return {"error": f"Errore chiamata OpenAI-compat: {e}"}

    def opencode_api(self, base_url, prompt):
        password = os.environ.get("OPENCODE_SERVER_PASSWORD", "")
        username = os.environ.get("OPENCODE_SERVER_USERNAME", "opencode")
        base_url = base_url.rstrip("/")

        auth_headers = {}
        if password:
            token = base64.b64encode(f"{username}:{password}".encode()).decode()
            auth_headers["Authorization"] = f"Basic {token}"

        try:
            sess_resp = requests.post(f"{base_url}/session", headers=auth_headers, timeout=30)
            sess_resp.raise_for_status()
            session_id = sess_resp.json()["id"]

            payload = {
                "parts": [{"type": "text", "text": prompt}]
            }
            msg_resp = requests.post(
                f"{base_url}/session/{session_id}/message",
                json=payload,
                headers={**auth_headers, "Content-Type": "application/json"},
                timeout=self.timeout
            )
            msg_resp.raise_for_status()
            data = msg_resp.json()
            ai_text = ""
            for part in data.get("parts", []):
                if part.get("type") == "text":
                    ai_text += part.get("text", "")
            result = {"result": ai_text.strip()}
            try:
                requests.delete(f"{base_url}/session/{session_id}", headers=auth_headers, timeout=10)
            except Exception:
                pass
            return result
        except Exception as e:
            return {"error": f"Errore chiamata OpenCode API: {e}"}
