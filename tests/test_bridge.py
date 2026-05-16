import os
import pytest


class TestResolveEvent:
    def test_resolve_event_valid(self, bridge):
        route = bridge.resolve_event("small_fix")
        assert route["provider"] == "google_gemini_flash"

    def test_resolve_event_git_automation(self, bridge):
        route = bridge.resolve_event("git_automation")
        assert route["provider"] == "google_gemini_flash"

    def test_resolve_event_software_refactor(self, bridge):
        route = bridge.resolve_event("software_refactor")
        assert route["provider"] == "google_gemini_pro"

    def test_resolve_event_invalid_raises(self, bridge):
        with pytest.raises(ValueError, match="Nessuna regola"):
            bridge.resolve_event("nonexistent_event")


class TestLoadEventPrompt:
    def test_load_event_prompt_exists(self, bridge, config_dir):
        prompt = bridge.load_event_prompt("small_fix")
        assert prompt is not None
        assert "system_directive" in prompt
        assert "behavior" in prompt
        assert "output_format" in prompt

    def test_load_event_prompt_missing(self, bridge):
        prompt = bridge.load_event_prompt("nonexistent_event")
        assert prompt is None

    def test_load_event_prompt_git_automation(self, bridge):
        prompt = bridge.load_event_prompt("git_automation")
        assert prompt is not None
        assert "git" in prompt["system_directive"].lower()

    def test_load_event_prompt_software_refactor(self, bridge):
        prompt = bridge.load_event_prompt("software_refactor")
        assert prompt is not None
        assert "refactor" in prompt["system_directive"].lower()


class TestBuildSystemPrompt:
    def test_build_system_prompt_with_event(self, bridge):
        prompt = bridge.build_system_prompt("small_fix", False)
        assert "small fixes" in prompt.lower() or "minor" in prompt.lower()
        assert "Behavior rules:" in prompt

    def test_build_system_prompt_without_event(self, bridge):
        prompt = bridge.build_system_prompt("nonexistent", False)
        assert prompt == "You are an autonomous GitOps AI agent."

    def test_build_system_prompt_compact_with_event(self, bridge):
        prompt = bridge.build_system_prompt("small_fix", True)
        assert "CAVEMAN MODE" in prompt
        assert "drop filler words" in prompt

    def test_build_system_prompt_compact_without_event(self, bridge):
        prompt = bridge.build_system_prompt("nonexistent", True)
        assert "CAVEMAN MODE" in prompt
        assert "autonomous GitOps AI agent" in prompt

    def test_build_system_prompt_includes_behavior(self, bridge):
        prompt = bridge.build_system_prompt("git_automation", False)
        assert "conventional commit" in prompt.lower() or "commit" in prompt.lower()

    def test_build_system_prompt_chat_message(self, bridge):
        prompt = bridge.build_system_prompt("chat_message", False)
        assert "chat" in prompt.lower() or "mobile" in prompt.lower()


class TestCompressContext:
    def test_compress_context_truncate_long_lines(self, bridge):
        long_line = "x" * 300
        result = bridge._compress_context(long_line)
        assert len(result) <= 203
        assert result.endswith("...")

    def test_compress_context_skip_html_comments(self, bridge):
        text = "visible\n<!-- hidden -->\nalso visible"
        result = bridge._compress_context(text)
        assert "visible" in result
        assert "hidden" not in result
        assert "also visible" in result

    def test_compress_context_skip_blockquotes(self, bridge):
        text = "normal\n> blockquote\nnormal2"
        result = bridge._compress_context(text)
        assert "normal" in result
        assert "blockquote" not in result
        assert "normal2" in result

    def test_compress_context_deduplicate_blanks(self, bridge):
        text = "line1\n\n\n\nline2"
        result = bridge._compress_context(text)
        assert result.count("\n\n") <= 1

    def test_compress_context_preserves_headings(self, bridge):
        text = "# Heading\n## Subheading\nlong content here"
        result = bridge._compress_context(text)
        assert "# Heading" in result
        assert "## Subheading" in result

    def test_compress_context_preserves_list_items(self, bridge):
        text = "- item one\n- item two"
        result = bridge._compress_context(text)
        assert "- item one" in result
        assert "- item two" in result

    def test_compress_context_empty_input(self, bridge):
        result = bridge._compress_context("")
        assert result == ""

    def test_compress_context_short_lines_unchanged(self, bridge):
        text = "short line\nanother short line"
        result = bridge._compress_context(text)
        assert result == text
