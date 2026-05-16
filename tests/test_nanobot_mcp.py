import os
import pytest
import tempfile
import shutil
import sqlite3


@pytest.fixture
def tmp_git_repo():
    repo = tempfile.mkdtemp()
    os.chdir(repo)
    os.system("git init -q")
    os.system("git config user.email 'test@test.com'")
    os.system("git config user.name 'Test'")
    test_file = os.path.join(repo, "test.txt")
    with open(test_file, "w") as f:
        f.write("hello\n")
    os.system("git add test.txt")
    os.system("git commit -m 'initial' -q")
    yield repo
    os.chdir("/data/workspace/omni-infrastructure")
    shutil.rmtree(repo, ignore_errors=True)


class TestNanobotGitTools:
    def test_git_status(self, tmp_git_repo):
        from nanobot_mcp import git_status
        result = git_status(repo_path=tmp_git_repo)
        assert not result.startswith("error")

    def test_git_log(self, tmp_git_repo):
        from nanobot_mcp import git_log
        result = git_log(repo_path=tmp_git_repo, n=1)
        assert not result.startswith("error")
        assert "initial" in result

    def test_git_diff_clean(self, tmp_git_repo):
        from nanobot_mcp import git_diff
        result = git_diff(repo_path=tmp_git_repo)
        assert not result.startswith("error")

    def test_git_diff_with_changes(self, tmp_git_repo):
        from nanobot_mcp import git_diff
        with open(os.path.join(tmp_git_repo, "test.txt"), "a") as f:
            f.write("new line\n")
        result = git_diff(repo_path=tmp_git_repo)
        assert not result.startswith("error")
        assert "new line" in result

    def test_git_status_not_a_repo(self, tmp_git_repo):
        from nanobot_mcp import git_status
        non_repo = tempfile.mkdtemp()
        try:
            result = git_status(repo_path=non_repo)
            assert result.startswith("error")
        finally:
            shutil.rmtree(non_repo, ignore_errors=True)


class TestNanobotFsTools:
    def test_fs_read(self, tmp_git_repo):
        from nanobot_mcp import fs_read
        result = fs_read(file_path=os.path.join(tmp_git_repo, "test.txt"))
        assert not result.startswith("error")
        assert "hello" in result

    def test_fs_read_nonexistent(self):
        from nanobot_mcp import fs_read
        result = fs_read(file_path="/nonexistent/file.txt")
        assert result.startswith("error")

    def test_fs_write_and_read(self, tmp_git_repo):
        from nanobot_mcp import fs_write, fs_read
        path = os.path.join(tmp_git_repo, "new.txt")
        write_result = fs_write(file_path=path, content="new content")
        assert write_result.startswith("ok")
        read_result = fs_read(file_path=path)
        assert "new content" in read_result

    def test_fs_list_dir(self, tmp_git_repo):
        from nanobot_mcp import fs_list_dir
        result = fs_list_dir(dir_path=tmp_git_repo)
        assert not result.startswith("error")
        assert "test.txt" in result

    def test_fs_list_dir_nonexistent(self):
        from nanobot_mcp import fs_list_dir
        result = fs_list_dir(dir_path="/nonexistent/dir")
        assert result.startswith("error")

    def test_fs_glob(self, tmp_git_repo):
        from nanobot_mcp import fs_glob
        result = fs_glob(pattern="*.txt", root=tmp_git_repo)
        assert not result.startswith("error")
        assert "test.txt" in result

    def test_fs_glob_no_matches(self, tmp_git_repo):
        from nanobot_mcp import fs_glob
        result = fs_glob(pattern="*.py", root=tmp_git_repo)
        assert not result.startswith("error")
        assert "no matches" in result


class TestNanobotDbTools:
    def test_db_query_create_and_select(self, tmp_git_repo):
        from nanobot_mcp import db_query
        db_path = os.path.join(tmp_git_repo, "test.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO items (name) VALUES ('test_item')")
        conn.commit()
        conn.close()

        result = db_query(db_path=db_path, query="SELECT * FROM items")
        assert not result.startswith("error")
        assert "test_item" in result

    def test_db_query_insert(self, tmp_git_repo):
        from nanobot_mcp import db_query
        db_path = os.path.join(tmp_git_repo, "test.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

        result = db_query(db_path=db_path, query="INSERT INTO items (name) VALUES ('new')")
        assert result.startswith("ok")

    def test_db_query_invalid(self):
        from nanobot_mcp import db_query
        result = db_query(db_path="/nonexistent/path.db", query="SELECT 1")
        assert result.startswith("error")
