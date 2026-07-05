#!/usr/bin/env python3
"""Quiet Codex lifecycle hook entrypoint for codex-research-loop."""

from __future__ import annotations

from research_loop import lifecycle_main


if __name__ == "__main__":
    raise SystemExit(lifecycle_main())
