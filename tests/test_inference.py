import os
import json
import responses
import pytest


class TestGoogleAPI:
    @responses.activate
    def test_google_api_success(self, router):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=test-key"
        responses.add(
            responses.POST, url,
            json={
                "candidates": [{
                    "content": {
                        "parts": [{"text": "Hello from Gemini"}],
                        "role": "model"
                    }
                }]
            },
            status=200
        )
        os.environ["GEMINI_API_KEY"] = "test-key"
        result = router.google_api(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "Say hello"
        )
        assert "result" in result
        assert result["result"] == "Hello from Gemini"
        del os.environ["GEMINI_API_KEY"]

    def test_google_api_missing_key(self, router):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        result = router.google_api("https://example.com", "test")
        assert "error" in result
        assert "GEMINI_API_KEY" in result["error"]

    @responses.activate
    def test_google_api_error(self, router):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=test-key"
        responses.add(responses.POST, url, json={"error": "Internal error"}, status=500)
        os.environ["GEMINI_API_KEY"] = "test-key"
        result = router.google_api(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "test"
        )
        assert "error" in result
        del os.environ["GEMINI_API_KEY"]


class TestOpenAICompat:
    @responses.activate
    def test_openai_compat_success(self, router):
        url = "http://localhost:8080/v1/chat/completions"
        responses.add(
            responses.POST, url,
            json={
                "choices": [{
                    "message": {"content": "Hello from local model"},
                    "finish_reason": "stop"
                }]
            },
            status=200
        )
        result = router.openai_compat("http://localhost:8080", "llama3", "Say hello")
        assert "result" in result
        assert result["result"] == "Hello from local model"

    @responses.activate
    def test_openai_compat_error(self, router):
        url = "http://localhost:8080/v1/chat/completions"
        responses.add(responses.POST, url, json={"error": "Model not found"}, status=404)
        result = router.openai_compat("http://localhost:8080", "unknown", "test")
        assert "error" in result

    def test_openai_compat_connection_refused_hint(self, router):
        result = router.openai_compat("http://127.0.0.1:1", "llama3", "test")
        assert "error" in result


class TestOpencodeAPI:
    @responses.activate
    def test_opencode_api_success(self, router):
        base = "http://localhost:4096"
        responses.add(
            responses.POST, f"{base}/session",
            json={"id": "sess-123"}, status=200
        )
        responses.add(
            responses.POST, f"{base}/session/sess-123/message",
            json={"parts": [{"type": "text", "text": "Hello from Opencode"}]},
            status=200
        )
        responses.add(
            responses.DELETE, f"{base}/session/sess-123",
            json={}, status=200
        )
        result = router.opencode_api(base, "Say hello")
        assert "result" in result
        assert result["result"] == "Hello from Opencode"

    @responses.activate
    def test_opencode_api_auth(self, router):
        base = "http://localhost:4096"
        os.environ["OPENCODE_SERVER_PASSWORD"] = "secret"
        os.environ["OPENCODE_SERVER_USERNAME"] = "admin"

        def check_auth(request):
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Basic ")
            return (200, {}, json.dumps({"id": "sess-1"}))

        responses.add_callback(responses.POST, f"{base}/session", callback=check_auth)
        responses.add(
            responses.POST, f"{base}/session/sess-1/message",
            json={"parts": [{"type": "text", "text": "ok"}]}, status=200
        )
        responses.add(responses.DELETE, f"{base}/session/sess-1", json={}, status=200)

        result = router.opencode_api(base, "test")
        assert "result" in result
        del os.environ["OPENCODE_SERVER_PASSWORD"]
        del os.environ["OPENCODE_SERVER_USERNAME"]

    def test_opencode_api_connection_refused(self, router):
        result = router.opencode_api("http://127.0.0.1:1", "test")
        assert "error" in result


class TestOpenhandsAPI:
    @responses.activate
    def test_openhands_api_success(self, router):
        base = "http://localhost:8000"
        responses.add(
            responses.POST, f"{base}/api/sessions",
            json={"session_id": "oh-123"}, status=200
        )
        responses.add(
            responses.POST, f"{base}/api/sessions/oh-123/messages",
            json={"content": "Hello from OpenHands"}, status=200
        )
        responses.add(
            responses.DELETE, f"{base}/api/sessions/oh-123",
            json={}, status=200
        )
        result = router.openhands_api(base, "Say hello")
        assert "result" in result
        assert result["result"] == "Hello from OpenHands"
        assert "session_id" in result

    def test_openhands_api_without_key(self, router):
        if "OPENHANDS_API_KEY" in os.environ:
            del os.environ["OPENHANDS_API_KEY"]
        base = "http://localhost:8000"
        with responses.mock as rsps:
            rsps.add(responses.POST, f"{base}/api/sessions", json={"session_id": "oh-1"}, status=200)
            rsps.add(responses.POST, f"{base}/api/sessions/oh-1/messages", json={"content": "ok"}, status=200)
            rsps.add(responses.DELETE, f"{base}/api/sessions/oh-1", json={}, status=200)
            result = router.openhands_api(base, "test")
            assert "result" in result

    def test_openhands_api_connection_refused(self, router):
        result = router.openhands_api("http://127.0.0.1:1", "test")
        assert "error" in result


class TestRouterRun:
    def test_provider_not_found(self, router):
        with pytest.raises(ValueError, match="non trovato"):
            router.run("nonexistent_provider", "test")

    def test_unsupported_provider_type(self, router):
        router.providers["bad"] = {"type": "unknown_type", "endpoint": "http://x", "model": "x"}
        with pytest.raises(NotImplementedError, match="non supportato"):
            router.run("bad", "test")

    @responses.activate
    def test_run_google_api(self, router):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=test-key"
        responses.add(
            responses.POST, url,
            json={
                "candidates": [{
                    "content": {"parts": [{"text": "4"}], "role": "model"}
                }]
            },
            status=200
        )
        os.environ["GEMINI_API_KEY"] = "test-key"
        result = router.run("google_flash", "What is 2+2?")
        assert result["result"] == "4"
        del os.environ["GEMINI_API_KEY"]

    @responses.activate
    def test_run_openai_compat(self, router):
        url = "http://localhost:8080/v1/chat/completions"
        responses.add(
            responses.POST, url,
            json={"choices": [{"message": {"content": "42"}}]},
            status=200
        )
        result = router.run("local_llamacpp", "What is the answer?")
        assert result["result"] == "42"


class TestStreaming:
    @responses.activate
    def test_stream_openai_compat(self, router):
        url = "http://localhost:8080/v1/chat/completions"
        sse_lines = [
            'data: {"choices": [{"delta": {"content": "Hel"}, "finish_reason": null}]}',
            'data: {"choices": [{"delta": {"content": "lo"}, "finish_reason": null}]}',
            'data: {"choices": [{"delta": {"content": " world"}, "finish_reason": null}]}',
            "data: [DONE]",
            "",
        ]
        responses.add(
            responses.POST, url,
            body="\n".join(sse_lines),
            status=200
        )
        chunks = list(router._stream_openai_compat("http://localhost:8080", "llama3", "Say hello"))
        assert chunks == ["Hel", "lo", " world"]

    def test_stream_google_api_missing_key(self, router):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        chunks = list(router._stream_google_api("https://example.com", "test"))
        assert len(chunks) == 1
        assert "GEMINI_API_KEY" in chunks[0]

    def test_stream_provider_not_found(self, router):
        with pytest.raises(ValueError, match="non trovato"):
            list(router.stream("nonexistent", "test"))

    def test_stream_unsupported_provider_type(self, router):
        router.providers["bad"] = {"type": "unknown_type", "endpoint": "http://x", "model": "x"}
        with pytest.raises(NotImplementedError, match="non supportato"):
            list(router.stream("bad", "test"))

    @responses.activate
    def test_stream_google_api_chunks(self, router):
        stream_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key=test-key"
        sse_data = [
            '{"candidates": [{"content": {"parts": [{"text": "First "}]}}]}',
            '{"candidates": [{"content": {"parts": [{"text": "chunk"}]}}]}',
        ]
        responses.add(
            responses.POST, stream_url,
            body="\n".join(sse_data),
            status=200
        )
        os.environ["GEMINI_API_KEY"] = "test-key"
        chunks = list(router._stream_google_api(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "test"
        ))
        assert "First " in chunks
        assert "chunk" in chunks
        del os.environ["GEMINI_API_KEY"]
