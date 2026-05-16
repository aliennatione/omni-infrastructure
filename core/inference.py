import os
import json
import base64
import requests


PROVIDER_HINTS = {
    "local_llamacpp": "make up-llamacpp",
    "local_localai": "make up-localai",
    "local_ollama": "make up-ollama",
    "local_opencode": "opencode serve",
    "local_openhands": "openhands start",
}


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
        elif ptype == "openhands_api":
            return self.openhands_api(endpoint, prompt)
        else:
            raise NotImplementedError(f"Tipo provider {ptype} non supportato.")

    def _hint(self, provider_name, err):
        err_str = str(err).lower()
        if "connection refused" in err_str or "connection refused" in err_str or "111" in err_str or "connect" in err_str:
            hint = PROVIDER_HINTS.get(provider_name)
            extra = ""
            if hint:
                extra = f"\n    Suggerimento: {hint}"
            return {"error": f"Provider '{provider_name}': impossibile connettersi.{extra}"}
        return {"error": f"Provider '{provider_name}': {err}"}

    def google_api(self, endpoint, prompt):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return {"error": "GEMINI_API_KEY non configurata."}
        authenticated_url = f"{endpoint}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096}
        }
        try:
            response = requests.post(authenticated_url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            return self._hint("google_gemini_pro", e)
        response_json = response.json()
        try:
            ai_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            return {"result": ai_text}
        except (KeyError, IndexError):
            return {"error": "Impossibile decodificare la risposta di Google", "raw": response_json}

    def openai_compat(self, base_url, model, prompt):
        api_key = os.environ.get("LLM_API_KEY", "sk-no-key-required")
        url = f"{base_url.rstrip('/')}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
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
            return self._hint(None, e)

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
            payload = {"parts": [{"type": "text", "text": prompt}]}
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
            return self._hint("local_opencode", e)

    def openhands_api(self, base_url, prompt):
        api_key = os.environ.get("OPENHANDS_API_KEY", "")
        base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            sess_resp = requests.post(
                f"{base_url}/api/sessions",
                json={"name": "omni-agent-session"},
                headers=headers,
                timeout=30
            )
            sess_resp.raise_for_status()
            session_id = sess_resp.json()["session_id"]
            payload = {"message": prompt, "reset": True}
            msg_resp = requests.post(
                f"{base_url}/api/sessions/{session_id}/messages",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            msg_resp.raise_for_status()
            data = msg_resp.json()
            ai_text = data.get("content", "")
            if isinstance(ai_text, list):
                ai_text = " ".join(
                    part.get("text", "") for part in ai_text if isinstance(part, dict) and part.get("text")
                )
            result = {"result": ai_text.strip(), "session_id": session_id}
            try:
                requests.delete(f"{base_url}/api/sessions/{session_id}", headers=headers, timeout=10)
            except Exception:
                pass
            return result
        except Exception as e:
            return self._hint("local_openhands", e)

    def stream(self, provider_name, prompt):
        """Yield text chunks as they arrive from the LLM."""
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} non trovato nel config.")
        ptype = provider["type"]
        endpoint = provider["endpoint"]
        model = provider.get("model", "")

        if ptype == "google_api":
            yield from self._stream_google_api(endpoint, prompt)
        elif ptype == "openai_compat":
            yield from self._stream_openai_compat(endpoint, model, prompt)
        elif ptype == "opencode_api":
            result = self.opencode_api(endpoint, prompt)
            text = result.get("result", "")
            if text:
                yield text
        elif ptype == "openhands_api":
            result = self.openhands_api(endpoint, prompt)
            text = result.get("result", "")
            if text:
                yield text
        else:
            raise NotImplementedError(f"Tipo provider {ptype} non supportato per lo streaming.")

    def _stream_google_api(self, endpoint, prompt):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            yield "GEMINI_API_KEY non configurata."
            return
        stream_url = endpoint.replace(":generateContent", ":streamGenerateContent")
        authenticated_url = f"{stream_url}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096}
        }
        try:
            response = requests.post(authenticated_url, json=payload, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    candidates = chunk.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text", "")
                            if text:
                                yield text
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
        except Exception as e:
            yield f"Errore streaming: {e}"

    def _stream_openai_compat(self, base_url, model, prompt):
        api_key = os.environ.get("LLM_API_KEY", "sk-no-key-required")
        url = f"{base_url.rstrip('/')}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 4096,
            "stream": True
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                if not decoded.startswith("data: "):
                    continue
                data_str = decoded[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception as e:
            yield f"Errore streaming: {e}"
