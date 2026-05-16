#!/usr/bin/env python3
"""Nanobot MCP Server — git, filesystem, and database tools for AI agents."""

import os
import sys
import json
import sqlite3
import subprocess
import argparse
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("[-] mcp package not installed. Run: pip install mcp")
    sys.exit(1)


mcp = FastMCP("Nanobot")


def _run_git(args, cwd=None):
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd()
    )
    if result.returncode != 0:
        return f"error: {result.stderr.strip()}"
    return result.stdout.strip()


@mcp.tool()
def git_status(repo_path: str = ".") -> str:
    """Show the working tree status."""
    return _run_git(["status", "--short"], cwd=repo_path)


@mcp.tool()
def git_diff(repo_path: str = ".", target: str = "") -> str:
    """Show changes between commits, or working tree and index."""
    args = ["diff"]
    if target:
        args.append(target)
    return _run_git(args, cwd=repo_path)


@mcp.tool()
def git_log(repo_path: str = ".", n: int = 10) -> str:
    """Show commit logs."""
    return _run_git(["log", f"--oneline", f"-{n}"], cwd=repo_path)


@mcp.tool()
def git_commit(repo_path: str = ".", message: str = "") -> str:
    """Record changes to the repository."""
    if not message:
        return "error: message is required"
    return _run_git(["commit", "-m", message], cwd=repo_path)


@mcp.tool()
def git_branch_create(repo_path: str = ".", branch_name: str = "") -> str:
    """Create a new branch."""
    if not branch_name:
        return "error: branch_name is required"
    return _run_git(["branch", branch_name], cwd=repo_path)


@mcp.tool()
def git_push(repo_path: str = ".", remote: str = "origin", branch: str = "") -> str:
    """Update remote refs along with associated objects."""
    if not branch:
        current = _run_git(["branch", "--show-current"], cwd=repo_path)
        if current.startswith("error:"):
            return current
        branch = current
    return _run_git(["push", remote, branch], cwd=repo_path)


@mcp.tool()
def fs_read(file_path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def fs_write(file_path: str, content: str) -> str:
    """Write content to a file."""
    try:
        parent = Path(file_path).parent
        parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return f"ok: wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def fs_list_dir(dir_path: str = ".") -> str:
    """List contents of a directory."""
    try:
        entries = os.listdir(dir_path)
        lines = []
        for entry in sorted(entries):
            full = os.path.join(dir_path, entry)
            prefix = "d" if os.path.isdir(full) else "f"
            lines.append(f"{prefix} {entry}")
        return "\n".join(lines)
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def fs_glob(pattern: str, root: str = ".") -> str:
    """Find files matching a glob pattern."""
    try:
        import glob as globmod
        matches = globmod.glob(os.path.join(root, pattern), recursive=True)
        return "\n".join(sorted(matches)) if matches else "no matches"
    except Exception as e:
        return f"error: {e}"


@mcp.tool()
def db_query(db_path: str, query: str) -> str:
    """Execute a SQL query against a SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(query)
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [",".join(columns)]
            for row in rows:
                result.append(",".join(str(v) for v in row))
            conn.close()
            return "\n".join(result) if result else "empty result"
        else:
            conn.commit()
            conn.close()
            return f"ok: {cursor.rowcount} rows affected"
    except Exception as e:
        return f"error: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nanobot MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--port", type=int, default=4097)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    print(f"[*] Starting Nanobot MCP server on {args.transport}...")
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
