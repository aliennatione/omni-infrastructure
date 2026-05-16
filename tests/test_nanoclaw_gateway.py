import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock


class TestNanoClawHandleMessage:
    @patch("gateway_base.subprocess.run")
    def test_handle_message_success(self, mock_run):
        from nanoclaw_gateway import TelegramBackend
        from gateway_base import GatewayRunner
        mock_run.return_value = MagicMock(returncode=0, stdout="Bridge response", stderr="")

        backend = TelegramBackend("test-token")
        runner = GatewayRunner(backend, "./config", "/tmp/state", "/tmp/ws")
        response = runner.handle_message("Hello", "123")

        assert "Bridge response" in response
        mock_run.assert_called_once()

    @patch("gateway_base.subprocess.run")
    def test_handle_message_error(self, mock_run):
        from nanoclaw_gateway import TelegramBackend
        from gateway_base import GatewayRunner
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Something went wrong")

        backend = TelegramBackend("test-token")
        runner = GatewayRunner(backend, "./config", "/tmp/state", "/tmp/ws")
        response = runner.handle_message("Hello", "123")

        assert "Errore" in response

    @patch("gateway_base.subprocess.run")
    def test_call_bridge_builds_command(self, mock_run):
        from nanoclaw_gateway import TelegramBackend
        from gateway_base import GatewayRunner
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

        backend = TelegramBackend("test-token")
        runner = GatewayRunner(backend, "./config", "/tmp/state", "/tmp/ws")
        runner.call_bridge("test message", provider="local_llamacpp", mode="local")

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "core/bridge.py" in cmd
        assert "--event" in cmd
        assert "chat_message" in cmd
        assert "--payload" in cmd
        assert "test message" in cmd
        assert "--provider" in cmd
        assert "local_llamacpp" in cmd


class TestTelegramBackend:
    def test_backend_initializes(self):
        from nanoclaw_gateway import TelegramBackend
        backend = TelegramBackend("test-token")
        assert backend.token == "test-token"
        assert "test-token" in backend.base_url

    def test_backend_start_noop(self):
        from nanoclaw_gateway import TelegramBackend
        backend = TelegramBackend("test-token")
        backend.start()
