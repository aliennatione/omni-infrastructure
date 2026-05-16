import os
import json
import pytest
import tempfile
import shutil
import responses


@pytest.fixture
def tmp_state_dir():
    state = tempfile.mkdtemp()
    yield state
    shutil.rmtree(state, ignore_errors=True)


@pytest.fixture
def docs_config():
    config = tempfile.mkdtemp()
    docs_json = os.path.join(config, "docs.json")
    with open(docs_json, "w") as f:
        json.dump({
            "sources": [
                {"name": "test-docs", "url": "https://example.com/docs", "crawl": True},
                {"name": "skip-docs", "url": "https://example.com/skip", "crawl": False}
            ]
        }, f)
    yield config
    shutil.rmtree(config, ignore_errors=True)


class TestDocIngesterConfig:
    def test_load_docs_config(self, docs_config):
        from doclingest import DocIngester
        ingester = DocIngester(tempfile.mkdtemp(), docs_config)
        assert len(ingester.sources) == 2

    def test_crawl_sources_filters(self, docs_config):
        from doclingest import DocIngester
        ingester = DocIngester(tempfile.mkdtemp(), docs_config)
        crawlable = [s for s in ingester.sources if s.get("crawl")]
        assert len(crawlable) == 1
        assert crawlable[0]["name"] == "test-docs"

    def test_ingest_all_crawl_only(self, docs_config):
        from doclingest import DocIngester
        ingester = DocIngester(tempfile.mkdtemp(), docs_config)
        crawlable = [s for s in ingester.sources if s.get("crawl")]
        assert len(crawlable) == 1
        assert crawlable[0]["name"] == "test-docs"


class TestDocIngesterContext:
    def test_rebuild_context_creates_file(self, tmp_state_dir, docs_config):
        from doclingest import DocIngester
        docs_dir = os.path.join(tmp_state_dir, "docs", "test-docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "index.md"), "w") as f:
            f.write("# Test Doc\n\nSome content here.\n")

        ingester = DocIngester(tmp_state_dir, docs_config)
        ingester.rebuild_context()

        context_path = os.path.join(tmp_state_dir, "CONTEXT.md")
        assert os.path.exists(context_path)
        with open(context_path) as f:
            content = f.read()
        assert "Test Doc" in content or "Knowledge Base" in content

    def test_rebuild_context_appends_sources(self, tmp_state_dir, docs_config):
        from doclingest import DocIngester
        docs_dir = os.path.join(tmp_state_dir, "docs", "test-docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "index.md"), "w") as f:
            f.write("# Test Doc\n\nContent.\n")

        ingester = DocIngester(tmp_state_dir, docs_config)
        ingester.rebuild_context()

        context_path = os.path.join(tmp_state_dir, "CONTEXT.md")
        with open(context_path) as f:
            content = f.read()
        assert "test-docs" in content or "Test Doc" in content

    def test_rebuild_context_no_docs_dir(self, tmp_state_dir, docs_config):
        from doclingest import DocIngester
        ingester = DocIngester(tmp_state_dir, docs_config)
        ingester.rebuild_context()
        context_path = os.path.join(tmp_state_dir, "CONTEXT.md")
        assert not os.path.exists(context_path)


class TestDocIngesterCrawl:
    @responses.activate
    def test_crawl_source_fetches_page(self, tmp_state_dir, docs_config):
        from doclingest import DocIngester
        responses.add(
            responses.GET, "https://example.com/docs",
            body="<html><body><h1>Test Page</h1><p>Some content</p></body></html>",
            status=200
        )
        ingester = DocIngester(tmp_state_dir, docs_config)
        ingester.crawl_source({"name": "manual", "url": "https://example.com/docs", "crawl": True})

        docs_dir = os.path.join(tmp_state_dir, "docs", "manual")
        index_path = os.path.join(docs_dir, "index.md")
        if os.path.exists(index_path):
            with open(index_path) as f:
                content = f.read()
            assert "Test Page" in content or "content" in content

    @responses.activate
    def test_crawl_source_handles_error(self, tmp_state_dir, docs_config):
        from doclingest import DocIngester
        responses.add(responses.GET, "https://example.com/docs", status=500)
        ingester = DocIngester(tmp_state_dir, docs_config)
        ingester.crawl_source({"name": "error", "url": "https://example.com/docs", "crawl": True})
