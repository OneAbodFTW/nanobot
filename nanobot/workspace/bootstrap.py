"""Seed workspace files from templates.

Goal: when running in a platform/container environment, the workspace directory
may start empty. Nanobot expects certain markdown files to exist at the workspace
root (see nanobot/agent/context.py). This module ensures those files exist by
copying from a template directory, without overwriting user changes.
"""

from __future__ import annotations

import os
from pathlib import Path


WORKSPACE_FILES: tuple[str, ...] = (
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "TOOLS.md",
    "IDENTITY.md",
    "HEARTBEAT.md",
)


def resolve_template_dir() -> Path | None:
    """Find a template directory that contains OpenClaw-style markdown files."""
    env_dir = os.environ.get("NANOBOT_WORKSPACE_TEMPLATE_DIR", "").strip()
    if env_dir:
        p = Path(env_dir).expanduser()
        if p.exists() and p.is_dir():
            return p

    # Default when baked into the Docker image (WORKDIR is /app)
    p = Path("/app/openclaw-identity")
    if p.exists() and p.is_dir():
        return p

    # Back-compat / dev: templates under repo ./workspace
    p = Path("/app/workspace")
    if p.exists() and p.is_dir():
        return p

    # Running from source
    p = Path.cwd() / "openclaw-identity"
    if p.exists() and p.is_dir():
        return p

    p = Path.cwd() / "workspace"
    if p.exists() and p.is_dir():
        return p

    return None


def _read_template(template_dir: Path, filename: str) -> str | None:
    try:
        p = template_dir / filename
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
            return content if content.strip() else None
    except Exception:
        return None
    return None


def seed_workspace(workspace: Path, template_dir: Path | None = None) -> list[str]:
    """Create workspace files if missing.

    - Never overwrites existing files.
    - Best-effort: failures won't raise.

    Returns list of created paths (relative to workspace).
    """
    created: list[str] = []
    try:
        workspace.mkdir(parents=True, exist_ok=True)
    except Exception:
        return created

    template_dir = template_dir if template_dir else resolve_template_dir()

    for filename in WORKSPACE_FILES:
        dst = workspace / filename
        if dst.exists():
            continue
        content = _read_template(template_dir, filename) if template_dir else None
        if content is None:
            # Minimal fallback; platform installs should provide templates.
            content = f"# {filename}\n"
        try:
            dst.write_text(content, encoding="utf-8")
            created.append(filename)
        except Exception:
            pass

    # Memory files (never overwrite)
    memory_dir = workspace / "memory"
    try:
        memory_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return created

    mem = memory_dir / "MEMORY.md"
    if not mem.exists():
        try:
            mem.write_text("# Long-term Memory\n\n", encoding="utf-8")
            created.append("memory/MEMORY.md")
        except Exception:
            pass

    hist = memory_dir / "HISTORY.md"
    if not hist.exists():
        try:
            hist.write_text("", encoding="utf-8")
            created.append("memory/HISTORY.md")
        except Exception:
            pass

    # Skills directory
    try:
        (workspace / "skills").mkdir(exist_ok=True)
    except Exception:
        pass

    return created
