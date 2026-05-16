import os
import json
import pytest
import tempfile
import shutil


@pytest.fixture
def tmp_state_dir():
    state = tempfile.mkdtemp()
    os.makedirs(os.path.join(state, "journal"), exist_ok=True)
    with open(os.path.join(state, "CONTEXT.md"), "w") as f:
        f.write("# Project Context\n\nThis is a test context file.\n\n"
                "- Item one\n"
                "- Item two\n"
                "<!-- hidden comment -->\n"
                "> This is a blockquote that should be skipped\n\n"
                "A very long line that exceeds two hundred characters in length to test the truncation logic in the compress_context method "
                "which should truncate any line longer than 200 characters and add ellipsis at the end to indicate truncation occurred.\n")
    yield state
    shutil.rmtree(state, ignore_errors=True)


@pytest.fixture
def tmp_workspace_dir():
    ws = tempfile.mkdtemp()
    yield ws
    shutil.rmtree(ws, ignore_errors=True)


@pytest.fixture
def config_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


@pytest.fixture
def mock_providers():
    return {
        "google_flash": {
            "type": "google_api",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "model": "gemini-2.0-flash"
        },
        "local_llamacpp": {
            "type": "openai_compat",
            "endpoint": "http://localhost:8080",
            "model": "llama3"
        },
        "local_opencode": {
            "type": "opencode_api",
            "endpoint": "http://localhost:4096",
        },
        "local_openhands": {
            "type": "openhands_api",
            "endpoint": "http://localhost:8000",
        },
    }


@pytest.fixture
def router(mock_providers):
    from inference import InferenceRouter
    return InferenceRouter(mock_providers)


@pytest.fixture
def bridge(tmp_state_dir, tmp_workspace_dir, config_dir):
    from bridge import OmniBridge
    return OmniBridge(tmp_state_dir, tmp_workspace_dir, config_dir)
