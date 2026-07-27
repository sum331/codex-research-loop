#!/usr/bin/env python3
"""Project-local research loop runtime for Codex.

This script is intentionally dependency-free. It records durable research
state under .research-loop/ so a future Codex thread can resume without relying
on a long conversation transcript.
"""

from __future__ import annotations

import argparse
import ctypes
import csv
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import mimetypes
import os
import re
import signal
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOOP_DIR = ".research-loop"
SCHEMA_VERSION = "0.9.2"
PAYLOAD_LIMIT = 24000
INVENTORY_LIMIT = int(os.environ.get("RESEARCH_LOOP_INVENTORY_LIMIT", "1200"))
INVENTORY_SECONDS = float(os.environ.get("RESEARCH_LOOP_INVENTORY_SECONDS", "2.0"))
HASH_LIMIT_BYTES = int(os.environ.get("RESEARCH_LOOP_HASH_LIMIT_BYTES", "2097152"))
DEFAULT_ROUTE_AGENT_IDLE_TIMEOUT_SECONDS = float(os.environ.get("RESEARCH_LOOP_ROUTE_AGENT_IDLE_TIMEOUT_SECONDS", "900"))
DEFAULT_ROUTE_AGENT_WALL_TIMEOUT_SECONDS = float(os.environ.get("RESEARCH_LOOP_ROUTE_AGENT_WALL_TIMEOUT_SECONDS", "0"))
DEFAULT_ROUTE_AGENT_POLL_SECONDS = float(os.environ.get("RESEARCH_LOOP_ROUTE_AGENT_POLL_SECONDS", "1"))
DEFAULT_WATCHDOG_CHILD_IDLE_TIMEOUT_SECONDS = float(os.environ.get("RESEARCH_LOOP_WATCHDOG_CHILD_IDLE_TIMEOUT_SECONDS", "0"))
DEFAULT_WATCHDOG_CHILD_WALL_TIMEOUT_SECONDS = float(os.environ.get("RESEARCH_LOOP_WATCHDOG_CHILD_WALL_TIMEOUT_SECONDS", "0"))
DEFAULT_WATCHDOG_POLL_SECONDS = float(os.environ.get("RESEARCH_LOOP_WATCHDOG_POLL_SECONDS", "5"))
EXTERNAL_SUPERVISOR_CHOICES = {"none", "deepseek"}
DEFAULT_EXTERNAL_SUPERVISOR_MODEL = os.environ.get("RESEARCH_LOOP_EXTERNAL_SUPERVISOR_MODEL", "deepseek-v4-flash")
DEFAULT_EXTERNAL_SUPERVISOR_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEFAULT_EXTERNAL_SUPERVISOR_TIMEOUT_SECONDS = float(os.environ.get("RESEARCH_LOOP_EXTERNAL_SUPERVISOR_TIMEOUT_SECONDS", "20"))
DEFAULT_EXTERNAL_SUPERVISOR_MAX_CHARS = int(os.environ.get("RESEARCH_LOOP_EXTERNAL_SUPERVISOR_MAX_CHARS", "8000"))
TIMEOUT_EXIT_CODE = -124

EXTERNAL_SUPERVISOR_CONTINUE_RECOMMENDATIONS = {
    "continue_same_route",
    "retry_same_route",
    "route_next",
    "escalate_problem_loop",
    "resume",
}

RESUMABLE_AUTO_LOOP_STATUSES = {
    "route-agent-failed",
    "route-agent-timeout",
    "route-next-executor-missing",
    "route-depth-budget-exhausted",
    "route-next-handoff-required",
    "retry-same-route-handoff-required",
    "round-limit",
    "timeout",
}

SKIP_DIRS = {
    ".git",
    ".hook",
    LOOP_DIR,
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "artifacts",
    "temp_analysis",
}

STORAGE_BUCKETS: list[dict[str, Any]] = [
    {
        "id": "control",
        "default_path": LOOP_DIR,
        "aliases": [LOOP_DIR],
        "purpose": "Research-loop state, ledgers, route reports, checkpoints, and handoffs.",
        "create_by_default": True,
        "git_policy": "commit small JSON/Markdown state when useful; ignore bulky run logs",
        "internal": True,
    },
    {
        "id": "sources",
        "default_path": "sources",
        "aliases": ["sources", "references", "literature", "papers"],
        "purpose": "Human-readable source library and source-level notes.",
        "create_by_default": True,
        "git_policy": "commit curated metadata and notes",
    },
    {
        "id": "articles",
        "default_path": "sources/articles",
        "aliases": ["sources/articles", "articles", "literature/articles", "papers", "references/articles"],
        "purpose": "Article-processing packages produced from PDFs, HTML pages, text, and paper records.",
        "create_by_default": True,
        "git_policy": "commit metadata and extracted text when licensing permits; keep large PDFs external or LFS",
    },
    {
        "id": "data_root",
        "default_path": "data",
        "aliases": ["data", "datasets"],
        "purpose": "Top-level data namespace.",
        "create_by_default": True,
        "git_policy": "commit manifests and small samples; keep large data external or LFS",
    },
    {
        "id": "raw_data",
        "default_path": "data/raw",
        "aliases": ["data/raw", "datasets/raw", "raw_data"],
        "purpose": "Immutable source data exactly as acquired.",
        "create_by_default": True,
        "git_policy": "usually do not commit large raw data; commit manifest instead",
    },
    {
        "id": "external_data",
        "default_path": "data/external",
        "aliases": ["data/external", "datasets/external", "external_data"],
        "purpose": "Third-party data references, mirrors, and external provenance manifests.",
        "create_by_default": True,
        "git_policy": "commit manifests and download instructions",
    },
    {
        "id": "interim_data",
        "default_path": "data/interim",
        "aliases": ["data/interim", "datasets/interim", "intermediate", "interim"],
        "purpose": "Intermediate data that can be regenerated from raw inputs.",
        "create_by_default": True,
        "git_policy": "ignore or regenerate unless small and essential",
    },
    {
        "id": "processed_data",
        "default_path": "data/processed",
        "aliases": ["data/processed", "datasets/processed", "processed"],
        "purpose": "Cleaned or analysis-ready derived data.",
        "create_by_default": True,
        "git_policy": "commit small reproducible outputs; large outputs need release storage",
    },
    {
        "id": "data_packages",
        "default_path": "data/packages",
        "aliases": ["data/packages", "datasets/packages", "data/processed/packages"],
        "purpose": "Standardized dataset packages with raw bytes, metadata, schema, and README.",
        "create_by_default": True,
        "git_policy": "commit package metadata; large raw payloads external or LFS",
    },
    {
        "id": "code",
        "default_path": "src",
        "aliases": ["src", "code"],
        "purpose": "Reusable source code.",
        "create_by_default": False,
        "git_policy": "commit",
    },
    {
        "id": "scripts",
        "default_path": "scripts",
        "aliases": ["scripts", "bin"],
        "purpose": "Project scripts, one-off commands, and reproducible utilities.",
        "create_by_default": True,
        "git_policy": "commit",
    },
    {
        "id": "notebooks",
        "default_path": "notebooks",
        "aliases": ["notebooks", "notebook"],
        "purpose": "Exploratory notebooks and literate analysis.",
        "create_by_default": True,
        "git_policy": "commit curated notebooks; clear bulky outputs when needed",
    },
    {
        "id": "analysis",
        "default_path": "analysis",
        "aliases": ["analysis", "analyses"],
        "purpose": "Analysis plans, result interpretation, and statistical outputs.",
        "create_by_default": True,
        "git_policy": "commit",
    },
    {
        "id": "figures",
        "default_path": "outputs/figures",
        "aliases": ["outputs/figures", "figures", "artifacts/figures"],
        "purpose": "Generated figures and figure source material.",
        "create_by_default": True,
        "git_policy": "commit final figures; large working assets external or LFS",
    },
    {
        "id": "tables",
        "default_path": "outputs/tables",
        "aliases": ["outputs/tables", "tables", "artifacts/tables"],
        "purpose": "Generated tables and tabular summaries for manuscripts or reports.",
        "create_by_default": True,
        "git_policy": "commit final tables",
    },
    {
        "id": "manuscripts",
        "default_path": "manuscripts",
        "aliases": ["manuscripts", "manuscript", "paper", "docs/manuscript"],
        "purpose": "Drafts, manuscript source files, and submitted text artifacts.",
        "create_by_default": True,
        "git_policy": "commit when appropriate for the project",
    },
    {
        "id": "reports",
        "default_path": "reports",
        "aliases": ["reports", "docs/reports", "outputs/reports"],
        "purpose": "Project-facing reports distinct from loop control reports.",
        "create_by_default": True,
        "git_policy": "commit curated reports",
    },
    {
        "id": "releases",
        "default_path": "releases",
        "aliases": ["releases", "release", "public_release"],
        "purpose": "Public release packages, submissions, and reusable deliverables.",
        "create_by_default": True,
        "git_policy": "commit manifests; audit before public packaging",
    },
    {
        "id": "scratch",
        "default_path": "scratch",
        "aliases": ["scratch", "tmp", "temp_analysis"],
        "purpose": "Disposable local scratch files.",
        "create_by_default": True,
        "git_policy": "ignore",
    },
    {
        "id": "ingest_cache",
        "default_path": f"{LOOP_DIR}/ingest",
        "aliases": [f"{LOOP_DIR}/ingest"],
        "purpose": "Research-loop acquisition cache and provenance snapshots.",
        "create_by_default": True,
        "git_policy": "ignore bulky raw cache",
        "internal": True,
    },
]

STAGES = [
    "INTAKE",
    "SCOPING",
    "LITERATURE",
    "DESIGN",
    "EXECUTION",
    "ANALYSIS",
    "SYNTHESIS",
    "WRITING",
    "REVIEW",
    "REVISION_FINALIZE",
]

STAGE_ORDER = {stage: index for index, stage in enumerate(STAGES)}

ROUTE_RULES: dict[str, list[dict[str, Any]]] = {
    "INTAKE": [
        {
            "skill": "research-loop",
            "mode": "intake",
            "purpose": "Initialize project state, identify materials, and choose the correct entry stage.",
            "when": "Always run before substantive research work in a new project.",
        },
        {
            "skill": "academic-research-suite",
            "workflow": "ars/deep-research/WORKFLOW.md",
            "mode": "socratic",
            "purpose": "Narrow a broad topic into an answerable research question.",
            "when": "Use when the project has a broad topic but no precise research question.",
        },
    ],
    "SCOPING": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/deep-research/WORKFLOW.md",
            "mode": "socratic",
            "purpose": "Refine the research question, scope, variables, feasibility, and contribution.",
            "when": "Use until at least one candidate research question is active.",
        },
        {
            "skill": "nature-academic-search",
            "mode": "scoping-search",
            "purpose": "Run targeted literature probes and citation verification for the emerging question.",
            "when": "Use when the question is specific enough to search by concepts, methods, or claims.",
        },
    ],
    "LITERATURE": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/deep-research/WORKFLOW.md",
            "mode": "lit-review",
            "purpose": "Build source discovery, evidence synthesis, and literature gap analysis.",
            "when": "Use for source discovery and synthesis rather than immediate drafting.",
        },
        {
            "skill": "nature-academic-search",
            "mode": "citation-verification",
            "purpose": "Search, verify, and export citation metadata into the evidence ledger.",
            "when": "Use for DOI, Crossref, OpenAlex, PubMed, RIS, NBIB, or BibTeX work.",
        },
        {
            "skill": "pdf",
            "mode": "paper-ingest",
            "purpose": "Extract text, figures, tables, and layout evidence from PDFs.",
            "when": "Use when key materials are local PDFs or scanned/article files.",
        },
    ],
    "DESIGN": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/experiment-agent/WORKFLOW.md",
            "mode": "study-plan",
            "purpose": "Plan experiments, datasets, methods, statistics, and reproducibility checks.",
            "when": "Use before running expensive or consequential experiments.",
        },
        {
            "skill": "nature-data",
            "mode": "data-plan",
            "purpose": "Prepare data availability, FAIR metadata, and repository planning.",
            "when": "Use when a manuscript, dataset, or reproducibility package is a target.",
        },
    ],
    "EXECUTION": [
        {
            "skill": "research-loop",
            "mode": "run",
            "purpose": "Wrap commands so stdout, stderr, snapshots, and failures are recorded.",
            "when": "Use for experiments, tests, simulations, plotting, and conversions.",
        },
        {
            "skill": "academic-research-suite",
            "workflow": "ars/experiment-agent/WORKFLOW.md",
            "mode": "code-runner",
            "purpose": "Execute or audit code experiments with reproducibility discipline.",
            "when": "Use when command output needs statistical or experimental interpretation.",
        },
    ],
    "ANALYSIS": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/experiment-agent/WORKFLOW.md",
            "mode": "statistical-interpretation",
            "purpose": "Interpret results, uncertainty, robustness, and methodology limits.",
            "when": "Use when turning raw outputs into defensible findings.",
        },
        {
            "skill": "nature-figure",
            "mode": "figure-workflow",
            "purpose": "Create or audit publication-grade scientific figures.",
            "when": "Use when plots, panels, labels, or figure data provenance matter.",
        },
        {
            "skill": "spreadsheets",
            "mode": "analysis-table",
            "purpose": "Analyze or reshape CSV/XLSX/TSV tables and generate summary tables.",
            "when": "Use when primary results are tabular.",
        },
    ],
    "SYNTHESIS": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/academic-paper/WORKFLOW.md",
            "mode": "plan",
            "purpose": "Convert evidence, claims, and results into a manuscript structure.",
            "when": "Use before full drafting if claims or argument flow are still unsettled.",
        },
        {
            "skill": "nature-writing",
            "mode": "argument-structure",
            "purpose": "Draft or restructure Nature-style claims, novelty, limitations, and narrative.",
            "when": "Use for high-impact manuscript framing.",
        },
    ],
    "WRITING": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/academic-paper/WORKFLOW.md",
            "mode": "full",
            "purpose": "Draft the paper from a clear question, evidence base, and structure.",
            "when": "Use when RQ, evidence, and target output are clear.",
        },
        {
            "skill": "nature-writing",
            "mode": "manuscript-draft",
            "purpose": "Draft or restructure Nature-leaning manuscript sections.",
            "when": "Use for Nature/CNS-style manuscripts.",
        },
        {
            "skill": "nature-citation",
            "mode": "claim-citation-alignment",
            "purpose": "Attach strict citations to claims and split unsupported long passages.",
            "when": "Use when claims need citation grounding.",
        },
        {
            "skill": "word",
            "mode": "docx-output",
            "purpose": "Create or edit DOCX outputs.",
            "when": "Use when the target output is Word/DOCX.",
        },
    ],
    "REVIEW": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/academic-paper-reviewer/WORKFLOW.md",
            "mode": "full",
            "purpose": "Run a structured multi-perspective manuscript review.",
            "when": "Use for pre-submission review or internal peer review.",
        },
        {
            "skill": "nature-reviewer",
            "mode": "pre-submission-review",
            "purpose": "Simulate a Nature-style reviewer assessment.",
            "when": "Use for high-impact journal readiness.",
        },
        {
            "skill": "research-loop",
            "mode": "validate",
            "purpose": "Check structural loop integrity before review or submission.",
            "when": "Use before sending materials to any reviewer workflow.",
        },
    ],
    "REVISION_FINALIZE": [
        {
            "skill": "academic-research-suite",
            "workflow": "ars/academic-paper/WORKFLOW.md",
            "mode": "revision",
            "purpose": "Revise a manuscript against reviewer comments and maintain response traceability.",
            "when": "Use when review comments or a revision roadmap exist.",
        },
        {
            "skill": "nature-response",
            "mode": "reviewer-response",
            "purpose": "Draft or audit point-by-point reviewer responses.",
            "when": "Use with editor/reviewer comments.",
        },
        {
            "skill": "nature-polishing",
            "mode": "final-language-polish",
            "purpose": "Polish scientific prose while preserving claims and evidence.",
            "when": "Use after content is stable.",
        },
        {
            "skill": "academic-research-suite",
            "workflow": "ars/academic-paper/WORKFLOW.md",
            "mode": "format-convert",
            "purpose": "Finalize MD/DOCX/LaTeX/PDF outputs after integrity checks.",
            "when": "Use when final manuscript content is approved.",
        },
        {
            "skill": "presentations",
            "mode": "deck-output",
            "purpose": "Create a PPTX/slide deck from the completed research story.",
            "when": "Use when the target output includes slides or a talk.",
        },
    ],
}

TARGET_ROUTE_RULES: dict[str, list[dict[str, str]]] = {
    "paper": [
        {"skill": "academic-research-suite", "mode": "academic-pipeline", "purpose": "Coordinate research-to-paper flow."},
        {"skill": "nature-writing", "mode": "manuscript", "purpose": "Draft high-impact manuscript prose."},
    ],
    "manuscript": [
        {"skill": "academic-research-suite", "mode": "academic-pipeline", "purpose": "Coordinate full manuscript workflow."},
        {"skill": "nature-polishing", "mode": "language-polish", "purpose": "Polish final manuscript language."},
    ],
    "figure": [
        {"skill": "nature-figure", "mode": "publication-figure", "purpose": "Create or audit scientific figures."},
    ],
    "docx": [
        {"skill": "word", "mode": "docx", "purpose": "Create, edit, or verify Word documents."},
    ],
    "pdf": [
        {"skill": "pdf", "mode": "render-verify", "purpose": "Inspect, create, render, or verify PDFs."},
    ],
    "slides": [
        {"skill": "presentations", "mode": "pptx", "purpose": "Create or edit slide decks."},
    ],
    "ppt": [
        {"skill": "presentations", "mode": "pptx", "purpose": "Create or edit slide decks."},
    ],
    "patent": [
        {"skill": "nature-paper-to-patent", "mode": "patent-draft", "purpose": "Convert research materials into a Chinese invention patent draft."},
    ],
    "knowledge-base": [
        {"skill": "llm-wiki", "mode": "knowledge-ingest", "purpose": "Persist research materials into a structured knowledge base."},
    ],
}

SHARED_ROUTE_NODES: list[dict[str, str]] = [
    {"id": "N0", "name": "state-read", "purpose": "Read project state, passport, checkpoint, and handoff context."},
    {"id": "N1", "name": "task-intake", "purpose": "Classify the immediate task and available material state."},
    {"id": "N2", "name": "depth-assignment", "purpose": "Choose loop depth from lightweight recordkeeping to strict audit."},
    {"id": "N3", "name": "preflight-gate", "purpose": "Check prerequisites, blockers, data sensitivity, and verification strictness."},
    {"id": "N4", "name": "dispatcher", "purpose": "Dispatch work to one or more research subchains."},
    {"id": "N5", "name": "artifact-registry", "purpose": "Register files, datasets, drafts, figures, runs, and external sources."},
    {"id": "N6", "name": "ledger-update", "purpose": "Update claims, evidence, decisions, risks, and next actions."},
    {"id": "N7", "name": "quality-gate", "purpose": "Validate structural integrity and route failures back to the right subchain."},
    {"id": "N8", "name": "checkpoint-handoff", "purpose": "Persist resumable state for later threads or later phases."},
    {"id": "N9", "name": "feedback-dispatcher", "purpose": "Route failed gates back to literature, claim, method, data, analysis, writing, or revision work."},
]

CAPABILITY_MATRIX: dict[str, dict[str, Any]] = {
    "skill:research-loop": {
        "kind": "skill",
        "status": "available",
        "name": "research-loop",
        "use_for": "Project-local state, route plans, records, checkpoints, handoffs, run logs, and validation.",
    },
    "skill:academic-research-suite": {
        "kind": "skill",
        "status": "available",
        "name": "academic-research-suite",
        "use_for": "Deep research, paper workflow, experiment planning, review, revision, and integrity gates.",
    },
    "skill:nature-academic-search": {
        "kind": "skill",
        "status": "available",
        "name": "nature-academic-search",
        "use_for": "Literature search, citation verification, MeSH/search strategies, and citation exports.",
    },
    "skill:pdf": {"kind": "skill", "status": "available", "name": "pdf", "use_for": "PDF ingest, extraction, rendering, and layout verification."},
    "skill:nature-reader": {"kind": "skill", "status": "available", "name": "nature-reader", "use_for": "Paper reading and bilingual source-grounded paper readers."},
    "skill:nature-citation": {"kind": "skill", "status": "available", "name": "nature-citation", "use_for": "Strict claim-to-citation grounding and citation insertion."},
    "skill:nature-data": {"kind": "skill", "status": "available", "name": "nature-data", "use_for": "Data availability, FAIR metadata, dataset citations, and repository plans."},
    "skill:nature-figure": {"kind": "skill", "status": "available", "name": "nature-figure", "use_for": "Publication-grade scientific figures and figure audits."},
    "skill:nature-writing": {"kind": "skill", "status": "available", "name": "nature-writing", "use_for": "Nature-style manuscript sections, outlines, and argument structure."},
    "skill:nature-polishing": {"kind": "skill", "status": "available", "name": "nature-polishing", "use_for": "Final scientific prose polish and translation."},
    "skill:nature-reviewer": {"kind": "skill", "status": "available", "name": "nature-reviewer", "use_for": "Pre-submission reviewer simulation and critique."},
    "skill:nature-response": {"kind": "skill", "status": "available", "name": "nature-response", "use_for": "Reviewer response letters and revision strategy."},
    "skill:nature-paper2ppt": {"kind": "skill", "status": "available", "name": "nature-paper2ppt", "use_for": "Paper-to-PPT scientific presentation workflow."},
    "skill:nature-paper-to-patent": {"kind": "skill", "status": "available", "name": "nature-paper-to-patent", "use_for": "Research-to-Chinese-patent drafting."},
    "skill:llm-wiki": {"kind": "skill", "status": "available", "name": "llm-wiki", "use_for": "Local research knowledge base and graph-backed wiki workflows."},
    "skill:word": {"kind": "skill", "status": "available", "name": "word", "use_for": "Word/DOCX creation, editing, conversion, and verification."},
    "skill:spreadsheets": {"kind": "skill", "status": "available", "name": "spreadsheets", "use_for": "CSV/XLSX/Sheets analysis, tables, formulas, and charts."},
    "skill:presentations": {"kind": "skill", "status": "available", "name": "presentations", "use_for": "PPTX/Slides deck creation, editing, render, and export."},
    "skill:latex": {"kind": "skill", "status": "available", "name": "latex", "use_for": "LaTeX compilation and final PDF generation."},
    "skill:diagnose": {"kind": "skill", "status": "available", "name": "diagnose", "use_for": "Bug, failure, and performance diagnosis loops."},
    "skill:tdd": {"kind": "skill", "status": "available", "name": "tdd", "use_for": "Test-first implementation and regression coverage."},
    "skill:prototype": {"kind": "skill", "status": "available", "name": "prototype", "use_for": "Fast state-machine, workflow, or UI prototype validation."},
    "skill:skill-plugin-router": {"kind": "skill", "status": "available", "name": "skill-plugin-router", "use_for": "Capability inventory and skill/plugin/app routing."},
    "plugin:github": {"kind": "app", "status": "discoverable", "name": "GitHub", "use_for": "Repos, issues, PRs, comments, code review, and CI status."},
    "plugin:google-drive": {"kind": "app", "status": "discoverable", "name": "Google Drive", "use_for": "Drive, Docs, Sheets, Slides, comments, imports, and exports."},
    "plugin:gmail": {"kind": "app", "status": "discoverable", "name": "Gmail", "use_for": "Research email search, attachments, drafts, and reviewer correspondence."},
    "plugin:linear": {"kind": "app", "status": "discoverable", "name": "Linear", "use_for": "Issue/project planning and status updates."},
    "plugin:hugging-face": {"kind": "app", "status": "discoverable", "name": "Hugging Face", "use_for": "Models, datasets, papers, Spaces, docs, and remote jobs."},
    "plugin:readwise": {"kind": "app", "status": "discoverable", "name": "Readwise/Reader", "use_for": "Reading library, saved documents, and highlights."},
    "tool:prompt-normalizer": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "prompt-normalizer",
        "use_for": "Convert incomplete natural-language requests into project-grounded downstream prompts before routing.",
    },
    "tool:research-source-hub": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "research-source-hub",
        "use_for": "Public metadata lookup through Crossref, OpenAlex, and arXiv with normalized JSON outputs.",
    },
    "tool:content-ingest": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "content-ingest",
        "use_for": "Fetch or import explicit URLs and local files into storage-policy buckets as article packages, data packages, material records, and llm-wiki-compatible pages.",
    },
    "tool:storage-policy": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "storage-policy",
        "use_for": "Create, audit, and apply project-facing storage layouts that adapt to existing repositories or initialize a clean research project structure.",
    },
    "tool:problem-loop": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "problem-loop",
        "use_for": "Analyze blocked projects through isolated scratch labs, constructed expert panels, captured tests, adjustment plans, and promotion gates before core files are touched.",
    },
    "tool:zotero-bridge": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "zotero-bridge",
        "use_for": "Project-level Zotero collection plans, BibTeX/CSL-JSON exports, PDF attachment plans, dedupe reports, and llm-wiki-compatible paper pages.",
    },
    "tool:auto-loop-runner": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "auto-loop-runner",
        "use_for": "Run validation/test/repair rounds unattended, record failures, and route failed gates into the next loop round.",
    },
    "tool:deep-loop-router": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "deep-loop-router",
        "use_for": "Evaluate subchain gates, create review-for-transition or review-for-retry directives, and route deep loop trees across P1-P10 subchains.",
    },
    "tool:research-council-reviewer": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "research-council-reviewer",
        "use_for": "Construct fixed and dynamic expert cards with required reads, diagnostic frames, red flags, output contracts, cross-critique, and route recommendations for deep-loop gates.",
    },
    "tool:adversarial-gate-reviewer": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "adversarial-gate-reviewer",
        "use_for": "Attack premature convergence, fatal objections, missing counterfactuals, and killer tests before an arbiter finalizes deep-loop continuation decisions.",
    },
    "tool:claim-evidence-verifier": {
        "kind": "built-in-tool",
        "status": "available",
        "name": "claim-evidence-verifier",
        "use_for": "Deterministic claim-to-evidence structure checks over claim ids, evidence ids, source, locator, status, and verification verdicts.",
    },
    "missing:repository-publisher": {
        "kind": "missing-tool",
        "status": "missing",
        "name": "repository-publisher",
        "use_for": "Zenodo/OSF data, code, and supplement publication with DOI/provenance backfill.",
        "priority": "P1",
    },
    "missing:research-kg-builder": {
        "kind": "missing-tool",
        "status": "missing",
        "name": "research-kg-builder",
        "use_for": "Project knowledge graph over papers, claims, methods, datasets, runs, figures, and decisions.",
        "priority": "P1",
    },
    "missing:experiment-runner-plus": {
        "kind": "missing-tool",
        "status": "missing",
        "name": "experiment-runner-plus",
        "use_for": "Environment hashes, resource logging, retries, batch jobs, and local/remote run normalization.",
        "priority": "P1",
    },
    "missing:ethics-compliance-gate": {
        "kind": "missing-tool",
        "status": "missing",
        "name": "ethics-compliance-gate",
        "use_for": "IRB, privacy, AI disclosure, PRISMA/CONSORT, registered report, and compliance gate checks.",
        "priority": "P2",
    },
    "missing:literature-monitor": {
        "kind": "missing-tool",
        "status": "missing",
        "name": "literature-monitor",
        "use_for": "Scheduled new-paper, citation, and competitor-result monitoring for active projects.",
        "priority": "P2",
    },
}

SUBCHAIN_RULES: list[dict[str, Any]] = [
    {
        "id": "P1",
        "name": "scoping-question-chain",
        "task_types": ["intake", "scoping"],
        "stages": ["INTAKE", "SCOPING"],
        "required_inputs": ["project direction or broad topic"],
        "outputs": ["research question brief", "scope boundaries", "open questions"],
        "gates": ["active research question exists before later-stage routing"],
        "capability_ids": ["skill:research-loop", "tool:prompt-normalizer", "tool:storage-policy", "skill:academic-research-suite", "skill:nature-academic-search"],
        "missing_capability_ids": [],
        "default_depth": "L4",
        "feedback_on_fail": ["P1"],
    },
    {
        "id": "P2",
        "name": "literature-evidence-chain",
        "task_types": ["literature", "claim_synthesis"],
        "stages": ["LITERATURE", "SYNTHESIS", "WRITING", "REVIEW"],
        "required_inputs": ["research question", "search terms or seed materials"],
        "outputs": ["bibliography", "source metadata", "evidence ledger records", "reading matrix"],
        "gates": ["source metadata verified", "key sources recorded", "unverified evidence visible"],
        "capability_ids": ["tool:content-ingest", "tool:research-source-hub", "tool:zotero-bridge", "skill:nature-academic-search", "skill:pdf", "skill:nature-reader", "plugin:readwise", "skill:llm-wiki"],
        "missing_capability_ids": [],
        "default_depth": "L3",
        "feedback_on_fail": ["P2", "P3"],
    },
    {
        "id": "P3",
        "name": "claim-contribution-chain",
        "task_types": ["claim_synthesis", "writing_formatting", "review_revision"],
        "stages": ["SYNTHESIS", "WRITING", "REVIEW", "REVISION_FINALIZE"],
        "required_inputs": ["claims", "evidence records", "counterevidence if available"],
        "outputs": ["claim map", "novelty audit", "claim evidence links"],
        "gates": ["claims have evidence ids", "unsupported claims blocked or deferred"],
        "capability_ids": ["tool:claim-evidence-verifier", "skill:academic-research-suite", "skill:nature-citation", "skill:nature-reviewer"],
        "missing_capability_ids": [],
        "default_depth": "L5",
        "feedback_on_fail": ["P2", "P3", "P7"],
    },
    {
        "id": "P4",
        "name": "method-experiment-compliance-chain",
        "task_types": ["design_compliance"],
        "stages": ["DESIGN"],
        "required_inputs": ["research question", "method candidates", "data constraints"],
        "outputs": ["protocol", "experiment plan", "statistics plan", "data management plan"],
        "gates": ["method reproducibility checked", "data sensitivity handled", "compliance flags resolved"],
        "capability_ids": ["skill:academic-research-suite", "skill:nature-data", "skill:prototype"],
        "missing_capability_ids": ["missing:ethics-compliance-gate"],
        "default_depth": "L5",
        "feedback_on_fail": ["P1", "P4"],
    },
    {
        "id": "P5",
        "name": "data-code-execution-chain",
        "task_types": ["execution"],
        "stages": ["EXECUTION"],
        "required_inputs": ["code, script, dataset, command, or notebook"],
        "outputs": ["run logs", "failure logs", "datasets", "code artifacts", "provenance records"],
        "gates": ["commands wrapped", "failures recorded", "environment or run context captured"],
        "capability_ids": ["skill:research-loop", "tool:storage-policy", "tool:content-ingest", "tool:auto-loop-runner", "skill:diagnose", "skill:tdd", "plugin:github", "plugin:hugging-face"],
        "missing_capability_ids": ["missing:experiment-runner-plus"],
        "default_depth": "L3",
        "feedback_on_fail": ["P5", "P4"],
    },
    {
        "id": "P6",
        "name": "analysis-statistics-figure-chain",
        "task_types": ["analysis_visualization"],
        "stages": ["ANALYSIS", "SYNTHESIS", "WRITING"],
        "required_inputs": ["results, data, tables, run logs, or analysis scripts"],
        "outputs": ["analysis report", "tables", "figures", "figure legends"],
        "gates": ["statistics and uncertainty checked", "figures trace to data/results"],
        "capability_ids": ["skill:academic-research-suite", "skill:nature-figure", "skill:spreadsheets", "skill:pdf"],
        "missing_capability_ids": [],
        "default_depth": "L4",
        "feedback_on_fail": ["P5", "P6", "P3"],
    },
    {
        "id": "P7",
        "name": "writing-citation-format-chain",
        "task_types": ["writing_formatting", "submission_release"],
        "stages": ["SYNTHESIS", "WRITING", "REVISION_FINALIZE"],
        "required_inputs": ["research question", "claims", "evidence", "target output"],
        "outputs": ["outline", "manuscript draft", "citations", "DOCX/LaTeX/PDF outputs"],
        "gates": ["claims grounded", "citation style aligned", "format target checked"],
        "capability_ids": ["tool:claim-evidence-verifier", "skill:academic-research-suite", "skill:nature-writing", "skill:nature-citation", "skill:nature-polishing", "skill:word", "skill:latex", "skill:pdf"],
        "missing_capability_ids": [],
        "default_depth": "L4",
        "feedback_on_fail": ["P2", "P3", "P7"],
    },
    {
        "id": "P8",
        "name": "review-revision-integrity-chain",
        "task_types": ["review_revision"],
        "stages": ["REVIEW", "REVISION_FINALIZE"],
        "required_inputs": ["draft, review comments, revision roadmap, or target venue"],
        "outputs": ["review reports", "revision roadmap", "revised draft", "response letter", "integrity report"],
        "gates": ["high risks resolved or accepted", "failed evidence resolved", "revision response traceable"],
        "capability_ids": ["tool:claim-evidence-verifier", "skill:academic-research-suite", "skill:nature-reviewer", "skill:nature-response", "skill:nature-citation", "plugin:gmail", "plugin:google-drive"],
        "missing_capability_ids": [],
        "default_depth": "L6",
        "feedback_on_fail": ["P2", "P3", "P6", "P7", "P8"],
    },
    {
        "id": "P9",
        "name": "submission-publication-reuse-chain",
        "task_types": ["submission_release"],
        "stages": ["REVISION_FINALIZE"],
        "required_inputs": ["final draft", "figures", "data/code availability", "submission target"],
        "outputs": ["submission package", "cover letter", "slides", "data/code release", "next project seeds"],
        "gates": ["package complete", "no absolute-path residue", "release provenance recorded"],
        "capability_ids": ["tool:zotero-bridge", "skill:llm-wiki", "skill:presentations", "skill:nature-paper2ppt", "skill:nature-paper-to-patent", "plugin:github", "plugin:google-drive", "plugin:gmail", "plugin:linear"],
        "missing_capability_ids": ["missing:repository-publisher", "missing:research-kg-builder", "missing:literature-monitor"],
        "default_depth": "L5",
        "feedback_on_fail": ["P7", "P8", "P9"],
    },
    {
        "id": "P10",
        "name": "problem-resolution-expert-chain",
        "task_types": ["problem_resolution"],
        "stages": STAGES,
        "required_inputs": ["problem statement, current project state, available logs, and optional test commands"],
        "outputs": ["problem context snapshot", "expert panel", "isolated lab artifacts", "test logs", "adjustment plan", "promotion gate"],
        "gates": ["lab isolation enforced", "expert threshold met", "tests pass before promotion", "core edits require promotion"],
        "capability_ids": ["tool:problem-loop", "tool:storage-policy", "tool:auto-loop-runner", "skill:diagnose", "skill:tdd", "skill:research-loop"],
        "missing_capability_ids": [],
        "default_depth": "L6",
        "feedback_on_fail": ["P10", "P5", "P8"],
    },
]

STAGE_TASK_TYPES: dict[str, str] = {
    "INTAKE": "intake",
    "SCOPING": "scoping",
    "LITERATURE": "literature",
    "DESIGN": "design_compliance",
    "EXECUTION": "execution",
    "ANALYSIS": "analysis_visualization",
    "SYNTHESIS": "claim_synthesis",
    "WRITING": "writing_formatting",
    "REVIEW": "review_revision",
    "REVISION_FINALIZE": "review_revision",
}

PRIMARY_STAGE_SUBCHAINS: dict[str, set[str]] = {
    "INTAKE": {"P1"},
    "SCOPING": {"P1", "P2"},
    "LITERATURE": {"P2"},
    "DESIGN": {"P4"},
    "EXECUTION": {"P5"},
    "ANALYSIS": {"P6"},
    "SYNTHESIS": {"P3", "P7"},
    "WRITING": {"P7"},
    "REVIEW": {"P8"},
    "REVISION_FINALIZE": {"P8", "P9"},
}

TASK_KEYWORDS: dict[str, list[str]] = {
    "problem_resolution": ["problem", "blocked", "blocker", "failure", "fails", "failing", "error", "bug", "diagnose", "root cause", "stuck", "issue", "obstacle", "not working", "问题", "阻碍", "失败", "报错", "诊断", "卡住", "故障"],
    "content_ingest": ["ingest", "import", "fetch", "crawl", "scrape", "download", "url", "local file", "content", "\u722c\u53d6", "\u6293\u53d6", "\u5bfc\u5165", "\u91c7\u96c6", "\u6536\u96c6", "\u5185\u5bb9\u6295\u5165"],
    "literature": ["literature", "source", "citation", "reference", "doi", "pubmed", "arxiv", "crossref", "\u6587\u732e", "\u5f15\u7528"],
    "claim_synthesis": ["claim", "hypothesis", "contribution", "novelty", "argument", "\u5047\u8bbe", "\u8d21\u732e", "\u521b\u65b0"],
    "design_compliance": ["method", "protocol", "experiment design", "statistics plan", "ethics", "irb", "compliance", "\u65b9\u6cd5", "\u5b9e\u9a8c\u8bbe\u8ba1", "\u5408\u89c4"],
    "execution": ["run", "execute", "debug", "test", "train", "simulation", "notebook", "code", "\u8fd0\u884c", "\u4ee3\u7801", "\u8c03\u8bd5"],
    "analysis_visualization": ["analysis", "statistics", "figure", "plot", "table", "visual", "\u5206\u6790", "\u7edf\u8ba1", "\u56fe"],
    "writing_formatting": ["write", "draft", "manuscript", "paper", "docx", "latex", "format", "\u5199", "\u8bba\u6587", "\u521d\u7a3f", "\u6392\u7248"],
    "review_revision": ["review", "reviewer", "comment", "response", "rebuttal", "revise", "revision", "\u5ba1\u7a3f", "\u4fee\u8ba2", "\u8fd4\u4fee"],
    "submission_release": ["submit", "submission", "publish", "release", "zenodo", "osf", "slides", "ppt", "patent", "\u6295\u7a3f", "\u53d1\u5e03", "\u4e13\u5229"],
}

ARTICLE_INGEST_KEYWORDS = ["article", "paper", "pdf", "html", "webpage", "text", "literature", "\u6587\u7ae0", "\u8bba\u6587", "\u6587\u732e", "\u7f51\u9875"]
DATA_INGEST_KEYWORDS = ["data", "dataset", "csv", "tsv", "json", "jsonl", "parquet", "xlsx", "xls", "table", "\u6570\u636e", "\u6570\u636e\u96c6", "\u8868\u683c"]

MANUSCRIPT_ARTIFACT_KEYWORDS = [
    "formula",
    "citation",
    "reference",
    "figure",
    "table",
    "caption",
    "layout",
    "word",
    "docx",
    "latex",
    "pdf",
    "manuscript",
    "\u516c\u5f0f",
    "\u5f15\u7528",
    "\u53c2\u8003\u6587\u732e",
    "\u56fe",
    "\u8868",
    "\u6392\u7248",
]

RESEARCH_EXPERIMENT_KEYWORDS = [
    "metric",
    "baseline",
    "ablation",
    "seed",
    "validation set",
    "target transform",
    "reproducibility",
    "controlled experiment",
    "small shard",
    "\u6307\u6807",
    "\u57fa\u7ebf",
    "\u6d88\u878d",
    "\u968f\u673a\u79cd\u5b50",
    "\u53ef\u590d\u73b0",
]

EXECUTION_PROFILE_DEFS: dict[str, dict[str, Any]] = {
    "standard_loop": {
        "label": "standard research loop",
        "description": "Normal project work with a chosen validation surface, smallest coherent change, direct output readback, and report.",
    },
    "manuscript_artifact_loop": {
        "label": "manuscript/artifact loop",
        "description": "Writing, citation, figure, table, formula, DOCX, LaTeX, or PDF work with artifact-specific integrity checks.",
    },
    "research_experiment_loop": {
        "label": "research experiment loop",
        "description": "Method, data, code, analysis, figure, or experiment work that must lock metrics and validate with small representative checks before interpretation.",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slug(value: str, fallback: str = "research-loop") -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", value.lower()).strip("-")
    return (text or fallback)[:80].strip("-") or fallback


def compact_payload(data: Any, limit: int = PAYLOAD_LIMIT) -> str:
    try:
        text = json.dumps(data, ensure_ascii=True, indent=2, default=str)
    except Exception:
        text = repr(data)
    if len(text) > limit:
        return text[:limit] + "\n... truncated ..."
    return text


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_stdin": raw[:PAYLOAD_LIMIT]}
    return data if isinstance(data, dict) else {"payload": data}


def iter_values(data: Any):
    if isinstance(data, dict):
        for key, value in data.items():
            yield key, value
            yield from iter_values(value)
    elif isinstance(data, list):
        for item in data:
            yield from iter_values(item)


def psafe(path: Path) -> str:
    return str(path.resolve())


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, default=str), encoding="utf-8")


def write_lines(path: Path, lines: list[str]) -> None:
    ensure_dir(path.parent)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    line = json.dumps(record, ensure_ascii=True, default=str) + "\n"
    # Avoid interleaved JSONL writes when hooks/tools append to the same ledger.
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_handle = None
    deadline = time.monotonic() + 10.0
    while lock_handle is None:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            lock_handle = os.fdopen(fd, "w", encoding="utf-8")
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for JSONL ledger lock: {lock_path}")
            time.sleep(0.05)
    try:
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        lock_handle.close()
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def read_jsonl_with_errors(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not path.exists():
        return [], []
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(
                {
                    "path": psafe(path),
                    "line": line_number,
                    "error": str(exc),
                    "sample": line[:160],
                }
            )
            continue
        if isinstance(item, dict):
            records.append(item)
        else:
            errors.append(
                {
                    "path": psafe(path),
                    "line": line_number,
                    "error": "JSONL record is not an object.",
                    "sample": line[:160],
                }
            )
    return records, errors


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records, _errors = read_jsonl_with_errors(path)
    return records


def acquire_path_lock(lock_path: Path, timeout_seconds: float = 10.0):
    ensure_dir(lock_path.parent)
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            handle = os.fdopen(fd, "w", encoding="utf-8")
            handle.write(f"{os.getpid()} {utc_now()}\n")
            handle.flush()
            return handle
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(0.05)


def release_path_lock(lock_path: Path, handle: Any) -> None:
    try:
        handle.close()
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


SHORT_MUTATING_COMMANDS = {
    "init",
    "storage",
    "passport",
    "profile",
    "question",
    "material",
    "claim",
    "evidence",
    "decision",
    "risk",
    "next",
    "update",
    "problem-promote",
    "checkpoint",
    "handoff",
}


def command_needs_workspace_lock(args: argparse.Namespace) -> bool:
    command = getattr(args, "command_name", "")
    if command in SHORT_MUTATING_COMMANDS:
        return True
    if command == "claim-evidence" and getattr(args, "write", False):
        return True
    if command == "validate":
        return True
    if command == "route" and getattr(args, "write", False):
        return True
    if command == "deep-loop" and getattr(args, "write", False):
        return True
    return False


def short_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:10]


def record_id(prefix: str, text: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{short_digest(text)}"


def run_name(prefix: str, text: str, fallback: str = "goal") -> str:
    readable = slug(text, fallback)[:36].strip("-") or fallback
    return f"{timestamp()}-{prefix}-{short_digest(text)}-{readable}"


def split_multi(value: str | None) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[;\n]+", value)
    return [part.strip() for part in parts if part.strip()]


def normalize_record_status(status: str | None, allowed: set[str], default: str) -> str:
    value = (status or default).strip().lower().replace("_", "-")
    if value not in allowed:
        raise ValueError(f"Unknown status '{status}'. Allowed: {', '.join(sorted(allowed))}")
    return value


def update_list_item(items: list[dict[str, Any]], item: dict[str, Any]) -> None:
    item_id = item.get("id")
    if not item_id:
        items.append(item)
        return
    for index, existing in enumerate(items):
        if isinstance(existing, dict) and existing.get("id") == item_id:
            merged = dict(existing)
            merged.update(item)
            items[index] = merged
            return
    items.append(item)


def find_item(items: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None:
    for item in items:
        if isinstance(item, dict) and item.get("id") == item_id:
            return item
    return None


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def text_excerpt(path: Path, max_chars: int = 2400) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    if len(text) > max_chars:
        return text[:max_chars] + "\n... truncated ..."
    return text


def current_evidence_records(cwd: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(evidence_path(cwd)):
        record_type = record.get("type")
        record_id_value = record.get("id") or record.get("evidence_id")
        if not record_id_value:
            continue
        record_id_text = str(record_id_value)
        if record_type == "evidence":
            records[record_id_text] = dict(record)
        elif record_type == "evidence_update" and record_id_text in records:
            updated = dict(records[record_id_text])
            for key in ["kind", "source", "locator", "claim_id", "status", "note"]:
                if key in record and record[key] is not None:
                    updated[key] = record[key]
            updated["updated_at"] = record.get("timestamp", utc_now())
            records[record_id_text] = updated
    return records


def recompute_evidence_summary(cwd: Path, passport: dict[str, Any]) -> None:
    summary = {"verified": 0, "partial": 0, "unverified": 0, "failed": 0}
    for record in current_evidence_records(cwd).values():
        status = str(record.get("status") or "unverified")
        if status in summary:
            summary[status] += 1
    passport["evidence_summary"] = summary


def default_profile() -> dict[str, Any]:
    return {
        "target_venue": None,
        "citation_style": None,
        "preferred_language": None,
        "data_sensitivity": "normal",
        "verification_strictness": "standard",
        "route_mode": "standard",
    }


def loop_root(cwd: Path) -> Path:
    return cwd / LOOP_DIR


def state_path(cwd: Path) -> Path:
    return loop_root(cwd) / "state.json"


def passport_path(cwd: Path) -> Path:
    return loop_root(cwd) / "material-passport.json"


def evidence_path(cwd: Path) -> Path:
    return loop_root(cwd) / "evidence-ledger.jsonl"


def decisions_path(cwd: Path) -> Path:
    return loop_root(cwd) / "decision-log.jsonl"


def artifacts_path(cwd: Path) -> Path:
    return loop_root(cwd) / "artifact-registry.jsonl"


def lifecycle_path(cwd: Path) -> Path:
    return loop_root(cwd) / "lifecycle-events.jsonl"


def current_path(cwd: Path) -> Path:
    return loop_root(cwd) / "current.json"


def runs_root(cwd: Path) -> Path:
    return loop_root(cwd) / "runs"


def checkpoints_root(cwd: Path) -> Path:
    return loop_root(cwd) / "checkpoints"


def handoffs_root(cwd: Path) -> Path:
    return loop_root(cwd) / "handoffs"


def reports_root(cwd: Path) -> Path:
    return loop_root(cwd) / "reports"


def watchdog_root(cwd: Path) -> Path:
    return loop_root(cwd) / "watchdog"


def supervisor_root(cwd: Path) -> Path:
    return loop_root(cwd) / "supervisor"


def experts_root(cwd: Path) -> Path:
    return loop_root(cwd) / "experts"


def research_councils_root(cwd: Path) -> Path:
    return experts_root(cwd) / "councils"


def adversarial_gates_root(cwd: Path) -> Path:
    return loop_root(cwd) / "adversarial-gates"


def deep_loops_root(cwd: Path) -> Path:
    return loop_root(cwd) / "deep-loops"


def problem_cases_root(cwd: Path) -> Path:
    return loop_root(cwd) / "problem-cases"


def problem_reports_root(cwd: Path) -> Path:
    return loop_root(cwd) / "problem-reports"


def promotions_root(cwd: Path) -> Path:
    return loop_root(cwd) / "promotions"


def storage_policy_path(cwd: Path) -> Path:
    return loop_root(cwd) / "storage-policy.json"


def storage_reports_root(cwd: Path) -> Path:
    return loop_root(cwd) / "storage-reports"


def normalize_storage_style(style: str | None) -> str:
    value = (style or "adaptive").strip().lower().replace("_", "-")
    aliases = {
        "auto": "adaptive",
        "standard": "canonical",
        "research": "canonical",
        "project": "canonical",
        "loop": "loop-local",
        "looplocal": "loop-local",
    }
    value = aliases.get(value, value)
    if value not in {"adaptive", "canonical", "minimal", "loop-local"}:
        raise ValueError("Unknown storage style. Allowed: adaptive, canonical, minimal, loop-local.")
    return value


def storage_spec(bucket_id: str) -> dict[str, Any]:
    for item in STORAGE_BUCKETS:
        if item["id"] == bucket_id:
            return item
    raise ValueError(f"Unknown storage bucket: {bucket_id}")


def normalize_storage_relpath(value: str) -> str:
    return value.replace("\\", "/").strip().strip("/")


def storage_candidate_exists(cwd: Path, relpath: str) -> bool:
    path = cwd / relpath
    try:
        return path.exists() and path.is_dir()
    except Exception:
        return False


def detect_storage_path(cwd: Path, spec: dict[str, Any]) -> tuple[str, str]:
    for alias in spec.get("aliases") or []:
        rel = normalize_storage_relpath(str(alias))
        if storage_candidate_exists(cwd, rel):
            return rel, "detected"
    return normalize_storage_relpath(str(spec["default_path"])), "default"


def loop_local_storage_path(spec: dict[str, Any]) -> str:
    bucket_id = str(spec["id"])
    mapping = {
        "control": LOOP_DIR,
        "sources": f"{LOOP_DIR}/sources",
        "articles": f"{LOOP_DIR}/articles",
        "data_root": f"{LOOP_DIR}/data",
        "raw_data": f"{LOOP_DIR}/data/raw",
        "external_data": f"{LOOP_DIR}/data/external",
        "interim_data": f"{LOOP_DIR}/data/interim",
        "processed_data": f"{LOOP_DIR}/data/processed",
        "data_packages": f"{LOOP_DIR}/data",
        "reports": f"{LOOP_DIR}/reports",
        "scratch": f"{LOOP_DIR}/scratch",
        "ingest_cache": f"{LOOP_DIR}/ingest",
    }
    return mapping.get(bucket_id, f"{LOOP_DIR}/{bucket_id}")


def minimal_storage_path(spec: dict[str, Any]) -> str:
    bucket_id = str(spec["id"])
    mapping = {
        "control": LOOP_DIR,
        "sources": "materials",
        "articles": "materials/articles",
        "data_root": "data",
        "raw_data": "data/raw",
        "external_data": "data/external",
        "interim_data": "data/interim",
        "processed_data": "data/processed",
        "data_packages": "data/packages",
        "figures": "outputs/figures",
        "tables": "outputs/tables",
        "reports": "outputs/reports",
        "ingest_cache": f"{LOOP_DIR}/ingest",
    }
    return mapping.get(bucket_id, normalize_storage_relpath(str(spec["default_path"])))


def build_storage_policy(cwd: Path, style: str | None = None) -> dict[str, Any]:
    resolved_style = normalize_storage_style(style)
    buckets: list[dict[str, Any]] = []
    for spec in STORAGE_BUCKETS:
        if resolved_style == "adaptive":
            relpath, source = detect_storage_path(cwd, spec)
        elif resolved_style == "loop-local":
            relpath, source = loop_local_storage_path(spec), "style"
        elif resolved_style == "minimal":
            relpath, source = minimal_storage_path(spec), "style"
        else:
            relpath, source = normalize_storage_relpath(str(spec["default_path"])), "style"
        abs_path = resolve_storage_path(cwd, relpath)
        buckets.append(
            {
                "id": spec["id"],
                "path": relpath,
                "absolute_path": psafe(abs_path),
                "path_source": source,
                "purpose": spec.get("purpose"),
                "create_by_default": bool(spec.get("create_by_default")),
                "git_policy": spec.get("git_policy"),
                "internal": bool(spec.get("internal", False)),
                "exists": abs_path.exists(),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "style": resolved_style,
        "project_root": psafe(cwd),
        "policy_path": psafe(storage_policy_path(cwd)),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "rules": {
            "control_plane": LOOP_DIR,
            "do_not_move_existing_files": True,
            "prefer_relative_project_paths": True,
            "large_file_policy": "store manifests in git; keep large raw data/PDFs external, ignored, or in LFS",
        },
        "buckets": buckets,
    }


def resolve_storage_path(cwd: Path, path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (cwd / path).resolve()


def migrate_storage_policy(cwd: Path, policy: dict[str, Any], style: str | None = None) -> dict[str, Any]:
    if not isinstance(policy, dict):
        policy = build_storage_policy(cwd, style)
    policy.setdefault("schema_version", SCHEMA_VERSION)
    policy["schema_version"] = SCHEMA_VERSION
    policy.setdefault("style", normalize_storage_style(style))
    policy["style"] = normalize_storage_style(style or policy.get("style"))
    policy["project_root"] = psafe(cwd)
    policy["policy_path"] = psafe(storage_policy_path(cwd))
    policy.setdefault("created_at", utc_now())
    policy["updated_at"] = utc_now()
    policy.setdefault(
        "rules",
        {
            "control_plane": LOOP_DIR,
            "do_not_move_existing_files": True,
            "prefer_relative_project_paths": True,
            "large_file_policy": "store manifests in git; keep large raw data/PDFs external, ignored, or in LFS",
        },
    )
    existing = {item.get("id"): item for item in policy.get("buckets") or [] if isinstance(item, dict)}
    buckets: list[dict[str, Any]] = []
    generated = build_storage_policy(cwd, policy["style"])
    for generated_bucket in generated["buckets"]:
        bucket_id = generated_bucket["id"]
        current = dict(generated_bucket)
        if bucket_id in existing:
            current.update({key: value for key, value in existing[bucket_id].items() if key not in {"id", "absolute_path", "exists"}})
        current["id"] = bucket_id
        current["path"] = normalize_storage_relpath(str(current.get("path") or generated_bucket["path"]))
        absolute = resolve_storage_path(cwd, current["path"])
        current["absolute_path"] = psafe(absolute)
        current["exists"] = absolute.exists()
        buckets.append(current)
    policy["buckets"] = buckets
    return policy


def load_storage_policy(cwd: Path, style: str | None = None, rebuild: bool = False) -> dict[str, Any]:
    if rebuild or not storage_policy_path(cwd).exists():
        policy = build_storage_policy(cwd, style)
    else:
        policy = read_json(storage_policy_path(cwd), {})
    policy = migrate_storage_policy(cwd, policy, style)
    write_json(storage_policy_path(cwd), policy)
    return policy


def storage_bucket(cwd: Path, bucket_id: str, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = policy or load_storage_policy(cwd)
    for bucket in policy.get("buckets") or []:
        if bucket.get("id") == bucket_id:
            return bucket
    raise ValueError(f"Storage bucket is not configured: {bucket_id}")


def storage_bucket_path(cwd: Path, bucket_id: str, policy: dict[str, Any] | None = None) -> Path:
    bucket = storage_bucket(cwd, bucket_id, policy)
    return resolve_storage_path(cwd, str(bucket.get("path") or storage_spec(bucket_id)["default_path"]))


def materialize_storage_policy(cwd: Path, policy: dict[str, Any], include_optional: bool = False) -> list[str]:
    created: list[str] = []
    for bucket in policy.get("buckets") or []:
        if not include_optional and not bucket.get("create_by_default"):
            continue
        path = storage_bucket_path(cwd, str(bucket["id"]), policy)
        existed = path.exists()
        ensure_dir(path)
        if not existed:
            created.append(psafe(path))
    return created


def storage_policy_issues(cwd: Path, policy: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    seen_paths: dict[str, str] = {}
    for bucket in policy.get("buckets") or []:
        bucket_id = str(bucket.get("id"))
        path = storage_bucket_path(cwd, bucket_id, policy)
        rel = normalize_storage_relpath(str(bucket.get("path") or ""))
        if bucket.get("create_by_default") and not path.exists():
            issues.append({"severity": "info", "bucket": bucket_id, "code": "directory_missing", "text": f"Directory is not created yet: {rel}"})
        key = psafe(path).lower()
        if key in seen_paths and bucket_id not in {"data_root"}:
            issues.append({"severity": "low", "bucket": bucket_id, "code": "shared_path", "text": f"Bucket shares path with {seen_paths[key]}: {rel}"})
        seen_paths[key] = bucket_id
        try:
            path.relative_to(cwd)
        except ValueError:
            issues.append({"severity": "medium", "bucket": bucket_id, "code": "outside_project", "text": f"Bucket points outside project root: {psafe(path)}"})
    return issues


def storage_policy_markdown(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# Research Storage Policy",
        "",
        f"- Created at UTC: {payload['timestamp']}",
        f"- Project root: {payload['project_root']}",
        f"- Style: {payload['style']}",
        f"- Policy: `{payload['policy_path']}`",
        f"- Directories created: {len(payload.get('created_directories') or [])}",
        f"- Issues: {len(payload.get('issues') or [])}",
        "",
        "## Buckets",
        "",
    ]
    for bucket in payload.get("buckets") or []:
        status = "exists" if bucket.get("exists") else "missing"
        lines.append(f"- `{bucket['id']}` -> `{bucket['path']}` ({status}, {bucket.get('path_source')})")
        if bucket.get("purpose"):
            lines.append(f"  - Purpose: {bucket['purpose']}")
        if bucket.get("git_policy"):
            lines.append(f"  - Git policy: {bucket['git_policy']}")
    if payload.get("created_directories"):
        lines.extend(["", "## Created Directories", ""])
        for path in payload["created_directories"]:
            lines.append(f"- `{path}`")
    if payload.get("issues"):
        lines.extend(["", "## Issues", ""])
        for issue in payload["issues"]:
            lines.append(f"- [{issue.get('severity')}] `{issue.get('bucket')}` {issue.get('code')}: {issue.get('text')}")
    return lines


def usable_workspace_path(path: Path) -> bool:
    try:
        resolved = path.expanduser().resolve()
        if not resolved.exists() or not resolved.is_dir():
            return False
        if "windowsapps" in {part.lower() for part in resolved.parts}:
            return False
        ensure_dir(resolved / LOOP_DIR)
        return True
    except Exception:
        return False


def resolve_cwd_from_payload(data: dict[str, Any]) -> Path:
    preferred = {
        "cwd",
        "workingDirectory",
        "working_directory",
        "projectRoot",
        "project_root",
        "workspaceRoot",
        "workspace_root",
        "repoPath",
        "repositoryPath",
    }
    for key, value in iter_values(data):
        if key in preferred and isinstance(value, str):
            path = Path(value).expanduser()
            if usable_workspace_path(path):
                return path.resolve()
    for env_name in ("CODEX_WORKSPACE_ROOT", "CODEX_PROJECT_ROOT", "PWD", "INIT_CWD"):
        raw = os.environ.get(env_name)
        if raw:
            path = Path(raw).expanduser()
            if usable_workspace_path(path):
                return path.resolve()
    try:
        cwd = Path.cwd().resolve()
        if usable_workspace_path(cwd):
            return cwd
    except Exception:
        pass
    return orphan_workspace(data)


def orphan_workspace(data: dict[str, Any]) -> Path:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=True, default=str)[:4000]
    digest = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:16]
    path = Path.home() / ".codex" / "hooks" / "codex-research-loop" / "orphan-workspaces" / digest
    ensure_dir(path)
    return path.resolve()


def resolve_workspace(path_value: str | None) -> Path:
    path = Path(path_value).expanduser() if path_value else Path.cwd()
    path = path.resolve()
    ensure_dir(path)
    return path


def session_key(data: dict[str, Any], cwd: Path) -> str:
    preferred = {
        "session_id",
        "sessionId",
        "conversation_id",
        "conversationId",
        "thread_id",
        "threadId",
    }
    for key, value in iter_values(data):
        if key in preferred and isinstance(value, str) and value.strip():
            return slug(value.strip(), "session")
    digest = hashlib.sha256(str(cwd).encode("utf-8", "replace")).hexdigest()[:16]
    return f"default-{digest}"


def run_git(cwd: Path, args: list[str], timeout: float = 1.2) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-c", "core.longpaths=true", *args],
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return [f"<git failed: {exc}>"]
    text = proc.stdout if proc.stdout.strip() else proc.stderr
    return text.splitlines()


def git_info(cwd: Path) -> dict[str, Any]:
    inside = run_git(cwd, ["rev-parse", "--is-inside-work-tree"])
    if not inside or inside[0].strip() != "true":
        return {"is_repository": False}
    return {
        "is_repository": True,
        "root": "\n".join(run_git(cwd, ["rev-parse", "--show-toplevel"])).strip(),
        "branch": "\n".join(run_git(cwd, ["branch", "--show-current"])).strip(),
        "head": "\n".join(run_git(cwd, ["rev-parse", "--short", "HEAD"])).strip(),
        "status_short": run_git(cwd, ["status", "--short"]),
        "diff_stat": run_git(cwd, ["diff", "--stat"]),
    }


def hash_file(path: Path) -> str | None:
    try:
        if path.stat().st_size > HASH_LIMIT_BYTES:
            return None
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 256), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return None


def inventory(cwd: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    truncated = False
    timed_out = False
    total_count = 0
    total_bytes = 0
    started = time.monotonic()

    def onerror(_error: OSError) -> None:
        return

    for root, dirs, names in os.walk(cwd, topdown=True, onerror=onerror):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        rel_root = Path(root).resolve().relative_to(cwd)
        if time.monotonic() - started > INVENTORY_SECONDS:
            timed_out = True
            break
        for name in names:
            path = Path(root) / name
            try:
                stat = path.stat()
                rel = str((rel_root / name) if str(rel_root) != "." else Path(name))
                total_count += 1
                total_bytes += stat.st_size
                if len(files) >= INVENTORY_LIMIT:
                    truncated = True
                    continue
                files.append(
                    {
                        "path": rel.replace("\\", "/"),
                        "length": stat.st_size,
                        "last_write_time_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        "sha256": hash_file(path),
                    }
                )
            except Exception:
                continue
    files.sort(key=lambda item: item["path"])
    return {
        "file_count": total_count,
        "total_bytes": total_bytes,
        "listed_count": len(files),
        "truncated": truncated,
        "timed_out": timed_out,
        "time_budget_seconds": INVENTORY_SECONDS,
        "files": files,
    }


def compare_inventory(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    before_files = {item["path"]: item for item in before.get("files", [])}
    after_files = {item["path"]: item for item in after.get("files", [])}
    added = sorted(set(after_files) - set(before_files))
    removed = sorted(set(before_files) - set(after_files))
    changed = sorted(
        path
        for path in set(before_files) & set(after_files)
        if before_files[path].get("length") != after_files[path].get("length")
        or before_files[path].get("last_write_time_utc") != after_files[path].get("last_write_time_utc")
        or before_files[path].get("sha256") != after_files[path].get("sha256")
    )
    return {"added": added, "removed": removed, "changed": changed}


def default_state(cwd: Path) -> dict[str, Any]:
    project_id = hashlib.sha256(psafe(cwd).encode("utf-8", "replace")).hexdigest()[:16]
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "project_root": psafe(cwd),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "current_stage": "INTAKE",
        "active_run_id": None,
        "latest_checkpoint": None,
        "latest_handoff": None,
        "storage_policy": None,
        "sessions": {},
        "counters": {
            "checkpoints": 0,
            "handoffs": 0,
            "runs": 0,
            "failures": 0,
            "materials": 0,
            "claims": 0,
            "evidence": 0,
            "decisions": 0,
            "deep_loops": 0,
        },
    }


def default_passport(cwd: Path, state: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": state["project_id"],
        "project_root": psafe(cwd),
        "updated_at": utc_now(),
        "stage": state.get("current_stage", "INTAKE"),
        "project_title": None,
        "domain": None,
        "profile": default_profile(),
        "output_targets": [],
        "research_question": None,
        "research_questions": [],
        "active_question_id": None,
        "project_summary": None,
        "materials": [],
        "hypotheses": [],
        "methods": [],
        "experiments": [],
        "key_claims": [],
        "evidence_summary": {
            "verified": 0,
            "partial": 0,
            "unverified": 0,
            "failed": 0,
        },
        "open_questions": [],
        "risks": [],
        "next_actions": [],
        "integrity_flags": [],
        "latest_checkpoint": None,
        "latest_handoff": None,
    }


def migrate_state(cwd: Path, state: dict[str, Any]) -> dict[str, Any]:
    default = default_state(cwd)
    for key, value in default.items():
        state.setdefault(key, value)
    counters = state.setdefault("counters", {})
    for key, value in default["counters"].items():
        counters.setdefault(key, value)
    state["schema_version"] = SCHEMA_VERSION
    state["project_root"] = psafe(cwd)
    state["storage_policy"] = psafe(storage_policy_path(cwd))
    if state.get("current_stage") not in STAGES:
        state["current_stage"] = "INTAKE"
    return state


def migrate_passport(cwd: Path, state: dict[str, Any], passport: dict[str, Any]) -> dict[str, Any]:
    default = default_passport(cwd, state)
    for key, value in default.items():
        passport.setdefault(key, value)
    passport["schema_version"] = SCHEMA_VERSION
    passport["project_id"] = state["project_id"]
    passport["project_root"] = psafe(cwd)
    passport["stage"] = state.get("current_stage", "INTAKE")

    question = passport.get("research_question")
    questions = passport.setdefault("research_questions", [])
    if question and not questions:
        question_id = record_id("rq", str(question))
        questions.append(
            {
                "id": question_id,
                "text": question,
                "status": "active",
                "stage": passport["stage"],
                "created_at": passport.get("updated_at") or utc_now(),
            }
        )
        passport["active_question_id"] = question_id
    if questions and not passport.get("research_question"):
        first = questions[0]
        if isinstance(first, dict):
            passport["research_question"] = first.get("text")

    summary = passport.setdefault("evidence_summary", {})
    for key in ["verified", "partial", "unverified", "failed"]:
        summary.setdefault(key, 0)
    profile = passport.setdefault("profile", {})
    if not isinstance(profile, dict):
        profile = {}
        passport["profile"] = profile
    for key, value in default_profile().items():
        profile.setdefault(key, value)
    for key in ["output_targets", "materials", "hypotheses", "methods", "experiments", "key_claims", "open_questions", "risks", "next_actions", "integrity_flags"]:
        if not isinstance(passport.get(key), list):
            passport[key] = []
    return passport


def load_state(cwd: Path) -> dict[str, Any]:
    state = read_json(state_path(cwd), None)
    if not isinstance(state, dict):
        state = default_state(cwd)
    state = migrate_state(cwd, state)
    write_json(state_path(cwd), state)
    return state


def save_state(cwd: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    write_json(state_path(cwd), state)


def load_passport(cwd: Path, state: dict[str, Any]) -> dict[str, Any]:
    passport = read_json(passport_path(cwd), None)
    if not isinstance(passport, dict):
        passport = default_passport(cwd, state)
    passport = migrate_passport(cwd, state, passport)
    write_json(passport_path(cwd), passport)
    return passport


def save_passport(cwd: Path, passport: dict[str, Any]) -> None:
    passport["updated_at"] = utc_now()
    write_json(passport_path(cwd), passport)


def init_project(cwd: Path, stage: str | None = None, storage_style: str | None = None, init_storage: bool = False) -> dict[str, Any]:
    root = loop_root(cwd)
    for child in ["runs", "checkpoints", "handoffs", "reports", "storage-reports", "deep-loops", "experts", "experts/councils", "adversarial-gates", "problem-cases", "problem-reports", "promotions", "watchdog"]:
        ensure_dir(root / child)
    policy = load_storage_policy(cwd, storage_style)
    if init_storage:
        materialize_storage_policy(cwd, policy, include_optional=True)
    state = load_state(cwd)
    if stage:
        state["current_stage"] = normalize_stage(stage)
    state["storage_policy"] = psafe(storage_policy_path(cwd))
    save_state(cwd, state)
    passport = load_passport(cwd, state)
    passport["stage"] = state.get("current_stage", "INTAKE")
    save_passport(cwd, passport)
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("runs/\n*.tmp\n", encoding="utf-8")
    return state


def normalize_stage(stage: str) -> str:
    value = stage.strip().upper().replace("-", "_")
    if value not in STAGES:
        raise ValueError(f"Unknown stage '{stage}'. Allowed: {', '.join(STAGES)}")
    return value


def append_lifecycle(cwd: Path, event: str, data: dict[str, Any], extra: dict[str, Any] | None = None) -> None:
    record = {
        "timestamp": utc_now(),
        "event": event,
        "cwd": psafe(cwd),
        "payload_keys": sorted(data.keys()),
    }
    if extra:
        record.update(extra)
    append_jsonl(lifecycle_path(cwd), record)


def run_dir_for_session(cwd: Path, key: str) -> Path | None:
    current = read_json(current_path(cwd), {})
    session = current.get("sessions", {}).get(key) if isinstance(current, dict) else None
    if isinstance(session, dict) and isinstance(session.get("run_directory"), str):
        path = Path(session["run_directory"])
        if path.exists():
            return path
    state = load_state(cwd)
    session = state.get("sessions", {}).get(key)
    if isinstance(session, dict) and isinstance(session.get("run_directory"), str):
        path = Path(session["run_directory"])
        if path.exists():
            return path
    return None


def record_current_session(cwd: Path, key: str, run_dir: Path) -> None:
    current = read_json(current_path(cwd), {})
    if not isinstance(current, dict):
        current = {}
    sessions = current.setdefault("sessions", {})
    sessions[key] = {"run_directory": psafe(run_dir), "updated_at": utc_now()}
    current["last_session_key"] = key
    write_json(current_path(cwd), current)

    state = load_state(cwd)
    state_sessions = state.setdefault("sessions", {})
    state_sessions[key] = {"run_directory": psafe(run_dir), "updated_at": utc_now()}
    state["active_run_id"] = run_dir.name
    state["counters"]["runs"] = max(int(state["counters"].get("runs", 0)), len(list(runs_root(cwd).glob("*"))))
    save_state(cwd, state)


def create_pre_snapshot(cwd: Path, key: str, event: str, data: dict[str, Any]) -> Path:
    init_project(cwd)
    run_name = f"{timestamp()}-{slug(event)}-{key[:16]}"
    run_dir = runs_root(cwd) / run_name
    ensure_dir(run_dir)
    snap = {
        "schema_version": SCHEMA_VERSION,
        "event": event,
        "session_key": key,
        "created_at": utc_now(),
        "working_directory": psafe(cwd),
        "stage": load_state(cwd).get("current_stage", "INTAKE"),
        "git": git_info(cwd),
        "inventory": inventory(cwd),
    }
    write_json(run_dir / "pre-snapshot.json", snap)
    write_json(run_dir / f"{slug(event)}-payload.json", data)
    write_lines(
        run_dir / "pre-snapshot.md",
        [
            "# Research Loop Pre-Snapshot",
            "",
            f"- Event: {event}",
            f"- Session key: {key}",
            f"- Created at UTC: {snap['created_at']}",
            f"- Working directory: {cwd}",
            f"- Stage: {snap['stage']}",
            "",
            "## Inventory",
            "",
            f"- File count: {snap['inventory']['file_count']}",
            f"- Total bytes: {snap['inventory']['total_bytes']}",
            f"- Listed files: {snap['inventory']['listed_count']}",
            f"- Truncated: {snap['inventory']['truncated']}",
        ],
    )
    record_current_session(cwd, key, run_dir)
    append_lifecycle(cwd, event, data, {"session_key": key, "run_directory": psafe(run_dir)})
    return run_dir


def is_failure_payload(data: dict[str, Any]) -> bool:
    for key, value in iter_values(data):
        lowered = str(key).lower()
        if lowered in {"exit_code", "exitcode", "status_code"}:
            try:
                if int(value) != 0:
                    return True
            except Exception:
                pass
        if lowered in {"status", "outcome", "result"} and isinstance(value, str):
            if value.lower() in {"failed", "failure", "error", "errored"}:
                return True
        if lowered in {"error", "stderr", "exception"}:
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, dict) and value:
                return True
    return False


def post_tool_use(cwd: Path, key: str, event: str, data: dict[str, Any]) -> None:
    init_project(cwd)
    run_dir = run_dir_for_session(cwd, key) or create_pre_snapshot(cwd, key, event, data)
    failure = is_failure_payload(data)
    record = {
        "timestamp": utc_now(),
        "event": event,
        "session_key": key,
        "failure": failure,
        "tool_name": data.get("tool_name") or data.get("name"),
        "tool_use_id": data.get("tool_use_id"),
    }
    append_jsonl(run_dir / "tool-events.jsonl", record)
    append_lifecycle(cwd, event, data, {"session_key": key, "run_directory": psafe(run_dir), "failure": failure})
    if not failure:
        return
    failure_dir = run_dir / "failures"
    ensure_dir(failure_dir)
    stamp = timestamp()
    write_json(failure_dir / f"{stamp}-post-tool-use.json", data)
    write_lines(
        failure_dir / f"{stamp}-post-tool-use.md",
        [
            "# Research Loop Tool Failure",
            "",
            f"- Captured at UTC: {utc_now()}",
            f"- Session key: {key}",
            f"- Working directory: {cwd}",
            f"- Tool: {record.get('tool_name') or 'unknown'}",
            "",
            "## Payload",
            "",
            "```json",
            compact_payload(data),
            "```",
        ],
    )
    state = load_state(cwd)
    state["counters"]["failures"] = int(state["counters"].get("failures", 0)) + 1
    save_state(cwd, state)


def extract_assistant_message(data: dict[str, Any]) -> str:
    for key, value in iter_values(data):
        if key in {"last_assistant_message", "assistant_message", "message"} and isinstance(value, str):
            return value.strip()
    return ""


def stop_summary(cwd: Path, key: str, event: str, data: dict[str, Any]) -> None:
    init_project(cwd)
    run_dir = run_dir_for_session(cwd, key) or create_pre_snapshot(cwd, key, event, data)
    before = read_json(run_dir / "pre-snapshot.json", {})
    after = {"captured_at": utc_now(), "git": git_info(cwd), "inventory": inventory(cwd)}
    changes = compare_inventory(before.get("inventory", {}), after["inventory"])
    write_json(run_dir / "stop-payload.json", data)
    write_json(run_dir / "post-state.json", after)
    failures = sorted((run_dir / "failures").glob("*.md")) if (run_dir / "failures").exists() else []
    assistant = extract_assistant_message(data)
    lines = [
        "# Research Loop Session Summary",
        "",
        f"- Event: {event}",
        f"- Session key: {key}",
        f"- Started at UTC: {before.get('created_at', '')}",
        f"- Ended at UTC: {after['captured_at']}",
        f"- Working directory: {cwd}",
        f"- Stage: {load_state(cwd).get('current_stage', 'INTAKE')}",
        "",
        "## File Inventory Changes",
        "",
        f"- Added: {len(changes['added'])}",
        f"- Changed: {len(changes['changed'])}",
        f"- Removed: {len(changes['removed'])}",
        f"- Failure logs: {len(failures)}",
        "",
    ]
    for title, items in [("Added", changes["added"]), ("Changed", changes["changed"]), ("Removed", changes["removed"])]:
        if items:
            lines.extend([f"### {title}", "", "```text"])
            lines.extend(items[:120])
            if len(items) > 120:
                lines.append("... truncated ...")
            lines.extend(["```", ""])
    if failures:
        lines.extend(["## Failure Logs", ""])
        lines.extend(f"- {path.name}" for path in failures)
        lines.append("")
    if assistant:
        lines.extend(["## Last Assistant Message", "", assistant[:4000], ""])
    write_lines(run_dir / "summary.md", lines)
    append_lifecycle(cwd, event, data, {"session_key": key, "run_directory": psafe(run_dir)})
    auto_checkpoint_from_stop(cwd, key, run_dir, assistant, changes)


def auto_checkpoint_from_stop(cwd: Path, key: str, run_dir: Path, assistant: str, changes: dict[str, list[str]]) -> None:
    state = load_state(cwd)
    stamp = timestamp()
    checkpoint_id = f"{stamp}-auto-stop-{key[:8]}"
    path = checkpoints_root(cwd) / f"{checkpoint_id}.md"
    write_lines(
        path,
        [
            "# Research Loop Auto Checkpoint",
            "",
            f"- Created at UTC: {utc_now()}",
            f"- Stage: {state.get('current_stage', 'INTAKE')}",
            f"- Session run: {run_dir.name}",
            f"- Added files: {len(changes['added'])}",
            f"- Changed files: {len(changes['changed'])}",
            f"- Removed files: {len(changes['removed'])}",
            "",
            "## Last Assistant Message",
            "",
            assistant[:4000] if assistant else "(No assistant message was available in the hook payload.)",
        ],
    )
    state["latest_checkpoint"] = psafe(path)
    state["counters"]["checkpoints"] = int(state["counters"].get("checkpoints", 0)) + 1
    save_state(cwd, state)
    passport = load_passport(cwd, state)
    passport["stage"] = state.get("current_stage", "INTAKE")
    passport["latest_checkpoint"] = psafe(path)
    save_passport(cwd, passport)


def command_init(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    state = init_project(cwd, args.stage, args.storage_style, args.init_storage)
    print(f"Research loop initialized: {loop_root(cwd)}")
    print(f"Stage: {state.get('current_stage')}")
    print(f"Storage policy: {storage_policy_path(cwd)}")
    return 0


def command_storage(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    policy = load_storage_policy(cwd, args.style, args.rebuild)
    created = materialize_storage_policy(cwd, policy, include_optional=args.include_optional) if args.init_dirs else []
    if created:
        policy = load_storage_policy(cwd)
    issues = storage_policy_issues(cwd, policy)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "style": policy.get("style"),
        "policy_path": psafe(storage_policy_path(cwd)),
        "created_directories": created,
        "issues": issues,
        "buckets": policy.get("buckets") or [],
        "rules": policy.get("rules") or {},
    }
    if args.write:
        suffix = "json" if args.format == "json" else "md"
        path = storage_reports_root(cwd) / f"{timestamp()}-storage-policy.{suffix}"
        if args.format == "json":
            write_json(path, payload)
        else:
            write_lines(path, storage_policy_markdown(payload))
        append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "storage_policy", "path": psafe(path), "style": policy.get("style")})
        print(f"Storage policy report: {path}")
    else:
        if args.format == "json":
            print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
        else:
            print("\n".join(storage_policy_markdown(payload)).rstrip() + "\n")
    return 0


def command_status(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    storage_policy = load_storage_policy(cwd)
    profile = passport.get("profile") or {}
    print(f"Research loop: {loop_root(cwd)}")
    print(f"Project id: {state.get('project_id')}")
    print(f"Stage: {state.get('current_stage')}")
    print(f"Updated: {state.get('updated_at')}")
    print(f"Latest checkpoint: {state.get('latest_checkpoint') or '(none)'}")
    print(f"Latest handoff: {state.get('latest_handoff') or '(none)'}")
    print(f"Storage style: {storage_policy.get('style') or 'adaptive'}")
    print(f"Storage policy: {storage_policy_path(cwd)}")
    print(f"Research question: {passport.get('research_question') or '(not set)'}")
    print(f"Target venue: {profile.get('target_venue') or '(not set)'}")
    print(f"Citation style: {profile.get('citation_style') or '(not set)'}")
    print(f"Route mode: {profile.get('route_mode') or 'standard'}")
    print(f"Verification strictness: {profile.get('verification_strictness') or 'standard'}")
    print(f"Data sensitivity: {profile.get('data_sensitivity') or 'normal'}")
    print(f"Materials: {len(passport.get('materials') or [])}")
    print(f"Claims: {len(passport.get('key_claims') or [])}")
    print(f"Open questions: {len([q for q in passport.get('open_questions') or [] if not isinstance(q, dict) or q.get('status') == 'open'])}")
    print(f"Open risks: {len([r for r in passport.get('risks') or [] if isinstance(r, dict) and r.get('status') == 'open'])}")
    print(f"Runs: {state.get('counters', {}).get('runs', 0)}")
    print(f"Failures: {state.get('counters', {}).get('failures', 0)}")
    return 0


def command_passport(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    if args.title:
        passport["project_title"] = args.title
    if args.domain:
        passport["domain"] = args.domain
    if args.summary:
        passport["project_summary"] = args.summary
    for target in args.target or []:
        append_unique(passport["output_targets"], target)
    if args.question:
        question_id = record_id("rq", args.question)
        item = {
            "id": question_id,
            "text": args.question,
            "status": "active",
            "stage": state.get("current_stage", "INTAKE"),
            "created_at": utc_now(),
        }
        update_list_item(passport["research_questions"], item)
        passport["active_question_id"] = question_id
        passport["research_question"] = args.question
    save_passport(cwd, passport)
    append_jsonl(
        decisions_path(cwd),
        {
            "timestamp": utc_now(),
            "type": "passport_update",
            "stage": state.get("current_stage", "INTAKE"),
            "fields": {
                "title": bool(args.title),
                "domain": bool(args.domain),
                "summary": bool(args.summary),
                "question": bool(args.question),
                "targets": args.target or [],
            },
        },
    )
    print(f"Passport updated: {passport_path(cwd)}")
    return 0


def command_profile(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    profile = passport.setdefault("profile", default_profile())
    updates = remove_none_values(
        {
            "target_venue": args.target_venue,
            "citation_style": args.citation_style,
            "preferred_language": args.preferred_language,
            "data_sensitivity": args.data_sensitivity,
            "verification_strictness": args.verification_strictness,
            "route_mode": args.route_mode,
        }
    )
    if args.data_sensitivity:
        updates["data_sensitivity"] = normalize_record_status(
            args.data_sensitivity,
            {"normal", "sensitive", "restricted"},
            "normal",
        )
    if args.verification_strictness:
        updates["verification_strictness"] = normalize_record_status(
            args.verification_strictness,
            {"quick", "standard", "strict"},
            "standard",
        )
    if args.route_mode:
        updates["route_mode"] = normalize_record_status(
            args.route_mode,
            {"quick", "standard", "strict"},
            "standard",
        )
    profile.update(updates)
    save_passport(cwd, passport)
    append_jsonl(
        decisions_path(cwd),
        {
            "id": record_id("profile", json.dumps(updates, sort_keys=True)),
            "timestamp": utc_now(),
            "type": "profile_update",
            "stage": state.get("current_stage", "INTAKE"),
            "updates": updates,
        },
    )
    print(f"Profile updated: {passport_path(cwd)}")
    return 0


def command_question(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    status = normalize_record_status(args.status, {"open", "active", "answered", "dropped"}, "open")
    kind = args.kind
    item_id = record_id("q", args.text)
    item = {
        "id": item_id,
        "text": args.text,
        "kind": kind,
        "status": status,
        "stage": state.get("current_stage", "INTAKE"),
        "created_at": utc_now(),
        "note": args.note,
    }
    if kind == "research":
        update_list_item(passport["research_questions"], item)
        if status == "active":
            passport["active_question_id"] = item_id
            passport["research_question"] = args.text
    else:
        update_list_item(passport["open_questions"], item)
    save_passport(cwd, passport)
    append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "question", **item})
    print(f"Question recorded: {item_id}")
    return 0


def command_material(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    material_path = Path(args.path).expanduser() if args.path else None
    resolved_path = None
    exists = None
    sha256 = None
    size = None
    if material_path:
        if not material_path.is_absolute():
            material_path = cwd / material_path
        resolved_path = psafe(material_path)
        exists = material_path.exists()
        if exists and material_path.is_file():
            sha256 = hash_file(material_path)
            size = material_path.stat().st_size
    identity = args.title or args.source or resolved_path or args.note or args.kind
    item_id = record_id("mat", identity)
    item = {
        "id": item_id,
        "kind": args.kind,
        "title": args.title,
        "path": resolved_path,
        "source": args.source,
        "status": normalize_record_status(args.status, {"available", "missing", "external", "derived"}, "available"),
        "note": args.note,
        "exists": exists,
        "size": size,
        "sha256": sha256,
        "created_at": utc_now(),
    }
    update_list_item(passport["materials"], item)
    save_passport(cwd, passport)
    append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "material", **item})
    state["counters"]["materials"] = int(state["counters"].get("materials", 0)) + 1
    save_state(cwd, state)
    print(f"Material recorded: {item_id}")
    return 0


def command_claim(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    status = normalize_record_status(
        args.status,
        {"proposed", "supported", "contested", "unverified", "retracted"},
        "proposed",
    )
    claim_id = record_id("claim", args.text)
    item = {
        "id": claim_id,
        "text": args.text,
        "status": status,
        "stage": state.get("current_stage", "INTAKE"),
        "evidence_ids": args.evidence_id or [],
        "note": args.note,
        "created_at": utc_now(),
    }
    update_list_item(passport["key_claims"], item)
    save_passport(cwd, passport)
    append_jsonl(evidence_path(cwd), {"timestamp": utc_now(), "type": "claim", **item})
    state["counters"]["claims"] = int(state["counters"].get("claims", 0)) + 1
    save_state(cwd, state)
    print(f"Claim recorded: {claim_id}")
    return 0


def command_evidence(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    status = normalize_record_status(args.status, {"verified", "partial", "unverified", "failed"}, "unverified")
    identity = " ".join(part for part in [args.source, args.locator, args.note] if part)
    evidence_id = record_id("ev", identity or args.kind)
    record = {
        "id": evidence_id,
        "type": "evidence",
        "timestamp": utc_now(),
        "kind": args.kind,
        "source": args.source,
        "locator": args.locator,
        "claim_id": args.claim_id,
        "status": status,
        "note": args.note,
    }
    append_jsonl(evidence_path(cwd), record)
    if args.claim_id:
        claim = find_item(passport["key_claims"], args.claim_id)
        if claim is None:
            passport["integrity_flags"].append(
                {
                    "id": record_id("flag", args.claim_id),
                    "severity": "medium",
                    "status": "open",
                    "text": f"Evidence {evidence_id} references missing claim {args.claim_id}.",
                    "created_at": utc_now(),
                }
            )
        else:
            ids = claim.setdefault("evidence_ids", [])
            append_unique(ids, evidence_id)
    recompute_evidence_summary(cwd, passport)
    save_passport(cwd, passport)
    state["counters"]["evidence"] = int(state["counters"].get("evidence", 0)) + 1
    save_state(cwd, state)
    print(f"Evidence recorded: {evidence_id}")
    return 0


def command_decision(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    status = normalize_record_status(args.status, {"active", "superseded", "rejected", "deferred"}, "active")
    decision_id = record_id("dec", args.decision)
    record = {
        "id": decision_id,
        "timestamp": utc_now(),
        "type": "decision",
        "stage": state.get("current_stage", "INTAKE"),
        "decision": args.decision,
        "rationale": args.rationale,
        "alternatives": split_multi(args.alternatives),
        "status": status,
    }
    append_jsonl(decisions_path(cwd), record)
    state["counters"]["decisions"] = int(state["counters"].get("decisions", 0)) + 1
    save_state(cwd, state)
    print(f"Decision recorded: {decision_id}")
    return 0


def command_risk(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    severity = normalize_record_status(args.severity, {"low", "medium", "high", "blocking"}, "medium")
    status = normalize_record_status(args.status, {"open", "mitigated", "accepted", "closed"}, "open")
    item_id = record_id("risk", args.text)
    item = {
        "id": item_id,
        "text": args.text,
        "severity": severity,
        "status": status,
        "mitigation": args.mitigation,
        "created_at": utc_now(),
    }
    update_list_item(passport["risks"], item)
    if severity in {"high", "blocking"} and status == "open":
        update_list_item(
            passport["integrity_flags"],
            {
                "id": record_id("flag", args.text),
                "severity": severity,
                "status": "open",
                "text": args.text,
                "created_at": utc_now(),
            },
        )
    save_passport(cwd, passport)
    append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "risk", **item})
    print(f"Risk recorded: {item_id}")
    return 0


def command_next(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    status = normalize_record_status(args.status, {"todo", "in-progress", "done", "blocked"}, "todo")
    item_id = record_id("next", args.text)
    item = {
        "id": item_id,
        "text": args.text,
        "stage": state.get("current_stage", "INTAKE"),
        "status": status,
        "owner": args.owner,
        "created_at": utc_now(),
    }
    update_list_item(passport["next_actions"], item)
    save_passport(cwd, passport)
    append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "next_action", **item})
    print(f"Next action recorded: {item_id}")
    return 0


def update_passport_item(
    items: list[dict[str, Any]],
    item_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    item = find_item(items, item_id)
    if item is None:
        raise ValueError(f"No record with id '{item_id}' found.")
    item.update(remove_none_values(updates))
    item["updated_at"] = utc_now()
    return item


def command_update(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    kind = args.kind
    updates = remove_none_values(
        {
            "text": args.text,
            "status": args.status,
            "note": args.note,
            "severity": args.severity,
            "mitigation": args.mitigation,
            "stage": args.stage,
            "title": args.title,
            "source": args.source,
            "path": args.path,
            "locator": args.locator,
        }
    )
    if args.evidence_id:
        updates["evidence_ids"] = args.evidence_id
    if args.stage:
        updates["stage"] = normalize_stage(args.stage)

    if kind == "claim":
        if args.status:
            updates["status"] = normalize_record_status(
                args.status,
                {"proposed", "supported", "contested", "unverified", "retracted"},
                "proposed",
            )
        item = update_passport_item(passport["key_claims"], args.id, updates)
        append_jsonl(evidence_path(cwd), {"timestamp": utc_now(), "type": "claim_update", "id": args.id, "updates": updates})
    elif kind == "risk":
        if args.status:
            updates["status"] = normalize_record_status(args.status, {"open", "mitigated", "accepted", "closed"}, "open")
        if args.severity:
            updates["severity"] = normalize_record_status(args.severity, {"low", "medium", "high", "blocking"}, "medium")
        item = update_passport_item(passport["risks"], args.id, updates)
        for flag in passport.get("integrity_flags", []):
            if isinstance(flag, dict) and flag.get("text") == item.get("text"):
                flag["status"] = "closed" if item.get("status") in {"mitigated", "accepted", "closed"} else "open"
                flag["updated_at"] = utc_now()
        append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "risk_update", "id": args.id, "updates": updates})
    elif kind == "next":
        if args.status:
            updates["status"] = normalize_record_status(args.status, {"todo", "in-progress", "done", "blocked"}, "todo")
        item = update_passport_item(passport["next_actions"], args.id, updates)
        append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "next_action_update", "id": args.id, "updates": updates})
    elif kind == "question":
        if args.status:
            updates["status"] = normalize_record_status(args.status, {"open", "active", "answered", "dropped"}, "open")
        target_list = passport["research_questions"] if find_item(passport["research_questions"], args.id) else passport["open_questions"]
        item = update_passport_item(target_list, args.id, updates)
        if item.get("status") == "active":
            passport["active_question_id"] = args.id
            passport["research_question"] = item.get("text")
        append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "question_update", "id": args.id, "updates": updates})
    elif kind == "material":
        if args.status:
            updates["status"] = normalize_record_status(args.status, {"available", "missing", "external", "derived", "retired"}, "available")
        item = update_passport_item(passport["materials"], args.id, updates)
        append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "material_update", "id": args.id, "updates": updates})
    elif kind == "evidence":
        if args.status:
            updates["status"] = normalize_record_status(args.status, {"verified", "partial", "unverified", "failed"}, "unverified")
        records = current_evidence_records(cwd)
        if args.id not in records:
            raise ValueError(f"No evidence record with id '{args.id}' found.")
        append_jsonl(
            evidence_path(cwd),
            {
                "timestamp": utc_now(),
                "type": "evidence_update",
                "id": args.id,
                **updates,
            },
        )
        recompute_evidence_summary(cwd, passport)
        item = current_evidence_records(cwd)[args.id]
    elif kind == "decision":
        if args.status:
            updates["status"] = normalize_record_status(args.status, {"active", "superseded", "rejected", "deferred"}, "active")
        append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "decision_update", "id": args.id, "updates": updates})
        item = {"id": args.id, **updates}
    else:
        raise ValueError(f"Unsupported update kind: {kind}")

    save_passport(cwd, passport)
    print(f"{kind} updated: {args.id}")
    if args.note:
        print(f"Note: {args.note}")
    return 0


def material_kinds(passport: dict[str, Any]) -> set[str]:
    return {
        str(item.get("kind", "")).lower()
        for item in passport.get("materials", [])
        if isinstance(item, dict) and item.get("kind")
    }


def target_values(passport: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for target in passport.get("output_targets", []) or []:
        values.add(str(target).strip().lower())
    return values


def active_claims(passport: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in passport.get("key_claims", []) or []
        if isinstance(item, dict) and item.get("status") not in {"retracted"}
    ]


def open_risks(passport: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in passport.get("risks", []) or []
        if isinstance(item, dict) and item.get("status") == "open"
    ]


def intent_text(intent: str | None, passport: dict[str, Any]) -> str:
    parts = [intent or "", passport.get("project_title") or "", passport.get("research_question") or ""]
    parts.extend(str(target) for target in passport.get("output_targets", []) or [])
    parts.extend(str(item.get("kind") or "") for item in passport.get("materials", []) or [] if isinstance(item, dict))
    return " ".join(parts).lower()


def task_signal_text(intent: str | None, passport: dict[str, Any]) -> str:
    current_intent = (intent or "").strip().lower()
    if current_intent:
        return current_intent
    return intent_text(intent, passport)


def has_literature_review_signal(text: str) -> bool:
    return any(
        token in text
        for token in [
            "literature review",
            "review literature",
            "systematic review",
            "scoping review",
            "meta-analysis",
            "\u6587\u732e\u7efc\u8ff0",
            "\u7efc\u8ff0",
        ]
    )


def has_review_revision_signal(text: str) -> bool:
    strong_tokens = [
        "reviewer",
        "referee",
        "comment",
        "decision letter",
        "response",
        "rebuttal",
        "revise",
        "revision",
        "pre-submission review",
        "peer review",
        "internal review",
        "\u5ba1\u7a3f",
        "\u4fee\u8ba2",
        "\u8fd4\u4fee",
        "\u5ba1\u7a3f\u610f\u89c1",
    ]
    if any(token in text for token in strong_tokens):
        return True
    if has_literature_review_signal(text):
        return False
    return any(
        token in text
        for token in [
            "review manuscript",
            "review the manuscript",
            "review paper",
            "review the paper",
            "review draft",
            "review the draft",
        ]
    )


def has_literature_signal(text: str) -> bool:
    return any(token in text for token in TASK_KEYWORDS["literature"]) or has_literature_review_signal(text)


def has_problem_resolution_signal(text: str) -> bool:
    return any(token in text for token in TASK_KEYWORDS["problem_resolution"])


def has_content_ingest_signal(text: str) -> bool:
    return any(token in text for token in TASK_KEYWORDS["content_ingest"])


def has_article_ingest_signal(text: str) -> bool:
    return any(token in text for token in ARTICLE_INGEST_KEYWORDS)


def has_data_ingest_signal(text: str) -> bool:
    return any(token in text for token in DATA_INGEST_KEYWORDS)


def has_deferred_secondary_signal(text: str) -> bool:
    return any(
        token in text
        for token in [
            "later",
            "after that",
            "afterwards",
            "eventually",
            "then",
            "next we can",
            "\u987a\u4fbf",
            "\u540e\u9762",
            "\u4e4b\u540e",
            "\u7136\u540e",
            "\u518d",
        ]
    )


def classify_execution_profile(task_type: str, passport: dict[str, Any], intent: str | None = None) -> dict[str, Any]:
    text = task_signal_text(intent, passport)
    targets = target_values(passport)
    profile_id = "standard_loop"
    if task_type in {"writing_formatting", "review_revision", "submission_release"} or targets & {"paper", "manuscript", "docx", "pdf"} or any(
        token in text for token in MANUSCRIPT_ARTIFACT_KEYWORDS
    ):
        profile_id = "manuscript_artifact_loop"
    elif task_type in {"design_compliance", "execution", "analysis_visualization"} or any(token in text for token in RESEARCH_EXPERIMENT_KEYWORDS):
        profile_id = "research_experiment_loop"
    profile = dict(EXECUTION_PROFILE_DEFS[profile_id])
    profile["id"] = profile_id
    return profile


def harness_protocol_for_profile(execution_profile: dict[str, Any], task_type: str, depth: str) -> dict[str, Any]:
    profile_id = str(execution_profile.get("id") or "standard_loop")
    sequence = [
        "scope objective, files, metrics, deliverable, and stop condition",
        "map current project state and relevant artifacts before acting",
        "choose a validation surface before editing or running",
        "build the smallest coherent increment",
        "test through the selected harness",
        "read back outputs, logs, renders, reports, or diffs directly",
        "loop until the gate passes, a retry limit is reached, or a real blocker is recorded",
        "report artifacts, validation evidence, remaining risks, and the next target",
    ]
    validation_surfaces = {
        "standard_loop": [
            "route plan",
            "structural validate",
            "artifact diff or report inspection",
            "small representative command",
        ],
        "manuscript_artifact_loop": [
            "claim-evidence verification",
            "citation or bibliography reality check",
            "formula/text preservation audit",
            "document or PDF render plus representative visual inspection",
            "artifact diff against the previous draft",
        ],
        "research_experiment_loop": [
            "metric and target-transform lock",
            "data/code material check",
            "dry-run or small representative shard",
            "wrapped command run log",
            "metric recomputation or artifact diff",
        ],
    }.get(profile_id, ["route plan", "structural validate", "artifact diff or report inspection"])
    guardrails = [
        "Do not claim completion from memory; inspect generated artifacts or logs directly.",
        "Prefer dry-runs or small representative validation before long-running commands.",
        "Record assumptions, risks, and defer decisions instead of silently accepting weak inputs.",
    ]
    if profile_id == "manuscript_artifact_loop":
        guardrails.append("Preserve LaTeX formulas, key numbers, figure/table markers, citation links, and paragraph coverage.")
    if profile_id == "research_experiment_loop":
        guardrails.append("Lock metric definitions, target transforms, validation sets, seeds, and compared training flows before interpreting deltas.")
    return {
        "source_pattern": "z2-harness-loop generalized harness discipline",
        "execution_profile": profile_id,
        "chain_depth": depth,
        "task_type": task_type,
        "sequence": sequence,
        "validation_surfaces": validation_surfaces,
        "case_contract": {
            "use_when": "Use only when the chosen validation surface benefits from reproducible case-level checks.",
            "fields": ["id", "input_or_target", "expected_or_gate", "grader", "tags", "weight", "timeout_or_budget"],
            "grader_types": ["exact", "contains", "regex", "numeric_abs_error", "artifact_exists", "human_review_gate"],
        },
        "feedback_summary": {
            "preferred_metrics": ["pass_rate", "weighted_score", "failures_by_tag", "avg_latency_or_runtime", "report_paths"],
            "routing_use": "Deep-loop and problem-loop should use failure tags and weak metric dimensions to choose retry, next subchain, or expert escalation.",
        },
        "integration_points": [
            "normalize/route choose the validation surface and case contract shape",
            "run/auto-loop execute commands and capture logs or artifacts",
            "deep-loop consumes pass/fail, scores, failure tags, and artifact refs as gate evidence",
            "problem-loop uses failure tags and logs to construct the expert panel and isolated lab plan",
            "handoff records report paths and remaining failed tags for the next subchain",
        ],
        "guardrails": guardrails,
        "report_fields": [
            "objective or hypothesis",
            "files and artifacts inspected or changed",
            "chosen validation surface",
            "commands/tests/renders run and exit status",
            "metrics, scores, counts, or direct readback evidence when available",
            "report paths and output artifacts",
            "remaining blockers or next revision target",
        ],
    }


def classify_task_type(state: dict[str, Any], passport: dict[str, Any], intent: str | None = None) -> str:
    text = task_signal_text(intent, passport)
    targets = target_values(passport)
    kinds = material_kinds(passport)
    if has_literature_review_signal(text):
        return "literature"
    if has_problem_resolution_signal(text):
        return "problem_resolution"
    if has_review_revision_signal(text) or kinds & {"reviewer-comments", "review-comments", "decision-letter", "reviews"}:
        return "review_revision"
    if any(token in text for token in TASK_KEYWORDS["submission_release"]) or targets & {"slides", "ppt", "patent"}:
        return "submission_release"
    if has_content_ingest_signal(text):
        return "content_ingest"
    if has_literature_signal(text) and has_deferred_secondary_signal(text):
        return "literature"
    for task_type in [
        "writing_formatting",
        "analysis_visualization",
        "execution",
        "design_compliance",
        "claim_synthesis",
        "literature",
        "problem_resolution",
    ]:
        if any(token in text for token in TASK_KEYWORDS[task_type]):
            return task_type
    return STAGE_TASK_TYPES.get(state.get("current_stage", "INTAKE"), "intake")


DEPTH_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
DEPTH_VALUES = {value: key for key, value in DEPTH_ORDER.items()}


def merge_depth(*values: str) -> str:
    max_value = max((DEPTH_ORDER.get(value, 0) for value in values), default=0)
    return DEPTH_VALUES.get(max_value, "L0")


def assign_depth(
    task_type: str,
    state: dict[str, Any],
    passport: dict[str, Any],
    blockers: list[dict[str, str]],
    intent: str | None = None,
) -> str:
    stage = state.get("current_stage", "INTAKE")
    profile = passport.get("profile") or {}
    base = {
        "intake": "L1",
        "scoping": "L4",
        "content_ingest": "L3",
        "problem_resolution": "L6",
        "literature": "L3",
        "claim_synthesis": "L5",
        "design_compliance": "L5",
        "execution": "L3",
        "analysis_visualization": "L4",
        "writing_formatting": "L4",
        "review_revision": "L6",
        "submission_release": "L5",
    }.get(task_type, "L2")
    text = task_signal_text(intent, passport)
    if any(token in text for token in ["full", "end-to-end", "pipeline", "systematic", "meta-analysis", "complete"]):
        base = merge_depth(base, "L5")
    if blockers or profile.get("verification_strictness") == "strict" or stage in {"REVIEW", "REVISION_FINALIZE"}:
        base = merge_depth(base, "L6" if task_type in {"review_revision", "submission_release"} else "L5")
    if profile.get("route_mode") == "quick" and DEPTH_ORDER.get(base, 0) > 4:
        return "L4"
    if profile.get("route_mode") == "strict":
        return merge_depth(base, "L5")
    return base


def should_select_subchain(
    rule: dict[str, Any],
    task_type: str,
    stage: str,
    passport: dict[str, Any],
    blockers: list[dict[str, str]],
    intent: str | None,
) -> bool:
    text = task_signal_text(intent, passport)
    targets = target_values(passport)
    kinds = material_kinds(passport)
    article_ingest = has_article_ingest_signal(text)
    data_ingest = has_data_ingest_signal(text)
    if task_type == "problem_resolution":
        return rule["id"] == "P10"
    if task_type in rule.get("task_types", []):
        return True
    if task_type != "content_ingest" and rule["id"] in PRIMARY_STAGE_SUBCHAINS.get(stage, set()) and stage in rule.get("stages", []):
        return True
    if rule["id"] == "P1" and any("research question" in item.get("text", "").lower() for item in blockers):
        return True
    if rule["id"] == "P2" and any(token in text for token in TASK_KEYWORDS["literature"]):
        return True
    if rule["id"] == "P2" and task_type == "content_ingest" and (article_ingest or not data_ingest):
        return True
    if rule["id"] == "P3" and active_claims(passport):
        return True
    if rule["id"] == "P4" and any(token in text for token in TASK_KEYWORDS["design_compliance"]):
        return True
    if rule["id"] == "P5" and (kinds & {"code", "script", "notebook", "dataset", "data"} or any(token in text for token in TASK_KEYWORDS["execution"])):
        return True
    if rule["id"] == "P5" and task_type == "content_ingest" and (data_ingest or not article_ingest):
        return True
    if rule["id"] == "P6" and ("figure" in targets or kinds & {"results", "analysis", "table", "dataset", "data"}):
        return True
    if rule["id"] == "P7" and task_type != "content_ingest" and (targets & {"paper", "manuscript", "docx", "pdf"} or any(token in text for token in TASK_KEYWORDS["writing_formatting"])):
        return True
    if rule["id"] == "P8" and (kinds & {"reviewer-comments", "review-comments", "decision-letter", "reviews"} or has_review_revision_signal(text)):
        return True
    if rule["id"] == "P9" and (targets & {"slides", "ppt", "patent"} or any(token in text for token in TASK_KEYWORDS["submission_release"])):
        return True
    return False


def selected_subchains(
    task_type: str,
    state: dict[str, Any],
    passport: dict[str, Any],
    blockers: list[dict[str, str]],
    intent: str | None = None,
) -> list[dict[str, Any]]:
    stage = state.get("current_stage", "INTAKE")
    selected: list[dict[str, Any]] = []
    for rule in SUBCHAIN_RULES:
        if should_select_subchain(rule, task_type, stage, passport, blockers, intent):
            item = dict(rule)
            item["depth"] = rule.get("default_depth", "L2")
            item["execution_mode"] = "audit" if item["depth"] == "L6" else "parallel-ready" if item["id"] in {"P2", "P5", "P6"} else "sequential"
            selected.append(item)
    if not selected:
        fallback = next((rule for rule in SUBCHAIN_RULES if stage in rule.get("stages", [])), SUBCHAIN_RULES[0])
        item = dict(fallback)
        item["depth"] = fallback.get("default_depth", "L2")
        item["execution_mode"] = "sequential"
        selected.append(item)
    return selected


def graph_edges(subchains: list[dict[str, Any]], blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = [
        {"from": "N0", "to": "N1", "condition": "always"},
        {"from": "N1", "to": "N2", "condition": "task classified"},
        {"from": "N2", "to": "N3", "condition": "depth assigned"},
        {"from": "N3", "to": "N4", "condition": "preflight complete"},
    ]
    for chain in subchains:
        chain_id = chain["id"]
        edges.extend(
            [
                {"from": "N4", "to": chain_id, "condition": chain.get("execution_mode", "sequential")},
                {"from": chain_id, "to": "N5", "condition": "subchain output produced"},
            ]
        )
    edges.extend(
        [
            {"from": "N5", "to": "N6", "condition": "artifacts registered"},
            {"from": "N6", "to": "N7", "condition": "ledgers updated"},
            {"from": "N7", "to": "N8", "condition": "gate passed"},
        ]
    )
    if blockers:
        edges.append({"from": "N7", "to": "N9", "condition": "gate failed or blocker present"})
        for chain in subchains:
            for target in chain.get("feedback_on_fail", []):
                edges.append({"from": "N9", "to": target, "condition": f"repair via {chain['id']}"})
    return edges


def capability_map_for_subchains(subchains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    controller = dict(CAPABILITY_MATRIX["tool:deep-loop-router"])
    controller["id"] = "tool:deep-loop-router"
    rows.append(controller)
    seen.add("tool:deep-loop-router")
    for controller_id in ["tool:research-council-reviewer", "tool:adversarial-gate-reviewer"]:
        controller = dict(CAPABILITY_MATRIX[controller_id])
        controller["id"] = controller_id
        rows.append(controller)
        seen.add(controller_id)
    for chain in subchains:
        for capability_id in list(chain.get("capability_ids", [])) + list(chain.get("missing_capability_ids", [])):
            if capability_id in seen:
                continue
            seen.add(capability_id)
            info = dict(CAPABILITY_MATRIX.get(capability_id, {}))
            info.setdefault("kind", "unknown")
            info.setdefault("status", "unknown")
            info.setdefault("name", capability_id)
            info["id"] = capability_id
            rows.append(info)
    return rows


def missing_tools_for_subchains(subchains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    seen: set[str] = set()
    for chain in subchains:
        for capability_id in chain.get("missing_capability_ids", []):
            if capability_id in seen:
                continue
            seen.add(capability_id)
            info = dict(CAPABILITY_MATRIX.get(capability_id, {"name": capability_id, "status": "missing"}))
            info["id"] = capability_id
            missing.append(info)
    return missing


TASK_TYPE_LABELS: dict[str, str] = {
    "intake": "project intake and state setup",
    "scoping": "research question scoping",
    "content_ingest": "content ingest and material packaging",
    "problem_resolution": "problem diagnosis, expert review, isolated testing, and gated promotion",
    "literature": "literature discovery and evidence synthesis",
    "claim_synthesis": "claim and contribution synthesis",
    "design_compliance": "method, experiment, and compliance design",
    "execution": "code, experiment, or simulation execution",
    "analysis_visualization": "analysis, statistics, tables, and figures",
    "writing_formatting": "manuscript writing, citation, and formatting",
    "review_revision": "review, revision, rebuttal, and integrity repair",
    "submission_release": "submission, publication, release, or reuse",
}

DEEP_LOOP_GATE_DECISIONS = {
    "route_next",
    "retry_same_route",
    "escalate_problem_loop",
    "pause_for_human",
}

ROUTE_AGENT_CHOICES = {"none", "codex"}

DEEP_LOOP_PASS_TRANSITIONS: dict[str, list[str]] = {
    "P1": ["P2", "P4"],
    "P2": ["P3", "P4"],
    "P3": ["P7", "P8"],
    "P4": ["P5"],
    "P5": ["P6"],
    "P6": ["P3", "P7"],
    "P7": ["P8", "P9"],
    "P8": ["P7", "P9"],
    "P9": [],
    "P10": ["P5", "P8"],
}

DEEP_LOOP_HUMAN_REVIEW_KEYWORDS = [
    "credential",
    "secret",
    "api key",
    "payment",
    "privacy",
    "restricted",
    "consent",
    "irb",
    "human approval",
    "manual",
    "copyright",
    "\u5bc6\u94a5",
    "\u9690\u79c1",
    "\u6388\u6743",
    "\u4eba\u5de5",
    "\u540c\u610f",
    "\u4ed8\u6b3e",
]

DEEP_LOOP_SUBCHAIN_BY_ID: dict[str, dict[str, Any]] = {str(rule["id"]): rule for rule in SUBCHAIN_RULES}

SUBCHAIN_AGENT_SPECS: dict[str, dict[str, Any]] = {
    "P1": {
        "agent_id": "p1_scope_head_agent",
        "subchain_id": "P1",
        "title": "Scope and Research Question Head Agent",
        "mission": "Convert rough goals into an answerable research question, scope boundary, and initial loop route.",
        "entry_read": [".research-loop/state.json", ".research-loop/material-passport.json", "latest handoff/checkpoint if present"],
        "planning_mode": "branch-and-bound scoping with explicit can-do and cannot-prove boundaries",
        "tool_policy": ["prompt-normalizer", "storage-policy", "academic-research-suite", "nature-academic-search"],
        "required_outputs": ["research question brief", "scope boundaries", "open questions", "initial route graph"],
        "quality_vector": ["objective_gap", "method_validity", "uncertainty_level", "handoff_completeness"],
        "failure_policy": "Retry P1 when the goal is ambiguous; escalate to P10 when the objective is internally inconsistent or infeasible.",
        "handoff_contract": ["active research question", "scope boundaries", "known missing inputs", "recommended next subchains"],
    },
    "P2": {
        "agent_id": "p2_literature_evidence_head_agent",
        "subchain_id": "P2",
        "title": "Literature and Evidence Head Agent",
        "mission": "Turn search targets and source material into verified metadata, evidence records, and a reading matrix.",
        "entry_read": [".research-loop/material-passport.json", ".research-loop/evidence-ledger.jsonl", "source-hub outputs", "ingest reports"],
        "planning_mode": "source-first retrieval with dedupe and evidence ledger updates",
        "tool_policy": ["research-source-hub", "content-ingest", "zotero-bridge", "nature-academic-search", "pdf", "nature-reader", "llm-wiki"],
        "required_outputs": ["bibliography", "source metadata", "evidence ledger records", "reading matrix", "counterevidence notes"],
        "quality_vector": ["evidence_integrity", "artifact_readiness", "uncertainty_level", "handoff_completeness"],
        "failure_policy": "Retry P2 for weak search coverage; route to P3 for claim conflicts; escalate to P10 when evidence cannot support the objective.",
        "handoff_contract": ["verified sources", "evidence ids", "unverified items", "claim candidates", "counterevidence"],
    },
    "P3": {
        "agent_id": "p3_claim_contribution_head_agent",
        "subchain_id": "P3",
        "title": "Claim and Contribution Head Agent",
        "mission": "Build auditable claims, novelty judgments, and claim-to-evidence links.",
        "entry_read": [".research-loop/material-passport.json", ".research-loop/evidence-ledger.jsonl", "reading matrix", "latest literature handoff"],
        "planning_mode": "multi-hypothesis claim mapping with competing explanations",
        "tool_policy": ["claim-evidence-verifier", "academic-research-suite", "nature-citation", "nature-reviewer"],
        "required_outputs": ["claim map", "novelty audit", "claim evidence links", "alternative explanations"],
        "quality_vector": ["objective_gap", "evidence_integrity", "novelty_risk", "uncertainty_level", "failure_mode_risk"],
        "failure_policy": "Route back to P2 for missing evidence; escalate to P10 when the claimed contribution collapses or conflicts persist.",
        "handoff_contract": ["supported claims", "unsupported claims", "novelty risks", "citation requirements", "revision targets"],
    },
    "P4": {
        "agent_id": "p4_method_compliance_head_agent",
        "subchain_id": "P4",
        "title": "Method and Compliance Head Agent",
        "mission": "Design reproducible methods, experiments, statistics, and data/compliance plans.",
        "entry_read": [".research-loop/state.json", ".research-loop/material-passport.json", "claim map", "data constraints"],
        "planning_mode": "method selection with explicit feasibility, compliance, and metric checks",
        "tool_policy": ["academic-research-suite", "nature-data", "prototype", "ethics-compliance-gate"],
        "required_outputs": ["protocol", "experiment plan", "statistics plan", "data management plan", "compliance flags"],
        "quality_vector": ["method_validity", "artifact_readiness", "human_blocker", "failure_mode_risk", "handoff_completeness"],
        "failure_policy": "Route to P1/P3 for objective-method mismatch; escalate to P10 or human checkpoint for compliance blockers.",
        "handoff_contract": ["method rationale", "metrics", "data requirements", "compliance status", "execution gate"],
    },
    "P5": {
        "agent_id": "p5_execution_head_agent",
        "subchain_id": "P5",
        "title": "Execution and Provenance Head Agent",
        "mission": "Run code, data processing, notebooks, and commands with captured provenance and failure logs.",
        "entry_read": [".research-loop/state.json", ".research-loop/storage-policy.json", "command plan", "data/code materials"],
        "planning_mode": "reproducible execution with run logs before interpretation",
        "tool_policy": ["research-loop run", "auto-loop-runner", "content-ingest", "diagnose", "tdd", "github", "hugging-face"],
        "required_outputs": ["run logs", "failure logs", "datasets", "code artifacts", "provenance records"],
        "quality_vector": ["artifact_readiness", "failure_mode_risk", "handoff_completeness", "objective_gap"],
        "failure_policy": "Retry P5 for command failures; route to P4 for design/data mismatch; escalate to P10 for environment or dependency blockers.",
        "handoff_contract": ["commands run", "exit codes", "log paths", "produced artifacts", "known failures"],
    },
    "P6": {
        "agent_id": "p6_analysis_figure_head_agent",
        "subchain_id": "P6",
        "title": "Analysis, Statistics, and Figure Head Agent",
        "mission": "Transform results into valid analysis, uncertainty statements, tables, figures, and legends.",
        "entry_read": ["run logs", "data/results artifacts", "analysis scripts", ".research-loop/evidence-ledger.jsonl"],
        "planning_mode": "analysis validation with uncertainty and figure traceability checks",
        "tool_policy": ["academic-research-suite", "nature-figure", "spreadsheets", "pdf"],
        "required_outputs": ["analysis report", "tables", "figures", "figure legends", "uncertainty note"],
        "quality_vector": ["analysis_validity", "artifact_readiness", "method_validity", "uncertainty_level", "failure_mode_risk"],
        "failure_policy": "Route to P5 for data/run defects; route to P3 for interpretation defects; escalate to P10 for statistical or causal validity risks.",
        "handoff_contract": ["validated results", "figure/table paths", "uncertainty limits", "interpretation constraints"],
    },
    "P7": {
        "agent_id": "p7_writing_citation_head_agent",
        "subchain_id": "P7",
        "title": "Writing and Citation Head Agent",
        "mission": "Write target-ready text under evidence, citation, and format constraints.",
        "entry_read": ["research question", "claim map", ".research-loop/evidence-ledger.jsonl", "target output profile"],
        "planning_mode": "evidence-constrained drafting with citation and format gates",
        "tool_policy": ["claim-evidence-verifier", "academic-research-suite", "nature-writing", "nature-citation", "nature-polishing", "word", "latex", "pdf"],
        "required_outputs": ["outline", "manuscript draft", "citations", "DOCX/LaTeX/PDF outputs"],
        "quality_vector": ["evidence_integrity", "artifact_readiness", "novelty_risk", "handoff_completeness", "objective_gap"],
        "failure_policy": "Route to P2/P3 for missing support; retry P7 for structure/format defects; escalate to P10 for unrecoverable narrative or integrity risk.",
        "handoff_contract": ["draft path", "citation status", "unsupported segments", "format target", "review checklist"],
    },
    "P8": {
        "agent_id": "p8_review_integrity_head_agent",
        "subchain_id": "P8",
        "title": "Review, Revision, and Integrity Head Agent",
        "mission": "Simulate review, audit integrity, and produce revision strategy before finalization.",
        "entry_read": ["draft artifacts", "figures/tables", ".research-loop/evidence-ledger.jsonl", "target venue", "review comments if present"],
        "planning_mode": "multi-perspective critique with novelty, rigor, evidence, and limitation checks",
        "tool_policy": ["claim-evidence-verifier", "academic-research-suite", "nature-reviewer", "nature-response", "nature-citation", "gmail", "google-drive"],
        "required_outputs": ["review report", "revision roadmap", "integrity report", "response plan"],
        "quality_vector": ["evidence_integrity", "analysis_validity", "novelty_risk", "failure_mode_risk", "handoff_completeness"],
        "failure_policy": "Route to P2/P3/P6/P7 for local defects; escalate to P10 for system-level integrity, novelty, or rebuttal risks.",
        "handoff_contract": ["review findings", "revision actions", "integrity risks", "accepted limitations", "release blockers"],
    },
    "P9": {
        "agent_id": "p9_release_reuse_head_agent",
        "subchain_id": "P9",
        "title": "Submission, Publication, and Reuse Head Agent",
        "mission": "Package final research outputs for submission, release, reuse, and follow-on work.",
        "entry_read": ["final draft", "figures", "data/code availability", "submission target", "latest integrity report"],
        "planning_mode": "release checklist with provenance and downstream reuse planning",
        "tool_policy": ["zotero-bridge", "llm-wiki", "presentations", "nature-paper2ppt", "nature-paper-to-patent", "github", "google-drive", "gmail", "linear"],
        "required_outputs": ["submission package", "cover letter", "slides", "release notes", "reuse seeds"],
        "quality_vector": ["artifact_readiness", "evidence_integrity", "handoff_completeness", "failure_mode_risk", "human_blocker"],
        "failure_policy": "Route to P7/P8 for package or integrity defects; escalate to P10 for publication, repository, or provenance blockers.",
        "handoff_contract": ["package manifest", "release paths", "availability statements", "reuse opportunities", "remaining blockers"],
    },
    "P10": {
        "agent_id": "p10_problem_expert_head_agent",
        "subchain_id": "P10",
        "title": "Problem Resolution and Expert Panel Head Agent",
        "mission": "Diagnose blockers in isolation, construct experts, test candidate fixes, and gate promotion into the main loop.",
        "entry_read": ["problem statement", "failure logs", ".research-loop/state.json", ".research-loop/material-passport.json", "available test commands"],
        "planning_mode": "isolated lab diagnosis with expert panel and promotion gate",
        "tool_policy": ["problem-loop", "storage-policy", "auto-loop-runner", "diagnose", "tdd", "research-loop"],
        "required_outputs": ["problem context snapshot", "expert panel", "isolated lab artifacts", "test logs", "adjustment plan", "promotion gate"],
        "quality_vector": ["failure_mode_risk", "artifact_readiness", "method_validity", "human_blocker", "handoff_completeness"],
        "failure_policy": "Continue P10 until the problem is reproduced, resolved, or blocked by owner-only authority.",
        "handoff_contract": ["root-cause hypothesis", "expert recommendations", "test evidence", "promotion decision", "safe patch scope"],
    },
}


def active_next_actions(passport: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in passport.get("next_actions") or []
        if isinstance(item, dict) and item.get("status") in {"todo", "in-progress", "blocked"}
    ]


def prompt_missing_slots(task_type: str, state: dict[str, Any], passport: dict[str, Any], cwd: Path) -> list[dict[str, str]]:
    profile = passport.get("profile") or {}
    kinds = material_kinds(passport)
    targets = target_values(passport)
    evidence_records = current_evidence_records(cwd)
    missing: list[dict[str, str]] = []
    if not passport.get("project_title"):
        missing.append({"slot": "project_title", "severity": "medium", "why": "Downstream agents need a stable project label."})
    if not passport.get("research_question") and task_type not in {"intake", "scoping", "content_ingest"}:
        missing.append({"slot": "research_question", "severity": "high", "why": "Later-stage work needs an active research question or objective."})
    if not targets and task_type in {"writing_formatting", "review_revision", "submission_release", "analysis_visualization"}:
        missing.append({"slot": "output_targets", "severity": "medium", "why": "Output type changes routing, formatting, and quality gates."})
    if task_type in {"literature", "claim_synthesis", "writing_formatting", "review_revision"} and not passport.get("materials"):
        missing.append({"slot": "materials", "severity": "medium", "why": "Literature, claims, writing, and review should be grounded in recorded sources."})
    if task_type in {"claim_synthesis", "writing_formatting", "review_revision"} and not active_claims(passport):
        missing.append({"slot": "key_claims", "severity": "medium", "why": "Drafting and review need explicit claims to audit."})
    if task_type in {"writing_formatting", "review_revision", "submission_release"} and not evidence_records:
        missing.append({"slot": "evidence_records", "severity": "high", "why": "Final text should not advance without evidence records."})
    if task_type in {"analysis_visualization", "execution"} and not ({"dataset", "data", "code", "script", "notebook", "results"} & kinds):
        missing.append({"slot": "data_or_code_materials", "severity": "medium", "why": "Execution and analysis need recorded data, code, notebooks, or results."})
    if task_type in {"writing_formatting", "review_revision", "submission_release"} and not profile.get("target_venue"):
        missing.append({"slot": "target_venue", "severity": "low", "why": "Venue affects format, claims, citations, figures, and response style."})
    if task_type in {"writing_formatting", "review_revision", "submission_release"} and not profile.get("citation_style"):
        missing.append({"slot": "citation_style", "severity": "low", "why": "Citation style affects formatting and reference checks."})
    if state.get("current_stage") in {"REVIEW", "REVISION_FINALIZE"} and not ({"reviewer-comments", "review-comments", "decision-letter", "reviews"} & kinds):
        missing.append({"slot": "review_materials", "severity": "medium", "why": "Revision routing works best with recorded reviewer comments or decision letters."})
    return missing


def project_context_payload(cwd: Path, state: dict[str, Any], passport: dict[str, Any]) -> dict[str, Any]:
    profile = passport.get("profile") or {}
    evidence_records = current_evidence_records(cwd)
    return {
        "project_root": psafe(cwd),
        "project_id": state.get("project_id"),
        "stage": state.get("current_stage", "INTAKE"),
        "title": passport.get("project_title"),
        "domain": passport.get("domain"),
        "summary": passport.get("project_summary"),
        "research_question": passport.get("research_question"),
        "output_targets": passport.get("output_targets") or [],
        "target_venue": profile.get("target_venue"),
        "citation_style": profile.get("citation_style"),
        "verification_strictness": profile.get("verification_strictness"),
        "route_mode": profile.get("route_mode"),
        "counts": {
            "materials": len(passport.get("materials") or []),
            "claims": len(active_claims(passport)),
            "evidence": len(evidence_records),
            "open_risks": len(open_risks(passport)),
            "active_next_actions": len(active_next_actions(passport)),
        },
        "material_kinds": sorted(material_kinds(passport)),
    }


def downstream_prompt_from_payload(payload: dict[str, Any]) -> str:
    context = payload["project_context"]
    missing = payload["missing_slots"]
    execution_profile = payload.get("execution_profile") or {}
    harness = payload.get("harness_protocol") or {}
    prompt_lines = [
        "Use the project-local research loop before acting.",
        "",
        "Raw user request:",
        payload.get("raw_input") or "(not provided)",
        "",
        "Interpreted task:",
        f"- Task type: {payload.get('task_type')} ({TASK_TYPE_LABELS.get(payload.get('task_type'), 'research task')})",
        f"- Chain depth: {payload.get('depth_level')}",
        f"- Execution profile: {execution_profile.get('id', 'standard_loop')} ({execution_profile.get('label', 'standard research loop')})",
        f"- Current stage: {context.get('stage')}",
        "",
        "Project context to preserve:",
        f"- Project root: {context.get('project_root')}",
        f"- Title: {context.get('title') or '(not set)'}",
        f"- Domain: {context.get('domain') or '(not set)'}",
        f"- Active research question: {context.get('research_question') or '(not set)'}",
        f"- Output targets: {', '.join(context.get('output_targets') or []) or '(not set)'}",
        f"- Target venue: {context.get('target_venue') or '(not set)'}",
        f"- Citation style: {context.get('citation_style') or '(not set)'}",
        f"- Record counts: materials={context['counts']['materials']}, claims={context['counts']['claims']}, evidence={context['counts']['evidence']}, open_risks={context['counts']['open_risks']}",
        "",
        "Task prompt for the next agent/tool:",
        payload.get("working_prompt") or payload.get("routing_intent") or payload.get("raw_input") or "(derive the task from loop state)",
        "",
        "Missing or weak inputs to handle explicitly:",
    ]
    if missing:
        prompt_lines.extend(f"- [{item['severity']}] {item['slot']}: {item['why']}" for item in missing)
    else:
        prompt_lines.append("- None detected by the local loop.")
    prompt_lines.extend(["", "Harness protocol to follow before claiming completion:"])
    if harness.get("validation_surfaces"):
        prompt_lines.append("- Choose one validation surface before editing/running: " + "; ".join(str(item) for item in harness["validation_surfaces"]))
    case_contract = harness.get("case_contract") if isinstance(harness.get("case_contract"), dict) else {}
    if case_contract.get("fields"):
        prompt_lines.append("- If using reproducible cases, define: " + "; ".join(str(item) for item in case_contract["fields"]))
    feedback_summary = harness.get("feedback_summary") if isinstance(harness.get("feedback_summary"), dict) else {}
    if feedback_summary.get("preferred_metrics"):
        prompt_lines.append("- Feed gate decisions with: " + "; ".join(str(item) for item in feedback_summary["preferred_metrics"]))
    if harness.get("guardrails"):
        prompt_lines.extend(f"- {item}" for item in harness["guardrails"])
    if harness.get("report_fields"):
        prompt_lines.append("- Final report must cover: " + "; ".join(str(item) for item in harness["report_fields"]))
    prompt_lines.extend(
        [
            "",
            "Operating requirements:",
            "- Read `.research-loop/state.json` and `.research-loop/material-passport.json` before substantive work.",
            "- Do not fabricate sources, evidence, results, paths, or reviewer comments.",
            "- If a missing slot blocks the task, ask only the smallest necessary clarification or record a defer/assumption decision.",
            "- After work, update materials, claims, evidence, decisions, risks, and next actions as appropriate.",
        ]
    )
    return "\n".join(prompt_lines).rstrip()


def normalize_task_input(cwd: Path, state: dict[str, Any], passport: dict[str, Any], user_input: str | None = None) -> dict[str, Any]:
    raw = (user_input or "").strip()
    task_type = classify_task_type(state, passport, raw or None)
    issues = route_blockers(cwd, state, passport)
    blockers = [item for item in issues if item["severity"] == "blocking"]
    depth = assign_depth(task_type, state, passport, blockers, raw or None)
    execution_profile = classify_execution_profile(task_type, passport, raw or None)
    harness_protocol = harness_protocol_for_profile(execution_profile, task_type, depth)
    context = project_context_payload(cwd, state, passport)
    target_hint = ", ".join(context.get("output_targets") or []) or "research artifact"
    question_hint = context.get("research_question") or "the active research question is missing; first recover or define it"
    if raw:
        working_prompt = f"{raw}\n\nFrame this as {TASK_TYPE_LABELS.get(task_type, task_type)} for the current project. Ground the work in the active question: {question_hint}. Expected output target: {target_hint}."
    else:
        working_prompt = f"Continue {TASK_TYPE_LABELS.get(task_type, task_type)} for the current project. Ground the work in the active question: {question_hint}. Expected output target: {target_hint}."
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "raw_input": raw,
        "routing_intent": raw or TASK_TYPE_LABELS.get(task_type, task_type),
        "working_prompt": working_prompt,
        "task_type": task_type,
        "depth_level": depth,
        "execution_profile": execution_profile,
        "harness_protocol": harness_protocol,
        "project_context": context,
        "missing_slots": prompt_missing_slots(task_type, state, passport, cwd),
        "blockers": blockers,
        "warnings": [item for item in issues if item["severity"] != "blocking"],
    }
    payload["downstream_prompt"] = downstream_prompt_from_payload(payload)
    return payload


def normalized_prompt_markdown(payload: dict[str, Any]) -> list[str]:
    context = payload["project_context"]
    lines = [
        "# Research Loop Normalized Prompt",
        "",
        f"- Generated at UTC: {payload['timestamp']}",
        f"- Task type: `{payload['task_type']}`",
        f"- Chain depth: `{payload['depth_level']}`",
        f"- Execution profile: `{(payload.get('execution_profile') or {}).get('id', 'standard_loop')}`",
        f"- Stage: `{context.get('stage')}`",
        "",
        "## Raw Input",
        "",
        payload.get("raw_input") or "(not provided)",
        "",
        "## Project Context Used",
        "",
        f"- Title: {context.get('title') or '(not set)'}",
        f"- Domain: {context.get('domain') or '(not set)'}",
        f"- Research question: {context.get('research_question') or '(not set)'}",
        f"- Output targets: {', '.join(context.get('output_targets') or []) or '(not set)'}",
        f"- Target venue: {context.get('target_venue') or '(not set)'}",
        f"- Citation style: {context.get('citation_style') or '(not set)'}",
        "",
        "## Missing Or Weak Inputs",
        "",
    ]
    if payload["missing_slots"]:
        lines.extend(f"- [{item['severity']}] `{item['slot']}`: {item['why']}" for item in payload["missing_slots"])
    else:
        lines.append("- None detected.")
    harness = payload.get("harness_protocol") or {}
    lines.extend(["", "## Harness Protocol", ""])
    lines.append("- Validation surfaces:")
    lines.extend(f"  - {item}" for item in harness.get("validation_surfaces") or [])
    case_contract = harness.get("case_contract") if isinstance(harness.get("case_contract"), dict) else {}
    lines.append("- Case contract fields:")
    lines.extend(f"  - {item}" for item in case_contract.get("fields") or [])
    feedback_summary = harness.get("feedback_summary") if isinstance(harness.get("feedback_summary"), dict) else {}
    lines.append("- Gate feedback metrics:")
    lines.extend(f"  - {item}" for item in feedback_summary.get("preferred_metrics") or [])
    lines.append("- Guardrails:")
    lines.extend(f"  - {item}" for item in harness.get("guardrails") or [])
    lines.append("- Report fields:")
    lines.extend(f"  - {item}" for item in harness.get("report_fields") or [])
    lines.extend(["", "## Downstream Prompt", "", payload["downstream_prompt"]])
    return lines


def build_route_graph(cwd: Path, state: dict[str, Any], passport: dict[str, Any], intent: str | None = None) -> dict[str, Any]:
    issues = route_blockers(cwd, state, passport)
    blockers = [item for item in issues if item["severity"] == "blocking"]
    warnings = [item for item in issues if item["severity"] != "blocking"]
    normalized = normalize_task_input(cwd, state, passport, intent)
    route_intent = normalized.get("routing_intent") or intent
    task_type = normalized["task_type"]
    depth = normalized["depth_level"]
    subchains = selected_subchains(task_type, state, passport, blockers, route_intent)
    for chain in subchains:
        chain["depth"] = merge_depth(chain.get("depth", "L0"), depth if DEPTH_ORDER.get(depth, 0) >= 5 and chain["id"] in {"P3", "P7", "P8", "P9"} else chain.get("depth", "L0"))
    return {
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "stage": state.get("current_stage", "INTAKE"),
        "intent": intent,
        "normalized_input": normalized,
        "task_type": task_type,
        "depth_level": depth,
        "execution_profile": normalized.get("execution_profile"),
        "harness_protocol": normalized.get("harness_protocol"),
        "profile": passport.get("profile") or {},
        "active_question": passport.get("research_question"),
        "output_targets": passport.get("output_targets") or [],
        "material_kinds": sorted(material_kinds(passport)),
        "blockers": blockers,
        "warnings": warnings,
        "shared_nodes": SHARED_ROUTE_NODES,
        "subchains": subchains,
        "edges": graph_edges(subchains, blockers),
        "recommendations": route_recommendations(cwd, state, passport, route_intent),
        "capability_map": capability_map_for_subchains(subchains),
        "missing_tools": missing_tools_for_subchains(subchains),
    }


def capability_matrix_payload() -> dict[str, Any]:
    available = [dict({"id": key}, **value) for key, value in CAPABILITY_MATRIX.items() if value.get("status") != "missing"]
    missing = [dict({"id": key}, **value) for key, value in CAPABILITY_MATRIX.items() if value.get("status") == "missing"]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "shared_nodes": SHARED_ROUTE_NODES,
        "subchains": SUBCHAIN_RULES,
        "available_capabilities": available,
        "missing_tools": missing,
    }


def route_blockers(cwd: Path, state: dict[str, Any], passport: dict[str, Any]) -> list[dict[str, str]]:
    stage = state.get("current_stage", "INTAKE")
    profile = passport.get("profile") or {}
    strictness = profile.get("verification_strictness", "standard")
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if STAGE_ORDER.get(stage, 0) >= STAGE_ORDER["LITERATURE"] and not passport.get("research_question"):
        blockers.append(
            {
                "severity": "blocking",
                "text": "No active research question is recorded. Route back to SCOPING before literature, design, writing, or review work.",
            }
        )

    if stage in {"WRITING", "REVIEW", "REVISION_FINALIZE"}:
        unsupported = [
            claim
            for claim in active_claims(passport)
            if not claim.get("evidence_ids") and claim.get("status") in {"proposed", "supported", "contested", "unverified"}
        ]
        if unsupported:
            blockers.append(
                {
                    "severity": "blocking",
                    "text": f"{len(unsupported)} active claim(s) have no evidence ids. Record evidence before drafting, review, or finalization.",
                }
            )

    evidence_records = list(current_evidence_records(cwd).values())
    failed_evidence = [record for record in evidence_records if record.get("status") == "failed"]
    unverified_evidence = [record for record in evidence_records if record.get("status") in {"unverified", "partial"}]
    if failed_evidence and stage in {"REVIEW", "REVISION_FINALIZE"}:
        blockers.append(
            {
                "severity": "blocking",
                "text": f"{len(failed_evidence)} evidence record(s) failed verification. Resolve before review/finalization.",
            }
        )
    if strictness == "strict" and unverified_evidence and stage in {"WRITING", "REVIEW", "REVISION_FINALIZE"}:
        blockers.append(
            {
                "severity": "blocking",
                "text": f"Strict verification is enabled and {len(unverified_evidence)} evidence record(s) are not verified.",
            }
        )

    high_risks = [risk for risk in open_risks(passport) if risk.get("severity") in {"high", "blocking"}]
    if high_risks and stage in {"REVIEW", "REVISION_FINALIZE"}:
        blockers.append(
            {
                "severity": "blocking",
                "text": f"{len(high_risks)} high/blocking open risk(s) exist. Mitigate, accept explicitly, or defer with rationale before final routing.",
            }
        )
    elif high_risks:
        warnings.append(
            {
                "severity": "warning",
                "text": f"{len(high_risks)} high/blocking open risk(s) exist. Keep them visible in the next checkpoint.",
            }
        )

    kinds = material_kinds(passport)
    targets = target_values(passport)
    if stage in {"EXECUTION", "ANALYSIS"} and not ({"dataset", "data", "code", "script", "notebook"} & kinds):
        warnings.append(
            {
                "severity": "warning",
                "text": "No dataset/code material is recorded. Record the relevant material before interpreting results.",
            }
        )
    if "figure" in targets and not ({"dataset", "data", "table", "results", "analysis"} & kinds) and stage in {"ANALYSIS", "SYNTHESIS", "WRITING"}:
        blockers.append(
            {
                "severity": "blocking",
                "text": "Figure output is targeted, but no dataset/data/results material is recorded.",
            }
        )
    if stage == "LITERATURE" and not passport.get("materials"):
        warnings.append(
            {
                "severity": "warning",
                "text": "No literature/material records exist yet. Start with source discovery and material recording.",
            }
        )
    if profile.get("data_sensitivity") in {"sensitive", "restricted"}:
        warnings.append(
            {
                "severity": "warning",
                "text": f"Data sensitivity is {profile.get('data_sensitivity')}; prefer local processing and avoid external uploads without explicit consent.",
            }
        )

    return blockers + warnings


def has_kind(passport: dict[str, Any], aliases: set[str]) -> bool:
    return bool(material_kinds(passport) & aliases)


def route_recommendations(cwd: Path, state: dict[str, Any], passport: dict[str, Any], intent: str | None = None) -> list[dict[str, Any]]:
    stage = state.get("current_stage", "INTAKE")
    profile = passport.get("profile") or {}
    recommendations = list(ROUTE_RULES.get(stage, []))
    intent_text = (intent or "").lower()
    targets = target_values(passport)
    for token in ["paper", "manuscript", "figure", "docx", "pdf", "slides", "ppt", "patent", "knowledge-base"]:
        if token in targets or token in intent_text:
            recommendations.extend(TARGET_ROUTE_RULES.get(token, []))
    if "reviewer" in intent_text or "comments" in intent_text or "rebuttal" in intent_text:
        recommendations.append(
            {
                "skill": "nature-response",
                "mode": "reviewer-response",
                "purpose": "Structure reviewer comments and draft response/revision strategy.",
                "when": "Use when external reviewer comments are available.",
            }
        )
    if "citation" in intent_text or "reference" in intent_text:
        recommendations.append(
            {
                "skill": "nature-citation",
                "mode": "citation-grounding",
                "purpose": "Check claim-to-reference alignment and add strict citations.",
                "when": "Use when citation integrity is the current task.",
            }
        )
    if has_kind(passport, {"pdf", "paper-pdf", "article-pdf"}) and stage in {"LITERATURE", "SYNTHESIS", "WRITING", "REVIEW"}:
        recommendations.insert(
            0,
            {
                "skill": "pdf",
                "mode": "paper-ingest",
                "purpose": "Extract text, tables, figures, and page-level evidence from recorded PDFs before synthesis.",
                "when": "Use because PDF materials are recorded in the passport.",
            },
        )
    if has_kind(passport, {"reviewer-comments", "review-comments", "decision-letter", "reviews"}) or any(token in intent_text for token in ["reviewer", "comments", "rebuttal", "response"]):
        recommendations.insert(
            0,
            {
                "skill": "nature-response",
                "mode": "reviewer-response",
                "purpose": "Structure reviewer/editor comments and build a response/revision plan.",
                "when": "Use because reviewer feedback is present or requested.",
            },
        )
    if active_claims(passport):
        unsupported_or_unverified = [
            claim
            for claim in active_claims(passport)
            if not claim.get("evidence_ids") or claim.get("status") in {"proposed", "unverified", "contested"}
        ]
        if unsupported_or_unverified and stage in {"SYNTHESIS", "WRITING", "REVIEW", "REVISION_FINALIZE"}:
            recommendations.insert(
                0,
                {
                    "skill": "nature-citation",
                    "mode": "claim-citation-alignment",
                    "purpose": "Ground active claims against verified citations before drafting or review.",
                    "when": "Use because some active claims are proposed, contested, unverified, or lack evidence ids.",
                },
            )
    evidence_records = list(current_evidence_records(cwd).values())
    if any(record.get("status") in {"unverified", "partial"} for record in evidence_records):
        recommendations.insert(
            0,
            {
                "skill": "nature-academic-search",
                "mode": "citation-verification",
                "purpose": "Resolve unverified or partial evidence records.",
                "when": "Use because the evidence ledger contains records that are not fully verified.",
            },
        )
    if target_values(passport) & {"figure"} and has_kind(passport, {"dataset", "data", "table", "results", "analysis"}):
        recommendations.insert(
            0,
            {
                "skill": "nature-figure",
                "mode": "publication-figure",
                "purpose": "Build or audit figure outputs from recorded data/results material.",
                "when": "Use because figure output is targeted and data/results material is available.",
            },
        )
    if profile.get("target_venue"):
        recommendations.append(
            {
                "skill": "research-loop",
                "mode": "checkpoint",
                "purpose": f"Keep route decisions aligned with target venue: {profile.get('target_venue')}.",
                "when": "Use after domain skill work to preserve target-specific decisions.",
            }
        )
    if profile.get("route_mode") == "quick":
        recommendations = [item for item in recommendations if item.get("skill") in {"research-loop", "academic-research-suite", "nature-academic-search", "pdf"}] or recommendations[:3]
    elif profile.get("route_mode") == "strict":
        recommendations.append(
            {
                "skill": "research-loop",
                "mode": "validate",
                "purpose": "Run structural validation after each routed stage because strict route mode is enabled.",
                "when": "Use after recording any new evidence, claims, materials, or decisions.",
            }
        )

    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, Any]] = []
    for item in recommendations:
        key = (str(item.get("skill")), str(item.get("mode")))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def route_markdown(cwd: Path, state: dict[str, Any], passport: dict[str, Any], intent: str | None = None) -> list[str]:
    graph = build_route_graph(cwd, state, passport, intent)
    profile = graph.get("profile") or {}
    execution_profile = graph.get("execution_profile") or {}
    harness = graph.get("harness_protocol") or {}
    blockers = graph["blockers"]
    warnings = graph["warnings"]
    recommendations = graph["recommendations"]
    next_actions = [
        item
        for item in passport.get("next_actions", []) or []
        if isinstance(item, dict) and item.get("status") in {"todo", "in-progress", "blocked"}
    ]

    lines = [
        "# Research Loop Route Plan",
        "",
        f"- Created at UTC: {graph['timestamp']}",
        f"- Project root: {cwd}",
        f"- Current stage: {graph['stage']}",
        f"- Task type: {graph['task_type']}",
        f"- Chain depth: {graph['depth_level']}",
        f"- Execution profile: {execution_profile.get('id', 'standard_loop')} ({execution_profile.get('label', 'standard research loop')})",
        f"- Active research question: {graph.get('active_question') or '(not set)'}",
        f"- Output targets: {', '.join(graph.get('output_targets') or []) or '(not set)'}",
        f"- Material kinds: {', '.join(graph.get('material_kinds') or []) or '(not set)'}",
        f"- Route mode: {profile.get('route_mode', 'standard')}",
        f"- Verification strictness: {profile.get('verification_strictness', 'standard')}",
        f"- Data sensitivity: {profile.get('data_sensitivity', 'normal')}",
    ]
    if intent:
        lines.append(f"- User intent: {intent}")

    normalized = graph.get("normalized_input") or {}
    if normalized.get("downstream_prompt"):
        lines.extend(["", "## Normalized Downstream Prompt", "", normalized["downstream_prompt"]])

    lines.extend(["", "## Harness Protocol", ""])
    lines.append("- Validation surfaces:")
    lines.extend(f"  - {item}" for item in harness.get("validation_surfaces") or [])
    case_contract = harness.get("case_contract") if isinstance(harness.get("case_contract"), dict) else {}
    lines.append("- Case contract fields:")
    lines.extend(f"  - {item}" for item in case_contract.get("fields") or [])
    feedback_summary = harness.get("feedback_summary") if isinstance(harness.get("feedback_summary"), dict) else {}
    lines.append("- Gate feedback metrics:")
    lines.extend(f"  - {item}" for item in feedback_summary.get("preferred_metrics") or [])
    lines.append("- Guardrails:")
    lines.extend(f"  - {item}" for item in harness.get("guardrails") or [])
    lines.append("- Report fields:")
    lines.extend(f"  - {item}" for item in harness.get("report_fields") or [])

    lines.extend(["", "## Shared Dispatcher Nodes", ""])
    for node in graph["shared_nodes"]:
        lines.append(f"- `{node['id']}` {node['name']}: {node['purpose']}")

    lines.extend(["", "## Selected Subchains", ""])
    for chain in graph["subchains"]:
        lines.append(f"- `{chain['id']}` {chain['name']} ({chain['depth']}, {chain['execution_mode']})")
        lines.append(f"  - Inputs: {', '.join(chain.get('required_inputs') or [])}")
        lines.append(f"  - Outputs: {', '.join(chain.get('outputs') or [])}")
        lines.append(f"  - Gates: {', '.join(chain.get('gates') or [])}")

    lines.extend(["", "## Gate Status", ""])
    if blockers:
        lines.append("Blocking issues are present. Do not advance to a later stage until they are resolved or explicitly deferred with rationale.")
        lines.append("")
        for item in blockers:
            lines.append(f"- [blocking] {item['text']}")
    else:
        lines.append("- No blocking route issues detected.")
    if warnings:
        lines.extend(["", "## Warnings", ""])
        for item in warnings:
            lines.append(f"- [warning] {item['text']}")

    lines.extend(["", "## Recommended Skill Route", ""])
    for index, item in enumerate(recommendations, start=1):
        lines.append(f"{index}. `{item.get('skill')}` / `{item.get('mode')}`")
        if item.get("workflow"):
            lines.append(f"   - Workflow: `{item.get('workflow')}`")
        lines.append(f"   - Purpose: {item.get('purpose')}")
        if item.get("when"):
            lines.append(f"   - Use when: {item.get('when')}")

    lines.extend(["", "## Capability Map", ""])
    for item in graph["capability_map"]:
        status = item.get("status", "unknown")
        kind = item.get("kind", "unknown")
        lines.append(f"- `{item['id']}` [{status}/{kind}] {item.get('use_for')}")

    if graph["missing_tools"]:
        lines.extend(["", "## Tooling Gaps To Add", ""])
        for item in graph["missing_tools"]:
            lines.append(f"- `{item['name']}` ({item.get('priority', 'P?')}): {item.get('use_for')}")

    lines.extend(["", "## Graph Edges", ""])
    for edge in graph["edges"]:
        lines.append(f"- `{edge['from']}` -> `{edge['to']}` when {edge.get('condition', 'ready')}")

    lines.extend(
        [
            "",
            "## Required Loop Reads Before Acting",
            "",
            "- `.research-loop/state.json`",
            "- `.research-loop/material-passport.json`",
            "- Latest `.research-loop/handoffs/*.md` if present",
            "- Latest `.research-loop/checkpoints/*.md` if present",
        ]
    )

    lines.extend(["", "## Active Next Actions", ""])
    if next_actions:
        for item in next_actions[:12]:
            lines.append(f"- [{item.get('status')}] {item.get('text')} ({item.get('stage')})")
    else:
        lines.append("- (No active next actions recorded.)")

    lines.extend(
        [
            "",
            "## Route Discipline",
            "",
            "- The research loop records state and recommends skills; it does not perform substantive research by itself.",
            "- For current facts, policies, citations, journal requirements, and source verification, use authoritative sources and record verification status.",
            "- After completing the routed work, record claims/evidence/decisions, run `validate`, then create a checkpoint or handoff.",
        ]
    )
    return lines


def command_route(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    graph = build_route_graph(cwd, state, passport, args.intent)
    output_format = args.format
    output = (
        json.dumps(graph, indent=2, ensure_ascii=True, default=str) + "\n"
        if output_format == "json"
        else "\n".join(route_markdown(cwd, state, passport, args.intent)).rstrip() + "\n"
    )
    if args.write:
        suffix = "json" if output_format == "json" else "md"
        path = reports_root(cwd) / f"{timestamp()}-route-plan.{suffix}"
        if output_format == "json":
            write_json(path, graph)
        else:
            write_lines(path, output.splitlines())
        append_jsonl(
            decisions_path(cwd),
            {
                "id": record_id("route", state.get("current_stage", "INTAKE") + (args.intent or "")),
                "timestamp": utc_now(),
                "type": "route_plan",
                "stage": state.get("current_stage", "INTAKE"),
                "intent": args.intent,
                "task_type": graph.get("task_type"),
                "depth_level": graph.get("depth_level"),
                "subchains": [item.get("id") for item in graph.get("subchains", [])],
                "path": psafe(path),
            },
        )
        print(f"Route plan: {path}")
    else:
        print(output)
    return 0


def normalize_quality_score(value: float | None) -> float | None:
    if value is None:
        return None
    score = float(value)
    if score > 1.0:
        score = score / 100.0
    return max(0.0, min(1.0, score))


def coerce_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    multiplier = 0.01 if text.endswith("%") else 1.0
    if text.endswith("%"):
        text = text[:-1].strip()
    try:
        return float(text) * multiplier
    except ValueError:
        return None


def coerce_int(value: Any) -> int | None:
    number = coerce_float(value)
    if number is None:
        return None
    return int(number)


def normalize_report_metric(value: Any) -> float | None:
    number = coerce_float(value)
    if number is None:
        return None
    if number > 1.0:
        number = number / 100.0
    return max(0.0, min(1.0, number))


def resolve_harness_report_path(cwd: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return path.resolve()


def merge_failure_tags(target: dict[str, int], value: Any) -> None:
    if isinstance(value, dict):
        for key, count in value.items():
            tag = str(key or "untagged")
            target[tag] = int(target.get(tag, 0)) + int(coerce_int(count) or 0)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                tag = str(item.get("tag") or item.get("name") or "untagged")
                count = int(coerce_int(item.get("count") or item.get("failures") or 1) or 1)
            else:
                tag = str(item or "untagged")
                count = 1
            target[tag] = int(target.get(tag, 0)) + count


def failed_cases_from_results(results: Any) -> list[dict[str, Any]]:
    failed: list[dict[str, Any]] = []
    if not isinstance(results, list):
        return failed
    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            continue
        passed = result.get("passed")
        if passed is None and "exit_code" in result:
            passed = result.get("exit_code") == 0
        if passed is True:
            continue
        case_id = result.get("case_id") or result.get("id") or result.get("name") or f"case-{index:02d}"
        tags = result.get("tags")
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            tags = []
        failed.append(
            {
                "case_id": str(case_id),
                "tags": [str(tag) for tag in tags],
                "score": coerce_float(result.get("score")),
                "error": result.get("error") or result.get("grading_message") or result.get("stderr_excerpt") or result.get("status"),
                "expected": result.get("expected"),
                "output": result.get("output"),
            }
        )
    return failed


def failure_tags_from_cases(cases: list[dict[str, Any]]) -> dict[str, int]:
    tags: dict[str, int] = {}
    for case in cases:
        case_tags = list(case.get("tags") or ["untagged"])
        for tag in case_tags or ["untagged"]:
            key = str(tag or "untagged")
            tags[key] = int(tags.get(key, 0)) + 1
    return tags


def select_harness_evaluation(payload: dict[str, Any]) -> dict[str, Any] | None:
    evaluations = payload.get("evaluations")
    if not isinstance(evaluations, list) or not evaluations:
        return None
    selected_name = payload.get("selected_candidate") or payload.get("selected")
    if selected_name:
        for evaluation in evaluations:
            if not isinstance(evaluation, dict):
                continue
            candidate = evaluation.get("candidate")
            candidate_name = candidate.get("name") if isinstance(candidate, dict) else candidate
            if str(candidate_name) == str(selected_name):
                return evaluation

    def rank(evaluation: Any) -> float:
        if not isinstance(evaluation, dict):
            return -1.0
        utility = coerce_float(evaluation.get("utility"))
        if utility is not None:
            return utility
        summary = evaluation.get("summary") if isinstance(evaluation.get("summary"), dict) else {}
        score = normalize_report_metric(summary.get("weighted_score"))
        return score if score is not None else -1.0

    candidates = [item for item in evaluations if isinstance(item, dict)]
    return max(candidates, key=rank) if candidates else None


def summarize_auto_loop_report(payload: dict[str, Any]) -> dict[str, Any] | None:
    rounds = payload.get("rounds")
    if not isinstance(rounds, list):
        return None
    rows: list[dict[str, Any]] = []
    for round_item in rounds:
        if not isinstance(round_item, dict):
            continue
        for group_name in ["executors", "tests"]:
            group = round_item.get(group_name)
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, dict):
                        rows.append({**item, "tags": [str(item.get("kind") or group_name)]})
    if not rows:
        return None
    failed = failed_cases_from_results(rows)
    case_count = len(rows)
    pass_count = case_count - len(failed)
    return {
        "case_count": case_count,
        "pass_count": pass_count,
        "pass_rate": pass_count / case_count if case_count else 0.0,
        "weighted_score": pass_count / case_count if case_count else 0.0,
        "failures_by_tag": failure_tags_from_cases(failed),
        "avg_latency_or_runtime": sum(float(item.get("elapsed_seconds") or 0.0) for item in rows) / case_count,
        "results": rows,
    }


def extract_harness_summary(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    selected = select_harness_evaluation(payload)
    if selected:
        summary = selected.get("summary") if isinstance(selected.get("summary"), dict) else {}
        return dict(summary), selected
    if isinstance(payload.get("summary"), dict):
        return dict(payload["summary"]), payload
    auto_summary = summarize_auto_loop_report(payload)
    if auto_summary:
        return auto_summary, auto_summary
    return dict(payload), payload


def harness_evidence_from_payload(report_path: Path, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "report_path": psafe(report_path),
            "status": "unparsed",
            "errors": ["Harness report JSON root is not an object."],
        }
    summary, source = extract_harness_summary(payload)
    results = source.get("results") if isinstance(source, dict) else None
    failed_cases = failed_cases_from_results(results)
    failures_by_tag: dict[str, int] = {}
    merge_failure_tags(failures_by_tag, summary.get("failures_by_tag"))
    if not failures_by_tag:
        failures_by_tag.update(failure_tags_from_cases(failed_cases))
    case_count = coerce_int(summary.get("case_count"))
    pass_count = coerce_int(summary.get("pass_count"))
    pass_rate = normalize_report_metric(summary.get("pass_rate"))
    weighted_score = normalize_report_metric(summary.get("weighted_score"))
    if case_count is None and isinstance(results, list):
        case_count = len(results)
    if pass_count is None and case_count is not None:
        pass_count = max(0, case_count - len(failed_cases))
    if pass_rate is None and case_count:
        pass_rate = (pass_count or 0) / case_count
    quality_score = weighted_score if weighted_score is not None else pass_rate
    latency = coerce_float(summary.get("avg_latency_or_runtime"))
    if latency is None:
        latency = coerce_float(summary.get("avg_latency_ms"))
    report_paths = [psafe(report_path)]
    for key in ["report", "json_report", "markdown_report", "paragraph_audit"]:
        if payload.get(key):
            report_paths.append(str(payload[key]))
    has_failures = bool(failures_by_tag) or bool(failed_cases) or (pass_rate is not None and pass_rate < 1.0)
    status = "fail" if has_failures else "pass"
    return {
        "report_path": psafe(report_path),
        "status": status,
        "selected_candidate": payload.get("selected_candidate") or payload.get("selected"),
        "case_count": case_count,
        "pass_count": pass_count,
        "pass_rate": pass_rate,
        "weighted_score": weighted_score,
        "quality_score": quality_score,
        "avg_latency_or_runtime": latency,
        "failures_by_tag": failures_by_tag,
        "failed_cases": failed_cases[:50],
        "report_paths": list(dict.fromkeys(report_paths)),
        "errors": [],
    }


def collect_harness_evidence(cwd: Path, report_values: list[str] | None) -> dict[str, Any]:
    reports = list(report_values or [])
    evidence_items: list[dict[str, Any]] = []
    errors: list[str] = []
    for value in reports:
        report_path = resolve_harness_report_path(cwd, str(value))
        if not report_path.exists():
            errors.append(f"Harness report not found: {psafe(report_path)}")
            continue
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001 - evidence adapter must report bad reports.
            errors.append(f"Cannot parse harness report {psafe(report_path)}: {type(exc).__name__}: {exc}")
            continue
        evidence_items.append(harness_evidence_from_payload(report_path, payload))
    failure_tags: dict[str, int] = {}
    report_paths: list[str] = []
    failed_cases: list[dict[str, Any]] = []
    quality_scores: list[float] = []
    case_count = 0
    pass_count = 0
    for item in evidence_items:
        merge_failure_tags(failure_tags, item.get("failures_by_tag"))
        report_paths.extend(str(path) for path in item.get("report_paths") or [item.get("report_path")])
        failed_cases.extend(list(item.get("failed_cases") or []))
        quality = normalize_report_metric(item.get("quality_score"))
        if quality is not None:
            quality_scores.append(quality)
        if item.get("case_count") is not None:
            case_count += int(item.get("case_count") or 0)
        if item.get("pass_count") is not None:
            pass_count += int(item.get("pass_count") or 0)
    pass_rate = (pass_count / case_count) if case_count else None
    quality_score = min(quality_scores) if quality_scores else pass_rate
    has_failures = bool(errors) or bool(failure_tags) or bool(failed_cases) or (pass_rate is not None and pass_rate < 1.0)
    summary_bits = []
    if pass_rate is not None:
        summary_bits.append(f"pass_rate={pass_rate:.3f}")
    if quality_score is not None:
        summary_bits.append(f"quality_score={quality_score:.3f}")
    if failure_tags:
        tag_text = ", ".join(f"{key}={value}" for key, value in sorted(failure_tags.items()))
        summary_bits.append(f"failures_by_tag: {tag_text}")
    if errors:
        summary_bits.append(f"errors={len(errors)}")
    gate_issues: list[str] = []
    if has_failures:
        gate_issues.append("Harness evidence did not pass: " + ("; ".join(summary_bits) if summary_bits else "no passing summary available"))
    gate_issues.extend(errors)
    return {
        "schema_version": SCHEMA_VERSION,
        "reports": list(dict.fromkeys(report_paths)),
        "items": evidence_items,
        "errors": errors,
        "case_count": case_count or None,
        "pass_count": pass_count if case_count else None,
        "pass_rate": pass_rate,
        "quality_score": quality_score,
        "failures_by_tag": failure_tags,
        "failed_cases": failed_cases[:80],
        "gate_result": "fail" if has_failures else ("pass" if evidence_items else "auto"),
        "gate_issues": gate_issues,
        "summary": "; ".join(summary_bits) if summary_bits else "",
    }


def deep_loop_pass_threshold(depth: str, profile: dict[str, Any]) -> float:
    threshold = {
        "L0": 0.50,
        "L1": 0.55,
        "L2": 0.60,
        "L3": 0.70,
        "L4": 0.75,
        "L5": 0.82,
        "L6": 0.90,
    }.get(depth, 0.70)
    if profile.get("verification_strictness") == "strict":
        threshold += 0.03
    if profile.get("route_mode") == "strict":
        threshold += 0.02
    if profile.get("route_mode") == "quick":
        threshold -= 0.05
    return max(0.50, min(0.95, round(threshold, 2)))


def deep_loop_round_limit(depth: str) -> int:
    return {
        "L0": 1,
        "L1": 1,
        "L2": 2,
        "L3": 3,
        "L4": 3,
        "L5": 4,
        "L6": 5,
    }.get(depth, 3)


def deep_loop_existing_round_count(cwd: Path, subchain_id: str) -> int:
    count = 0
    for record in read_jsonl(decisions_path(cwd)):
        if record.get("type") == "deep_loop_gate" and record.get("current_subchain") == subchain_id:
            count += 1
    return count


def deep_loop_subchain(route_graph: dict[str, Any], subchain_id: str | None) -> dict[str, Any]:
    route_subchains = [item for item in route_graph.get("subchains") or [] if isinstance(item, dict)]
    if subchain_id:
        for chain in route_subchains:
            if chain.get("id") == subchain_id:
                return dict(chain)
        if subchain_id in DEEP_LOOP_SUBCHAIN_BY_ID:
            item = dict(DEEP_LOOP_SUBCHAIN_BY_ID[subchain_id])
            item.setdefault("depth", item.get("default_depth", route_graph.get("depth_level", "L2")))
            item.setdefault("execution_mode", "sequential")
            return item
        raise ValueError(f"Unknown subchain '{subchain_id}'. Allowed: {', '.join(sorted(DEEP_LOOP_SUBCHAIN_BY_ID))}")
    if route_subchains:
        return dict(route_subchains[0])
    item = dict(SUBCHAIN_RULES[0])
    item.setdefault("depth", item.get("default_depth", "L2"))
    item.setdefault("execution_mode", "sequential")
    return item


def deep_loop_unique_subchains(values: list[str]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for value in values:
        if value in seen or value not in DEEP_LOOP_SUBCHAIN_BY_ID:
            continue
        seen.add(value)
        item = dict(DEEP_LOOP_SUBCHAIN_BY_ID[value])
        item.setdefault("depth", item.get("default_depth", "L2"))
        rows.append(item)
    return rows


def deep_loop_next_subchains(route_graph: dict[str, Any], current_subchain: dict[str, Any], explicit_next: list[str] | None) -> list[dict[str, Any]]:
    current_id = str(current_subchain.get("id"))
    if explicit_next:
        return deep_loop_unique_subchains(explicit_next)
    route_candidates = [
        str(item.get("id"))
        for item in route_graph.get("subchains") or []
        if isinstance(item, dict) and item.get("id") and item.get("id") != current_id
    ]
    if route_candidates:
        return deep_loop_unique_subchains(route_candidates)
    return deep_loop_unique_subchains(DEEP_LOOP_PASS_TRANSITIONS.get(current_id, []))


def deep_loop_human_pause_needed(text: str, profile: dict[str, Any]) -> bool:
    lowered = text.lower()
    if profile.get("data_sensitivity") == "restricted":
        return True
    return any(token in lowered for token in DEEP_LOOP_HUMAN_REVIEW_KEYWORDS)


def subchain_agent_spec(subchain_id: str) -> dict[str, Any]:
    spec = SUBCHAIN_AGENT_SPECS.get(subchain_id)
    if spec:
        return json.loads(json.dumps(spec, ensure_ascii=True))
    fallback = DEEP_LOOP_SUBCHAIN_BY_ID.get(subchain_id, {})
    return {
        "agent_id": f"{subchain_id.lower()}_head_agent",
        "subchain_id": subchain_id,
        "title": f"{fallback.get('name', subchain_id)} Head Agent",
        "mission": "Coordinate this research subchain and produce a valid handoff.",
        "entry_read": [".research-loop/state.json", ".research-loop/material-passport.json"],
        "planning_mode": "standard subchain planning",
        "tool_policy": list(fallback.get("capability_ids") or []),
        "required_outputs": list(fallback.get("outputs") or []),
        "quality_vector": ["objective_gap", "artifact_readiness", "handoff_completeness"],
        "failure_policy": "Retry the subchain or escalate to P10 when the failure is not locally recoverable.",
        "handoff_contract": ["summary", "artifacts", "next action"],
    }


def gate_vector_item(level: str, signals: list[str]) -> dict[str, Any]:
    return {"level": level, "signals": signals or ["No blocking signal detected."]}


def gate_vector_has_high(gate_vector: dict[str, Any], dimensions: set[str]) -> bool:
    return any((gate_vector.get(name) or {}).get("level") == "high" for name in dimensions)


def build_gate_vector(
    *,
    gate_result: str,
    current_subchain: dict[str, Any],
    route_graph: dict[str, Any],
    profile: dict[str, Any],
    depth: str,
    manual_issues: list[str],
    result_summary: str | None,
    artifacts: list[str],
    next_subchains: list[dict[str, Any]],
) -> dict[str, Any]:
    current_id = str(current_subchain.get("id"))
    task_type = str(route_graph.get("task_type") or "")
    blockers = [item for item in route_graph.get("blockers") or [] if isinstance(item, dict)]
    warnings = [item for item in route_graph.get("warnings") or [] if isinstance(item, dict)]
    issue_text = "\n".join(
        manual_issues
        + [str(item.get("text") or "") for item in blockers]
        + [str(item.get("text") or "") for item in warnings]
        + [result_summary or ""]
    ).lower()
    summary_missing = not (result_summary or "").strip()
    artifact_missing = not artifacts
    incomplete_tokens = ["missing", "incomplete", "unclear", "unknown", "unsupported", "failed", "blocked", "cannot", "缺失", "不足", "无法", "不确定", "失败"]
    uncertainty_tokens = ["uncertain", "unknown", "unclear", "ambiguous", "assumption", "limitation", "conflict", "不确定", "假设", "冲突", "局限"]
    evidence_tokens = ["evidence", "claim", "citation", "source", "unsupported", "locator", "证据", "引用", "文献", "主张"]
    method_tokens = ["method", "protocol", "statistics", "metric", "baseline", "compliance", "方法", "统计", "指标", "合规"]
    analysis_tokens = ["analysis", "figure", "table", "uncertainty", "result", "plot", "分析", "图", "表", "结果"]

    objective_signals: list[str] = []
    if gate_result in {"fail", "block"}:
        objective_signals.append(f"Gate result is {gate_result}.")
    if blockers:
        objective_signals.append(f"{len(blockers)} route blocker(s) remain.")
    if summary_missing and current_id not in {"P1", "P5"}:
        objective_signals.append("No result summary was supplied for a nontrivial subchain.")
    if any(token in issue_text for token in incomplete_tokens):
        objective_signals.append("Incomplete or blocked-work signal appears in gate text.")
    objective_level = "high" if gate_result in {"fail", "block"} or (summary_missing and current_id in {"P6", "P7", "P8", "P9"}) else ("medium" if objective_signals else "low")

    evidence_signals: list[str] = []
    if current_id in {"P2", "P3", "P7", "P8"} or task_type in {"claim_synthesis", "writing_formatting", "review_revision", "submission_release"}:
        evidence_signals.append("This subchain depends on explicit source, claim, or citation support.")
    if any(token in issue_text for token in evidence_tokens):
        evidence_signals.append("Evidence or citation issue signal appears in gate text.")
    evidence_level = "high" if evidence_signals and any(token in issue_text for token in ["unsupported", "failed", "missing", "缺失", "失败"]) else ("medium" if evidence_signals else "low")

    artifact_signals: list[str] = []
    if artifacts:
        artifact_signals.append(f"{len(artifacts)} artifact reference(s) were supplied.")
    if artifact_missing and current_id in {"P6", "P7", "P8", "P9"}:
        artifact_signals.append("This late-stage subchain needs concrete output artifacts before handoff.")
    if artifact_missing and current_id == "P5" and summary_missing:
        artifact_signals.append("Execution subchain lacks both artifact references and a result summary.")
    artifact_level = "high" if artifact_missing and current_id in {"P6", "P7", "P8", "P9"} else ("medium" if artifact_missing and current_id == "P5" else "low")

    method_signals: list[str] = []
    if current_id in {"P4", "P6"}:
        method_signals.append("This subchain depends on valid method, metric, or statistical design.")
    if any(token in issue_text for token in method_tokens):
        method_signals.append("Method, metric, statistics, or compliance signal appears in gate text.")
    method_level = "high" if gate_result == "block" and method_signals else ("medium" if method_signals else "low")

    analysis_signals: list[str] = []
    if current_id in {"P6", "P8"}:
        analysis_signals.append("This subchain must validate analysis, figures, interpretation, or review integrity.")
    if any(token in issue_text for token in analysis_tokens):
        analysis_signals.append("Analysis, figure, or result signal appears in gate text.")
    analysis_level = "high" if current_id == "P6" and artifact_missing and summary_missing else ("medium" if analysis_signals else "low")

    novelty_signals: list[str] = []
    if current_id in {"P3", "P7", "P8"} or task_type in {"claim_synthesis", "review_revision"}:
        novelty_signals.append("This subchain should check contribution, alternative explanations, or review novelty.")
    if any(token in issue_text for token in ["novelty", "contribution", "alternative", "创新", "贡献", "反例"]):
        novelty_signals.append("Novelty or alternative-explanation signal appears in gate text.")
    novelty_level = "medium" if novelty_signals else "low"

    uncertainty_signals: list[str] = []
    if any(token in issue_text for token in uncertainty_tokens):
        uncertainty_signals.append("Uncertainty, assumption, conflict, or limitation signal appears in gate text.")
    if depth in {"L5", "L6"} and summary_missing:
        uncertainty_signals.append("Deep task has no result summary for this round.")
    uncertainty_level = "high" if uncertainty_signals and (summary_missing or gate_result in {"fail", "block"}) else ("medium" if uncertainty_signals else "low")

    failure_signals: list[str] = []
    if manual_issues:
        failure_signals.append(f"{len(manual_issues)} manual gate issue(s) were supplied.")
    if gate_result in {"fail", "block"}:
        failure_signals.append(f"Gate result is {gate_result}.")
    if warnings:
        failure_signals.append(f"{len(warnings)} route warning(s) are present.")
    failure_level = "high" if gate_result in {"fail", "block"} else ("medium" if failure_signals else "low")

    handoff_signals: list[str] = []
    if next_subchains:
        handoff_signals.append(f"{len(next_subchains)} next subchain candidate(s) available.")
    else:
        handoff_signals.append("No next subchain candidate is available.")
    handoff_level = "high" if not next_subchains and gate_result == "pass" else ("low" if next_subchains else "medium")

    human_signals: list[str] = []
    if deep_loop_human_pause_needed(issue_text, profile):
        human_signals.append("Owner-only, restricted-data, credential, privacy, payment, or compliance signal detected.")
    human_level = "high" if human_signals else "low"

    return {
        "objective_gap": gate_vector_item(objective_level, objective_signals),
        "evidence_integrity": gate_vector_item(evidence_level, evidence_signals),
        "artifact_readiness": gate_vector_item(artifact_level, artifact_signals),
        "method_validity": gate_vector_item(method_level, method_signals),
        "analysis_validity": gate_vector_item(analysis_level, analysis_signals),
        "novelty_risk": gate_vector_item(novelty_level, novelty_signals),
        "uncertainty_level": gate_vector_item(uncertainty_level, uncertainty_signals),
        "failure_mode_risk": gate_vector_item(failure_level, failure_signals),
        "handoff_completeness": gate_vector_item(handoff_level, handoff_signals),
        "human_blocker": gate_vector_item(human_level, human_signals),
    }


RESEARCH_COUNCIL_FIXED_EXPERTS: list[dict[str, Any]] = [
    {
        "expert_id": "domain_pi",
        "role": "Domain Principal Investigator",
        "domain_scope": "Research-question fit, field realism, and scientific contribution boundaries.",
        "required_reads": ["active research question", "route graph", ".research-loop/material-passport.json"],
        "diagnostic_frame": [
            "State what the project can answer with current materials.",
            "Separate field-standard inference from speculation.",
            "Name the decisive missing domain evidence.",
        ],
        "red_flags": [
            "The claimed objective cannot be answered by the available materials.",
            "The project silently shifts research question between subchains.",
            "A domain convention or physical constraint is ignored.",
        ],
        "output_contract": {
            "verdict": "pass, revise, reroute, or block",
            "domain_constraints": "Non-negotiable field assumptions and limits.",
            "next_domain_action": "Smallest domain-grounded step.",
        },
    },
    {
        "expert_id": "literature_scout",
        "role": "Literature and Source Scout",
        "domain_scope": "Search coverage, source quality, citation provenance, and counterevidence.",
        "required_reads": [".research-loop/material-passport.json", ".research-loop/evidence-ledger.jsonl", "source-hub or ingest reports"],
        "diagnostic_frame": [
            "Check whether the source set is broad enough for the current claim.",
            "Identify missing primary sources, surveys, datasets, or negative evidence.",
            "Separate metadata candidates from verified sources.",
        ],
        "red_flags": [
            "No recorded source supports a late-stage claim.",
            "Citation locators or DOI/title identifiers are missing.",
            "Counterevidence is absent in a novelty or review gate.",
        ],
        "output_contract": {
            "coverage_verdict": "sufficient, partial, or insufficient",
            "must_read_sources": "Sources or source classes to acquire before advancing.",
            "evidence_updates": "Evidence ledger records that must be added or repaired.",
        },
    },
    {
        "expert_id": "methods_critic",
        "role": "Methods and Design Critic",
        "domain_scope": "Method validity, protocol fit, metrics, baselines, and compliance constraints.",
        "required_reads": ["method plan", "experiment or analysis protocol", "route blockers", "harness report"],
        "diagnostic_frame": [
            "Test whether the method can answer the research question.",
            "Check baseline, metric, sampling, and compliance alignment.",
            "Ask which smaller design test would falsify the current plan.",
        ],
        "red_flags": [
            "Metric success does not imply scientific success.",
            "A method is selected before its assumptions are checked.",
            "Compliance, privacy, or data-use constraints are deferred without a recorded decision.",
        ],
        "output_contract": {
            "method_verdict": "valid, partial, invalid, or owner-blocked",
            "assumption_tests": "Tests or checks required before execution.",
            "reroute_target": "P4, P5, P6, P10, or pause_for_human when needed.",
        },
    },
    {
        "expert_id": "data_computation_auditor",
        "role": "Data, Computation, and Reproducibility Auditor",
        "domain_scope": "Data packages, code execution, logs, artifacts, and reproducibility evidence.",
        "required_reads": ["storage-policy.json", "run logs", "artifact refs", "harness evidence"],
        "diagnostic_frame": [
            "Trace every result to an input, command, and output artifact.",
            "Check whether the reported artifact can be regenerated or inspected.",
            "Distinguish computation failure from interpretation failure.",
        ],
        "red_flags": [
            "A pass gate has no concrete artifact reference.",
            "Generated files are outside the storage policy or scratch lab.",
            "A failed command is summarized without stdout/stderr or report path.",
        ],
        "output_contract": {
            "provenance_verdict": "complete, partial, missing, or contaminated",
            "required_artifacts": "Logs, data packages, figures, or reports needed.",
            "validation_command": "Smallest command or inspection to prove readiness.",
        },
    },
    {
        "expert_id": "skeptical_reviewer",
        "role": "Skeptical Reviewer",
        "domain_scope": "Adversarial critique, alternative explanations, weak claims, and premature convergence.",
        "required_reads": ["result summary", "gate issues", "gate vector", "next-work prompt"],
        "diagnostic_frame": [
            "Assume the current conclusion is wrong and seek the strongest objection.",
            "Ask what counterexample would change the route decision.",
            "Separate fixable local gaps from project-level integrity risks.",
        ],
        "red_flags": [
            "The loop advances because a score passed while key evidence is absent.",
            "Alternative explanations or negative controls are missing.",
            "The next subchain would optimize presentation before substance.",
        ],
        "output_contract": {
            "strongest_objection": "Single most damaging objection.",
            "killer_test": "A test that could invalidate the current route.",
            "route_challenge": "Why the proposed route is or is not safe.",
        },
    },
    {
        "expert_id": "novelty_assessor",
        "role": "Novelty and Contribution Assessor",
        "domain_scope": "Contribution originality, claim scope, alternative explanations, and positioning.",
        "required_reads": ["claim map", "literature handoff", "review findings", "target output profile"],
        "diagnostic_frame": [
            "Compare the claimed contribution against the source landscape.",
            "Check whether novelty is a result, framing, method, dataset, or synthesis.",
            "Identify what would reduce the contribution to routine work.",
        ],
        "red_flags": [
            "Novelty is asserted without a comparison set.",
            "The claim is broader than the evidence and analysis support.",
            "The route moves to writing or release before contribution scope is stable.",
        ],
        "output_contract": {
            "novelty_verdict": "strong, plausible, weak, unsupported, or collapsed",
            "positioning_gap": "Missing comparison or claim boundary.",
            "next_claim_action": "Revise claim, return to evidence, or escalate.",
        },
    },
    {
        "expert_id": "failure_mode_diagnostician",
        "role": "Failure Mode Diagnostician",
        "domain_scope": "Blockers, repeated failures, brittle gates, and isolated problem-loop triggers.",
        "required_reads": ["gate vector", "manual issues", "harness evidence", "latest run logs"],
        "diagnostic_frame": [
            "Classify the failure as input, method, execution, analysis, evidence, or orchestration.",
            "Check whether retrying the same route can plausibly fix it.",
            "Define the escalation boundary for P10 isolated labs.",
        ],
        "red_flags": [
            "The same gate failure recurs without narrowing the next round.",
            "A problem needs core edits before an isolated diagnosis exists.",
            "A route executor failure is treated as project completion.",
        ],
        "output_contract": {
            "failure_class": "input, method, execution, analysis, evidence, orchestration, or human authority",
            "escalation_trigger": "Condition that requires P10.",
            "retry_scope": "Narrow retry plan if escalation is not yet needed.",
        },
    },
]


DIMENSION_EXPERT_SPECS: dict[str, dict[str, Any]] = {
    "evidence_integrity": {
        "expert_id": "source_evidence_forensics",
        "role": "Source Evidence Forensics Specialist",
        "domain_scope": "Unsupported claims, missing locators, weak citations, and source-to-claim traceability.",
        "required_reads": [".research-loop/evidence-ledger.jsonl", "claim map", "citation plan"],
        "diagnostic_frame": ["Trace each risky claim to a source locator.", "Find the first unsupported statement that would break review.", "Decide whether the route must return to P2."],
        "red_flags": ["Unsupported claim remains.", "Locator is missing.", "Evidence candidate was never verified."],
        "output_contract": {"evidence_gap": "Exact claim/source gap.", "repair_route": "P2, P3, or P10.", "minimum_evidence": "Record required before writing/review continues."},
    },
    "artifact_readiness": {
        "expert_id": "artifact_provenance_auditor",
        "role": "Artifact Provenance Auditor",
        "domain_scope": "Concrete output files, reproducible reports, figures, tables, and package paths.",
        "required_reads": ["artifact refs", "storage-policy.json", "artifact-registry.jsonl"],
        "diagnostic_frame": ["Inspect whether outputs exist and match the claimed stage.", "Check storage location and reproducibility record.", "Demand a readback artifact before handoff."],
        "red_flags": ["No artifact for a late-stage pass.", "Artifact path is temporary or untracked.", "Output cannot be inspected."],
        "output_contract": {"artifact_gap": "Missing or untrusted output.", "required_readback": "Inspection required.", "route": "Retry current subchain or P10."},
    },
    "analysis_validity": {
        "expert_id": "analysis_validity_auditor",
        "role": "Analysis Validity Auditor",
        "domain_scope": "Statistics, uncertainty, result interpretation, and figure/table correctness.",
        "required_reads": ["analysis report", "figures/tables", "run logs", "method plan"],
        "diagnostic_frame": ["Check whether interpretation follows from results.", "Name uncertainty or robustness checks.", "Route invalid analysis before writing."],
        "red_flags": ["Figure exists but analysis is not validated.", "Uncertainty is omitted.", "Result interpretation exceeds the method."],
        "output_contract": {"analysis_gap": "Invalid or unverified analysis point.", "required_check": "Statistic, table, or figure audit.", "route": "P6 or P10."},
    },
    "method_validity": {
        "expert_id": "method_validity_auditor",
        "role": "Method Validity Auditor",
        "domain_scope": "Method assumptions, metric fit, baselines, and feasibility.",
        "required_reads": ["method plan", "metrics", "baseline notes", "compliance flags"],
        "diagnostic_frame": ["Check whether the method answers the objective.", "Find mismatched metrics or baselines.", "Define the smallest feasibility test."],
        "red_flags": ["Objective-method mismatch.", "Metric does not test the claim.", "Compliance gate is unresolved."],
        "output_contract": {"method_gap": "Assumption or design failure.", "repair_route": "P4, P5, P6, or P10.", "minimum_test": "Feasibility or compliance check."},
    },
    "novelty_risk": {
        "expert_id": "counterclaim_mapper",
        "role": "Counterclaim and Alternative Explanation Mapper",
        "domain_scope": "Alternative explanations, novelty threats, and contribution collapse cases.",
        "required_reads": ["claim map", "literature matrix", "review findings"],
        "diagnostic_frame": ["List plausible rival explanations.", "Identify the strongest prior-art overlap.", "Set the claim boundary that survives counterevidence."],
        "red_flags": ["No counterclaim matrix.", "Novelty asserted without comparison.", "Contribution depends on unverified evidence."],
        "output_contract": {"counterclaims": "Rival explanations to test.", "novelty_gap": "Prior-art or framing gap.", "route": "P2, P3, P8, or P10."},
    },
}


def gate_vector_levels(gate_vector: dict[str, Any]) -> dict[str, str]:
    return {key: str(value.get("level")) for key, value in gate_vector.items() if isinstance(value, dict)}


def gate_level(gate_vector: dict[str, Any], dimension: str) -> str:
    value = gate_vector.get(dimension)
    return str(value.get("level", "low")) if isinstance(value, dict) else "low"


def risk_rank(level: str) -> int:
    return {"low": 0, "medium": 1, "high": 2}.get(str(level), 0)


def combined_signal_text(*parts: Any) -> str:
    chunks: list[str] = []
    for part in parts:
        if isinstance(part, str):
            chunks.append(part)
        elif isinstance(part, dict):
            chunks.append(json.dumps(part, ensure_ascii=True, default=str))
        elif isinstance(part, list):
            chunks.extend(str(item) for item in part)
        elif part is not None:
            chunks.append(str(part))
    return "\n".join(chunks).lower()


def research_council_id(current_subchain: dict[str, Any], gate_vector: dict[str, Any], result_summary: str | None, manual_issues: list[str]) -> str:
    seed = json.dumps(
        {
            "subchain": current_subchain.get("id"),
            "levels": gate_vector_levels(gate_vector),
            "summary": result_summary or "",
            "issues": manual_issues,
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    return f"council-{timestamp()}-{slug(str(current_subchain.get('id') or 'subchain'))}-{short_digest(seed)}"


def expert_card_from_spec(spec: dict[str, Any], *, project_domain: str | None, current_subchain: dict[str, Any], gate_vector: dict[str, Any], source: str) -> dict[str, Any]:
    card = json.loads(json.dumps(spec, ensure_ascii=True))
    card["source"] = source
    card["subchain_scope"] = str(current_subchain.get("id") or "")
    card["project_domain"] = project_domain or "(not set)"
    card["gate_dimensions_to_check"] = gate_vector_levels(gate_vector)
    return card


def dynamic_research_experts(
    *,
    project_domain: str | None,
    current_subchain: dict[str, Any],
    gate_vector: dict[str, Any],
    manual_issues: list[str],
    result_summary: str | None,
    harness_evidence: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    text = combined_signal_text(manual_issues, result_summary, harness_evidence or {}, gate_vector)
    experts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for dimension, spec in DIMENSION_EXPERT_SPECS.items():
        if risk_rank(gate_level(gate_vector, dimension)) >= 1:
            card = expert_card_from_spec(spec, project_domain=project_domain, current_subchain=current_subchain, gate_vector=gate_vector, source=f"dynamic:{dimension}")
            experts.append(card)
            seen.add(str(card.get("expert_id")))
    if any(token in text for token in ["data", "dataset", "csv", "schema", "provenance"]):
        spec = {
            "expert_id": "data_contract_specialist",
            "role": "Data Contract Specialist",
            "domain_scope": "Dataset layout, schema, provenance, and downstream reuse contracts.",
            "required_reads": ["storage-policy.json", "data package metadata", "schema.json when present"],
            "diagnostic_frame": ["Verify raw/interim/processed separation.", "Check schema drift and provenance.", "Name the smallest data validation gate."],
            "red_flags": ["Data bypasses standard package layout.", "Schema is inferred but never checked.", "Analysis consumes an ad hoc temp file."],
            "output_contract": {"data_contract_gap": "Broken storage or schema contract.", "validation_gate": "Smallest data check.", "route": "P5, P6, or P10."},
        }
        if spec["expert_id"] not in seen:
            experts.append(expert_card_from_spec(spec, project_domain=project_domain, current_subchain=current_subchain, gate_vector=gate_vector, source="dynamic:data-signal"))
    if any(token in text for token in ["python", "pytest", "command", "exit", "stderr", "runtime", "dependency"]):
        spec = {
            "expert_id": "execution_runtime_specialist",
            "role": "Execution Runtime Specialist",
            "domain_scope": "Commands, interpreters, dependency boundaries, and test execution failures.",
            "required_reads": ["run logs", "harness report", "test command list"],
            "diagnostic_frame": ["Separate environment failure from project failure.", "Check interpreter and dependency assumptions.", "Name retry or P10 reproduction command."],
            "red_flags": ["Route executor failed but work is treated as complete.", "No stdout/stderr path is recorded.", "Dependency state is guessed from memory."],
            "output_contract": {"runtime_gap": "Environment or command failure.", "reproduction_command": "Command to rerun in lab.", "route": "P5 or P10."},
        }
        if spec["expert_id"] not in seen:
            experts.append(expert_card_from_spec(spec, project_domain=project_domain, current_subchain=current_subchain, gate_vector=gate_vector, source="dynamic:runtime-signal"))
    return experts


def research_council_route_recommendation(
    *,
    current_subchain: dict[str, Any],
    next_subchains: list[dict[str, Any]],
    gate_vector: dict[str, Any],
    manual_issues: list[str],
    result_summary: str | None,
) -> dict[str, Any]:
    current_id = str(current_subchain.get("id"))
    text = combined_signal_text(manual_issues, result_summary, gate_vector)
    target_ids = [str(item.get("id")) for item in next_subchains]
    reason = "delivery_gap_route"
    action = "route_next" if target_ids else "pause_for_human"
    if gate_level(gate_vector, "human_blocker") == "high":
        return {"action": "pause_for_human", "semantic_reason": "systemic_blocker", "target_subchains": [], "rationale": "Human authority or restricted material is required."}
    if gate_level(gate_vector, "evidence_integrity") == "high" or any(token in text for token in ["unsupported", "citation", "locator", "source"]):
        reason = "evidence_gap_route"
        target_ids = ["P2", "P10"] if current_id not in {"P2", "P10"} else [current_id]
        action = "escalate_problem_loop" if current_id in {"P7", "P8", "P9"} else "retry_same_route"
    elif gate_level(gate_vector, "method_validity") == "high":
        reason = "method_gap_route"
        target_ids = ["P4", "P10"] if current_id not in {"P4", "P10"} else [current_id]
        action = "escalate_problem_loop" if current_id not in {"P4", "P10"} else "retry_same_route"
    elif gate_level(gate_vector, "analysis_validity") == "high":
        reason = "analysis_gap_route"
        target_ids = ["P6", "P10"] if current_id not in {"P6", "P10"} else [current_id if current_id == "P6" else "P10"]
        action = "escalate_problem_loop" if current_id in {"P7", "P8", "P9"} else "retry_same_route"
    elif gate_level(gate_vector, "artifact_readiness") == "high":
        reason = "delivery_gap_route"
        target_ids = [current_id, "P10"] if current_id != "P10" else ["P10"]
        action = "escalate_problem_loop" if current_id in {"P6", "P7", "P8", "P9"} else "retry_same_route"
    elif risk_rank(gate_level(gate_vector, "novelty_risk")) >= 1 and current_id in {"P3", "P7", "P8"}:
        reason = "expand_hypothesis_portfolio"
        target_ids = ["P3", "P2", "P10"] if current_id != "P3" else ["P3", "P2"]
        action = "retry_same_route"
    return {
        "action": action,
        "semantic_reason": reason,
        "target_subchains": target_ids,
        "rationale": "Council recommendation derived from gate-vector dimensions, supplied issues, and current subchain risk.",
    }


def research_council_review(
    *,
    cwd: Path,
    passport: dict[str, Any],
    route_graph: dict[str, Any],
    current_subchain: dict[str, Any],
    next_subchains: list[dict[str, Any]],
    gate_vector: dict[str, Any],
    result_summary: str | None,
    manual_issues: list[str],
    harness_evidence: dict[str, Any] | None,
    enabled: bool = True,
) -> dict[str, Any]:
    council_id = research_council_id(current_subchain, gate_vector, result_summary, manual_issues)
    if not enabled:
        return {
            "enabled": False,
            "council_id": council_id,
            "experts": [],
            "route_recommendation": {"action": "defer_to_gate", "semantic_reason": "disabled", "target_subchains": []},
        }
    project_domain = passport.get("domain")
    experts = [
        expert_card_from_spec(spec, project_domain=project_domain, current_subchain=current_subchain, gate_vector=gate_vector, source="fixed")
        for spec in RESEARCH_COUNCIL_FIXED_EXPERTS
    ]
    existing_ids = {str(expert.get("expert_id")) for expert in experts}
    for expert in dynamic_research_experts(
        project_domain=project_domain,
        current_subchain=current_subchain,
        gate_vector=gate_vector,
        manual_issues=manual_issues,
        result_summary=result_summary,
        harness_evidence=harness_evidence,
    ):
        if str(expert.get("expert_id")) not in existing_ids:
            experts.append(expert)
            existing_ids.add(str(expert.get("expert_id")))
    independent_contracts = [
        {
            "expert_id": expert["expert_id"],
            "must_answer": [
                "What is the strongest reason to pass, retry, reroute, escalate, or pause?",
                "Which evidence or artifact did you inspect or require?",
                "What is the smallest next action that changes the gate state?",
            ],
            "evidence_required": list(expert.get("required_reads") or []),
            "output_schema": expert.get("output_contract") or {},
        }
        for expert in experts
    ]
    route_recommendation = research_council_route_recommendation(
        current_subchain=current_subchain,
        next_subchains=next_subchains,
        gate_vector=gate_vector,
        manual_issues=manual_issues,
        result_summary=result_summary,
    )
    return {
        "enabled": True,
        "council_id": council_id,
        "created_at": utc_now(),
        "project_root": psafe(cwd),
        "current_subchain": current_subchain.get("id"),
        "route_task_type": route_graph.get("task_type"),
        "gate_vector_summary": gate_vector_levels(gate_vector),
        "experts": experts,
        "independent_review_contracts": independent_contracts,
        "cross_critique_contract": {
            "mode": "round_robin_challenge",
            "required_checks": [
                "Each expert must name one assumption another expert may be taking for granted.",
                "The skeptical reviewer must attack the council's easiest pass route.",
                "The failure-mode diagnostician must decide whether retrying locally is credible.",
            ],
        },
        "synthesis_contract": {
            "required_output": "A single route recommendation with dissenting objections preserved.",
            "must_include": ["majority recommendation", "minority objections", "killer tests", "safe next subchain", "promotion or pause boundary"],
            "no_core_mutation": True,
        },
        "route_recommendation": route_recommendation,
        "paths": {
            "json": psafe(research_councils_root(cwd) / f"{council_id}.json"),
            "markdown": psafe(research_councils_root(cwd) / f"{council_id}.md"),
        },
    }


def adversarial_killer_tests(gate_vector: dict[str, Any], current_subchain: dict[str, Any], manual_issues: list[str]) -> list[str]:
    current_id = str(current_subchain.get("id"))
    tests: list[str] = []
    if risk_rank(gate_level(gate_vector, "evidence_integrity")) >= 1:
        tests.append("Run claim-evidence verification and inspect every unsupported or partial claim before advancing.")
    if risk_rank(gate_level(gate_vector, "artifact_readiness")) >= 1:
        tests.append("Open or read back each claimed artifact path and verify it matches the subchain required outputs.")
    if risk_rank(gate_level(gate_vector, "method_validity")) >= 1:
        tests.append("Write a one-page method-assumption check mapping objective, method, metric, baseline, and failure criteria.")
    if risk_rank(gate_level(gate_vector, "analysis_validity")) >= 1:
        tests.append("Recompute or directly inspect the analysis/figure/table evidence used by the result summary.")
    if risk_rank(gate_level(gate_vector, "novelty_risk")) >= 1 or current_id in {"P3", "P8"}:
        tests.append("Build a counterclaim matrix with at least one plausible rival explanation or prior-art overlap.")
    if manual_issues:
        tests.append("For each supplied gate issue, record whether it is fixed, deferred with rationale, or escalated to P10.")
    return tests or ["Inspect the next-work prompt against the current gate vector before unattended continuation."]


def adversarial_gate_review(
    *,
    cwd: Path,
    route_graph: dict[str, Any],
    current_subchain: dict[str, Any],
    gate_vector: dict[str, Any],
    base_gate: dict[str, Any],
    result_summary: str | None,
    manual_issues: list[str],
    artifacts: list[str],
    harness_evidence: dict[str, Any] | None,
    enabled: bool = True,
) -> dict[str, Any]:
    current_id = str(current_subchain.get("id"))
    gate_result = str(base_gate.get("decision") or "")
    review_id_seed = json.dumps(
        {
            "subchain": current_id,
            "gate": gate_result,
            "levels": gate_vector_levels(gate_vector),
            "summary": result_summary or "",
            "issues": manual_issues,
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    review_id = f"adv-gate-{timestamp()}-{slug(current_id)}-{short_digest(review_id_seed)}"
    if not enabled:
        return {
            "enabled": False,
            "review_id": review_id,
            "premature_convergence_risk": "low",
            "fatal_objections": [],
            "nonfatal_objections": [],
            "route_recommendation": {"action": "defer_to_gate", "semantic_reason": "disabled", "target_subchains": []},
        }
    text = combined_signal_text(result_summary, manual_issues, harness_evidence or {}, gate_vector)
    fatal: list[str] = []
    nonfatal: list[str] = []
    missing_counterfactuals: list[str] = []
    thin_summary = len((result_summary or "").strip()) < 80
    late_stage = current_id in {"P6", "P7", "P8", "P9"}
    if gate_level(gate_vector, "human_blocker") == "high":
        fatal.append("Human authority, restricted data, credential, or compliance signal blocks unattended continuation.")
    if gate_level(gate_vector, "evidence_integrity") == "high":
        fatal.append("Evidence integrity is high risk; a pass decision would optimize downstream work around unsupported claims.")
    if gate_level(gate_vector, "artifact_readiness") == "high" and late_stage:
        fatal.append("Late-stage handoff has no trustworthy artifact readback.")
    if gate_level(gate_vector, "analysis_validity") == "high":
        fatal.append("Analysis validity is high risk; writing or release would be premature.")
    if gate_level(gate_vector, "method_validity") == "high":
        fatal.append("Method validity is high risk; execution or synthesis would be built on an unchecked design.")
    if thin_summary and current_id in {"P3", "P8"}:
        nonfatal.append("The result summary is too thin for a claim or review gate.")
    if manual_issues:
        nonfatal.append(f"{len(manual_issues)} unresolved gate issue(s) remain in the prompt.")
    if risk_rank(gate_level(gate_vector, "novelty_risk")) >= 1 or any(token in text for token in ["novelty", "alternative", "counter", "prior"]):
        missing_counterfactuals.append("A counterclaim or prior-art overlap matrix is required before convergence.")
    if current_id in {"P3", "P8"}:
        missing_counterfactuals.append("At least one rival interpretation should be tested by the claim/review chain.")
    if not artifacts and late_stage:
        missing_counterfactuals.append("The loop needs an artifact readback countercheck against the claimed stage output.")
    killer_tests = adversarial_killer_tests(gate_vector, current_subchain, manual_issues)
    risk = "low"
    if fatal:
        risk = "high"
    elif (thin_summary and current_id in {"P3", "P8"}) or manual_issues or missing_counterfactuals:
        risk = "medium"
    if gate_result == "route_next" and risk == "medium" and (gate_level(gate_vector, "evidence_integrity") == "high" or gate_level(gate_vector, "novelty_risk") == "medium"):
        risk = "high"
    route_recommendation = research_council_route_recommendation(
        current_subchain=current_subchain,
        next_subchains=[],
        gate_vector=gate_vector,
        manual_issues=manual_issues,
        result_summary=result_summary,
    )
    if risk == "high" and route_recommendation.get("action") == "route_next":
        route_recommendation = {"action": "retry_same_route", "semantic_reason": "reframe_problem", "target_subchains": [current_id], "rationale": "Adversarial review found high premature-convergence risk."}
    return {
        "enabled": True,
        "review_id": review_id,
        "created_at": utc_now(),
        "project_root": psafe(cwd),
        "current_subchain": current_id,
        "attack_summary": [
            "Assume the current gate decision is overconfident.",
            "Attack missing evidence, artifacts, counterfactuals, and route safety before continuation.",
        ],
        "fatal_objections": fatal,
        "nonfatal_objections": nonfatal,
        "missing_counterfactuals": missing_counterfactuals,
        "killer_tests": killer_tests,
        "premature_convergence_risk": risk,
        "route_recommendation": route_recommendation,
        "paths": {
            "json": psafe(adversarial_gates_root(cwd) / f"{review_id}.json"),
            "markdown": psafe(adversarial_gates_root(cwd) / f"{review_id}.md"),
        },
    }


def arbiter_semantic_reason(gate_vector: dict[str, Any], manual_issues: list[str], result_summary: str | None, current_subchain: dict[str, Any]) -> str:
    text = combined_signal_text(manual_issues, result_summary, gate_vector)
    current_id = str(current_subchain.get("id"))
    if gate_level(gate_vector, "human_blocker") == "high":
        return "systemic_blocker"
    if gate_level(gate_vector, "evidence_integrity") == "high" or any(token in text for token in ["unsupported", "citation", "locator", "source", "evidence"]):
        return "evidence_gap_route"
    if gate_level(gate_vector, "method_validity") == "high":
        return "method_gap_route"
    if gate_level(gate_vector, "analysis_validity") == "high":
        return "analysis_gap_route"
    if gate_level(gate_vector, "artifact_readiness") == "high":
        return "delivery_gap_route"
    if risk_rank(gate_level(gate_vector, "novelty_risk")) >= 1 or current_id in {"P3", "P8"} and "alternative" in text:
        return "expand_hypothesis_portfolio"
    if risk_rank(gate_level(gate_vector, "objective_gap")) >= 1:
        return "reframe_problem"
    return "ready_route"


def merge_route_targets(*recommendations: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for recommendation in recommendations:
        for target in recommendation.get("target_subchains") or []:
            append_unique(targets, str(target))
    return targets


def arbiter_decision(
    *,
    base_gate: dict[str, Any],
    current_subchain: dict[str, Any],
    gate_vector: dict[str, Any],
    council: dict[str, Any],
    adversarial: dict[str, Any],
    manual_issues: list[str],
    result_summary: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    current_id = str(current_subchain.get("id"))
    gate = json.loads(json.dumps(base_gate, ensure_ascii=True))
    semantic = arbiter_semantic_reason(gate_vector, manual_issues, result_summary, current_subchain)
    council_rec = council.get("route_recommendation") or {}
    adversarial_rec = adversarial.get("route_recommendation") or {}
    recommended_targets = merge_route_targets(council_rec, adversarial_rec)
    fatal_count = len(adversarial.get("fatal_objections") or [])
    premature_risk = str(adversarial.get("premature_convergence_risk") or "low")
    reasons = list(gate.get("reasons") or [])
    decision_source = "hard_gate"
    if gate_level(gate_vector, "human_blocker") == "high" or semantic == "systemic_blocker":
        gate["decision"] = "pause_for_human"
        gate["review_mode"] = "human_checkpoint"
        append_unique(reasons, "Arbiter paused because human authority or restricted material is required.")
        decision_source = "arbiter_human_blocker"
    elif gate.get("decision") == "route_next" and (fatal_count or premature_risk == "high"):
        if semantic in {"evidence_gap_route", "method_gap_route", "analysis_gap_route", "delivery_gap_route"} and current_id != "P10":
            gate["decision"] = "escalate_problem_loop"
            gate["review_mode"] = "review_for_problem_escalation"
            append_unique(reasons, f"Arbiter overrode route_next because adversarial review found {semantic}.")
            decision_source = "adversarial_override"
        else:
            gate["decision"] = "retry_same_route"
            gate["review_mode"] = "review_for_retry"
            append_unique(reasons, "Arbiter requires another same-subchain round before transition.")
            decision_source = "adversarial_retry"
    elif gate.get("decision") == "route_next" and semantic in {"evidence_gap_route", "method_gap_route", "analysis_gap_route"} and manual_issues:
        gate["decision"] = "retry_same_route"
        gate["review_mode"] = "review_for_retry"
        append_unique(reasons, f"Arbiter converted pass to retry because unresolved issues indicate {semantic}.")
        decision_source = "council_issue_override"
    elif gate.get("decision") in {"retry_same_route", "escalate_problem_loop"}:
        append_unique(reasons, f"Arbiter preserved {gate.get('decision')} with semantic reason {semantic}.")
    gate["reasons"] = reasons
    gate["arbiter_semantic_reason"] = semantic
    gate["arbiter_decision_source"] = decision_source
    arbiter = {
        "semantic_reason": semantic,
        "decision": gate.get("decision"),
        "decision_source": decision_source,
        "base_decision": base_gate.get("decision"),
        "premature_convergence_risk": premature_risk,
        "fatal_objection_count": fatal_count,
        "route_recommendation": {
            "action": gate.get("decision"),
            "target_subchains": recommended_targets or (["P10"] if gate.get("decision") == "escalate_problem_loop" else [current_id] if gate.get("decision") == "retry_same_route" else []),
            "semantic_reason": semantic,
            "rationale": "Arbiter combined hard gate constraints, research council recommendation, and adversarial objections.",
        },
        "reasons": reasons,
    }
    return gate, arbiter


def expert_escalation_reasons(current_subchain: dict[str, Any], depth: str, gate_vector: dict[str, Any]) -> list[str]:
    current_id = str(current_subchain.get("id"))
    critical = {"objective_gap", "evidence_integrity", "method_validity", "analysis_validity", "uncertainty_level", "failure_mode_risk"}
    reasons: list[str] = []
    if current_id in {"P6", "P7", "P8", "P9"} and gate_vector_has_high(gate_vector, critical):
        reasons.append(f"{current_id} has high-risk gate-vector dimensions that need P10 expert review before continuing.")
    if depth in {"L5", "L6"} and gate_vector_has_high(gate_vector, {"novelty_risk", "failure_mode_risk", "uncertainty_level"}):
        reasons.append(f"Depth {depth} task has high uncertainty, novelty, or failure-mode risk.")
    return reasons


def deep_loop_gate_decision(
    *,
    gate_result: str,
    current_subchain: dict[str, Any],
    route_graph: dict[str, Any],
    profile: dict[str, Any],
    depth: str,
    round_index: int,
    max_rounds: int,
    quality_score: float | None,
    pass_threshold: float,
    manual_issues: list[str],
    result_summary: str | None,
    next_subchains: list[dict[str, Any]],
    gate_vector: dict[str, Any],
    expert_reasons: list[str],
) -> dict[str, Any]:
    current_id = str(current_subchain.get("id"))
    reasons: list[str] = []
    blocking_items = [item for item in route_graph.get("blockers") or [] if isinstance(item, dict)]
    issue_text = "\n".join(manual_issues + [str(item.get("text") or "") for item in blocking_items] + [result_summary or ""])
    if blocking_items:
        reasons.append(f"{len(blocking_items)} route blocker(s) are present.")
    if manual_issues:
        reasons.append(f"{len(manual_issues)} manual gate issue(s) were supplied.")
    if quality_score is not None and quality_score < pass_threshold:
        reasons.append(f"Quality score {quality_score:.2f} is below threshold {pass_threshold:.2f}.")
    if deep_loop_human_pause_needed(issue_text, profile):
        reasons.append("Human or restricted-data checkpoint signal detected.")
        return {
            "decision": "pause_for_human",
            "review_mode": "human_checkpoint",
            "round_index": round_index,
            "max_rounds": max_rounds,
            "pass_threshold": pass_threshold,
            "quality_score": quality_score,
            "reasons": reasons,
        }
    if gate_result == "human":
        reasons.append("Gate result explicitly requested human review.")
        return {
            "decision": "pause_for_human",
            "review_mode": "human_checkpoint",
            "round_index": round_index,
            "max_rounds": max_rounds,
            "pass_threshold": pass_threshold,
            "quality_score": quality_score,
            "reasons": reasons,
        }
    if gate_result == "block":
        reasons.append("Gate result explicitly requested blocker escalation.")
        return {
            "decision": "escalate_problem_loop" if current_id != "P10" else "pause_for_human",
            "review_mode": "review_for_retry",
            "round_index": round_index,
            "max_rounds": max_rounds,
            "pass_threshold": pass_threshold,
            "quality_score": quality_score,
            "reasons": reasons,
        }
    if expert_reasons and current_id != "P10" and gate_result in {"pass", "auto"}:
        reasons.extend(expert_reasons)
        return {
            "decision": "escalate_problem_loop",
            "review_mode": "review_for_problem_escalation",
            "round_index": round_index,
            "max_rounds": max_rounds,
            "pass_threshold": pass_threshold,
            "quality_score": quality_score,
            "gate_vector": gate_vector,
            "expert_precheck_required": True,
            "reasons": reasons,
        }
    failing = bool(reasons) or gate_result == "fail"
    if gate_result == "pass":
        failing = False if not blocking_items and not (quality_score is not None and quality_score < pass_threshold) else True
    if gate_result == "auto" and not failing:
        failing = False
    if failing:
        if round_index >= max_rounds or current_id == "P10":
            reasons.append("Retry budget is exhausted or the current subchain is already the problem-resolution chain.")
            return {
                "decision": "escalate_problem_loop" if current_id != "P10" else "pause_for_human",
                "review_mode": "review_for_retry",
                "round_index": round_index,
                "max_rounds": max_rounds,
                "pass_threshold": pass_threshold,
                "quality_score": quality_score,
                "reasons": reasons,
            }
        reasons.append("Gate did not pass; continue inside the same subchain after review.")
        return {
            "decision": "retry_same_route",
            "review_mode": "review_for_retry",
            "round_index": round_index,
            "max_rounds": max_rounds,
            "pass_threshold": pass_threshold,
            "quality_score": quality_score,
            "gate_vector": gate_vector,
            "reasons": reasons,
        }
    if not next_subchains:
        reasons.append("No later subchain is available; stop at a human final checkpoint.")
        return {
            "decision": "pause_for_human",
            "review_mode": "review_for_transition",
            "round_index": round_index,
            "max_rounds": max_rounds,
            "pass_threshold": pass_threshold,
            "quality_score": quality_score,
            "gate_vector": gate_vector,
            "reasons": reasons,
        }
    reasons.append("Gate passed; review should prepare the next subchain.")
    return {
        "decision": "route_next",
        "review_mode": "review_for_transition",
        "round_index": round_index,
        "max_rounds": max_rounds,
        "pass_threshold": pass_threshold,
        "quality_score": quality_score,
        "gate_vector": gate_vector,
        "expert_precheck_required": False,
        "reasons": reasons,
    }


def deep_loop_review_directive(
    cwd: Path,
    route_graph: dict[str, Any],
    current_subchain: dict[str, Any],
    next_subchains: list[dict[str, Any]],
    gate: dict[str, Any],
    result_summary: str | None,
    manual_issues: list[str],
    harness_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current_id = str(current_subchain.get("id"))
    decision = gate["decision"]
    next_ids = [str(item.get("id")) for item in next_subchains]
    if decision == "route_next":
        mode = "review_for_transition"
        purpose = "Evaluate whether the completed subchain is stable enough to hand off, then give concrete work guidance for the next subchain."
        focus_questions = [
            "Which outputs from the completed subchain are verified and reusable?",
            "What assumptions, risks, or missing inputs must the next subchain inherit?",
            "Which next subchain should run first, and what is its acceptance gate?",
            "What evidence or artifacts must be read before the next subchain starts?",
        ]
        output_contract = {
            "verified_outputs": "List stable artifacts, claims, data packages, run logs, or decisions.",
            "next_subchain": "Choose the next subchain id and explain the route.",
            "working_guidance": "Give the next subchain a direct task prompt and gate checklist.",
            "stop_conditions": "Name conditions that should trigger retry, problem-loop, or human pause.",
        }
    elif decision == "retry_same_route":
        mode = "review_for_retry"
        purpose = "Diagnose why the current subchain gate did not pass and produce a narrower next-round plan inside the same subchain."
        focus_questions = [
            "Which gate criterion failed, and what evidence shows the failure?",
            "Is the failure caused by missing input, weak analysis, broken code, invalid data, or unsupported claims?",
            "What is the smallest corrective action for the next round?",
            "What test, validation, or evidence update will prove the retry succeeded?",
        ]
        output_contract = {
            "failure_diagnosis": "Map each failed gate issue to root cause and evidence.",
            "retry_scope": "Restrict the next round to necessary corrective actions.",
            "retry_prompt": "Give a concrete prompt for repeating the same subchain.",
            "retry_gate": "Define the next pass/fail gate and expected artifacts.",
        }
    elif decision == "escalate_problem_loop":
        mode = "review_for_problem_escalation"
        purpose = "Prepare an isolated problem-loop case before any core project files are changed."
        focus_questions = [
            "What is the minimal problem statement for the isolated lab?",
            "Which logs, artifacts, commands, and project context must be copied into the lab?",
            "Which domain experts need to be constructed for this problem?",
            "What promotion threshold and validation commands are required before core edits?",
        ]
        output_contract = {
            "problem_statement": "A precise problem-loop prompt.",
            "lab_inputs": "Files, commands, logs, and context to place in scratch lab scope.",
            "expert_panel": "Fixed and on-demand expert roles needed for evaluation.",
            "promotion_gate": "Tests and threshold required before promotion.",
        }
    else:
        mode = "human_checkpoint"
        purpose = "Pause unattended execution and ask for a human decision before continuing."
        focus_questions = [
            "Which decision requires human authority or project-owner judgment?",
            "What options are available, and what are the risks of each option?",
            "What evidence should the human review before approving continuation?",
            "What override rationale must be recorded if execution continues?",
        ]
        output_contract = {
            "decision_needed": "The exact human decision required.",
            "options": "Safe continuation, retry, defer, or stop options.",
            "evidence_to_review": "Artifacts and reports the human should inspect.",
            "approval_record": "Decision-log entry required before resuming.",
        }
    normalized = route_graph.get("normalized_input") or {}
    return {
        "mode": mode,
        "purpose": purpose,
        "current_subchain": current_id,
        "next_subchains": next_ids,
        "review_roles": [
            "workflow_orchestrator",
            "domain_method_reviewer",
            "evidence_integrity_reviewer",
            "implementation_or_artifact_reviewer",
        ],
        "focus_questions": focus_questions,
        "output_contract": output_contract,
        "inputs_to_review": {
            "project_root": psafe(cwd),
            "state": psafe(state_path(cwd)),
            "passport": psafe(passport_path(cwd)),
            "route_graph_stage": route_graph.get("stage"),
            "result_summary": result_summary,
            "manual_issues": manual_issues,
            "normalized_prompt": normalized.get("downstream_prompt"),
            "execution_profile": route_graph.get("execution_profile"),
            "harness_protocol": route_graph.get("harness_protocol"),
            "harness_evidence": harness_evidence or {},
        },
    }


def deep_loop_handoff_package(
    route_graph: dict[str, Any],
    current_subchain: dict[str, Any],
    next_subchains: list[dict[str, Any]],
    gate: dict[str, Any],
    review: dict[str, Any],
    artifacts: list[str],
) -> dict[str, Any]:
    current_id = str(current_subchain.get("id"))
    decision = str(gate.get("decision"))
    if decision == "route_next":
        target_ids = [str(item.get("id")) for item in next_subchains]
    elif decision == "retry_same_route":
        target_ids = [current_id]
    elif decision == "escalate_problem_loop":
        target_ids = ["P10"]
    else:
        target_ids = []
    return {
        "from_subchain": current_id,
        "gate_decision": decision,
        "target_subchains": target_ids,
        "must_read": [
            ".research-loop/state.json",
            ".research-loop/material-passport.json",
            ".research-loop/decision-log.jsonl",
            ".research-loop/evidence-ledger.jsonl",
            "latest .research-loop/checkpoints/*.md when present",
            "latest .research-loop/handoffs/*.md when present",
        ],
        "artifact_refs": artifacts,
        "review_mode": review.get("mode"),
        "review_output_contract": review.get("output_contract"),
        "harness_protocol": route_graph.get("harness_protocol"),
        "next_work_prompt": deep_loop_next_work_prompt(route_graph, current_subchain, next_subchains, gate, review),
    }


def subchain_agent_prompt_block(agent: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Subchain Head Agent Contract",
            "",
            f"- Agent id: `{agent.get('agent_id')}`",
            f"- Subchain id: `{agent.get('subchain_id')}`",
            f"- Title: {agent.get('title')}",
            f"- Mission: {agent.get('mission')}",
            f"- Planning mode: {agent.get('planning_mode')}",
            "- Required reads: " + ", ".join(str(item) for item in agent.get("entry_read") or []),
            "- Tool policy: " + ", ".join(str(item) for item in agent.get("tool_policy") or []),
            "- Required outputs: " + ", ".join(str(item) for item in agent.get("required_outputs") or []),
            "- Quality vector: " + ", ".join(str(item) for item in agent.get("quality_vector") or []),
            f"- Failure policy: {agent.get('failure_policy')}",
            "- Handoff contract: " + ", ".join(str(item) for item in agent.get("handoff_contract") or []),
        ]
    )


def deep_loop_continuation_contract(
    *,
    current_subchain: dict[str, Any],
    gate: dict[str, Any],
    handoff: dict[str, Any],
    subchain_agent: dict[str, Any],
    gate_vector: dict[str, Any],
    research_council: dict[str, Any] | None = None,
    adversarial_gate: dict[str, Any] | None = None,
    arbiter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = str(gate.get("decision"))
    target_ids = list(handoff.get("target_subchains") or [])
    next_agent = subchain_agent_spec(str(target_ids[0])) if target_ids else None
    blocking_dimensions = [
        key
        for key, value in gate_vector.items()
        if isinstance(value, dict) and value.get("level") == "high"
    ]
    council = research_council or {}
    adversarial = adversarial_gate or {}
    arbiter_payload = arbiter or {}
    return {
        "decision": decision,
        "from_subchain": current_subchain.get("id"),
        "from_agent": subchain_agent.get("agent_id"),
        "target_subchains": target_ids,
        "next_agent": next_agent,
        "next_work_prompt": handoff.get("next_work_prompt"),
        "required_reads": list(handoff.get("must_read") or []),
        "artifact_refs": list(handoff.get("artifact_refs") or []),
        "harness_protocol": handoff.get("harness_protocol"),
        "gate_vector_summary": {key: value.get("level") for key, value in gate_vector.items() if isinstance(value, dict)},
        "blocking_dimensions": blocking_dimensions,
        "council_findings": {
            "council_id": council.get("council_id"),
            "expert_ids": [expert.get("expert_id") for expert in council.get("experts") or []],
            "route_recommendation": council.get("route_recommendation") or {},
        },
        "adversarial_findings": {
            "review_id": adversarial.get("review_id"),
            "premature_convergence_risk": adversarial.get("premature_convergence_risk"),
            "fatal_objection_count": len(adversarial.get("fatal_objections") or []),
            "killer_tests": list(adversarial.get("killer_tests") or []),
        },
        "arbiter_findings": {
            "semantic_reason": arbiter_payload.get("semantic_reason"),
            "decision_source": arbiter_payload.get("decision_source"),
            "route_recommendation": arbiter_payload.get("route_recommendation") or {},
        },
        "stop_conditions": [
            "pause_for_human only when owner-only authorization, credentials, restricted data, payment, or ethics approval is required",
            "escalate_problem_loop when high-risk gate-vector dimensions remain unresolved",
            "retry_same_route when issues are local to the current subchain and retry budget remains",
        ],
        "unattended_safe": decision in {"route_next", "retry_same_route", "escalate_problem_loop"},
        "requires_human": decision == "pause_for_human",
        "core_files_mutable": False,
    }


def deep_loop_next_work_prompt(
    route_graph: dict[str, Any],
    current_subchain: dict[str, Any],
    next_subchains: list[dict[str, Any]],
    gate: dict[str, Any],
    review: dict[str, Any],
) -> str:
    current_id = str(current_subchain.get("id"))
    decision = str(gate.get("decision"))
    normalized = route_graph.get("normalized_input") or {}
    inherited_prompt = normalized.get("downstream_prompt") or route_graph.get("intent") or "Continue the current research-loop task."
    if decision == "route_next":
        target = next_subchains[0] if next_subchains else {}
        target_id = target.get("id", "next-subchain")
        target_name = target.get("name", "next research subchain")
        target_agent = subchain_agent_spec(str(target_id))
        return (
            f"Run subchain {target_id} ({target_name}) after review_for_transition. "
            f"Read the handoff, preserve verified outputs from {current_id}, then execute this project-grounded task:\n\n"
            f"{subchain_agent_prompt_block(target_agent)}\n\n"
            "## Project Task\n\n"
            f"{inherited_prompt}"
        )
    if decision == "retry_same_route":
        current_agent = subchain_agent_spec(current_id)
        return (
            f"Retry subchain {current_id} ({current_subchain.get('name')}) after review_for_retry. "
            "Limit the next round to the diagnosed failed gate criteria, then rerun the same gate.\n\n"
            f"{subchain_agent_prompt_block(current_agent)}\n\n"
            "## Project Task And Harness\n\n"
            f"{inherited_prompt}"
        )
    if decision == "escalate_problem_loop":
        problem_agent = subchain_agent_spec("P10")
        return (
            "Run P10 problem-resolution-expert-chain in an isolated lab. "
            "Convert the failed gate into a precise problem-loop case, capture reproduction or validation commands, "
            "and promote only after the threshold gate approves the adjustment plan.\n\n"
            f"{subchain_agent_prompt_block(problem_agent)}\n\n"
            "## Original Project Task And Harness\n\n"
            f"{inherited_prompt}"
        )
    return (
        "Pause unattended execution. Record the required human decision in the decision log before retrying, "
        "routing to the next subchain, or forcing a promotion."
    )


def build_deep_loop_payload(args: argparse.Namespace, cwd: Path, state: dict[str, Any], passport: dict[str, Any]) -> dict[str, Any]:
    graph = build_route_graph(cwd, state, passport, args.intent)
    current = deep_loop_subchain(graph, args.current_subchain)
    depth = merge_depth(str(current.get("depth", "L0")), str(graph.get("depth_level", "L0")))
    profile = passport.get("profile") or {}
    quality_score = normalize_quality_score(args.quality_score)
    harness_evidence = collect_harness_evidence(cwd, list(getattr(args, "harness_report", None) or []))
    if quality_score is None:
        quality_score = normalize_report_metric(harness_evidence.get("quality_score"))
    threshold = normalize_quality_score(args.pass_threshold) if args.pass_threshold is not None else deep_loop_pass_threshold(depth, profile)
    max_rounds = int(args.max_rounds or deep_loop_round_limit(depth))
    round_index = int(args.round_index or (deep_loop_existing_round_count(cwd, str(current.get("id"))) + 1))
    next_subchains = deep_loop_next_subchains(graph, current, args.next_subchain)
    manual_issues = list(args.gate_issue or []) + list(harness_evidence.get("gate_issues") or [])
    artifacts = list(args.artifact or [])
    for report_path in harness_evidence.get("reports") or []:
        append_unique(artifacts, str(report_path))
    effective_gate_result = str(args.gate_result)
    if effective_gate_result == "auto" and harness_evidence.get("gate_result") in {"pass", "fail"}:
        effective_gate_result = str(harness_evidence["gate_result"])
    result_summary = args.result_summary
    if harness_evidence.get("summary"):
        result_summary = "\n\n".join(part for part in [result_summary, f"Harness evidence: {harness_evidence['summary']}"] if part)
    subchain_agent = subchain_agent_spec(str(current.get("id")))
    gate_vector = build_gate_vector(
        gate_result=effective_gate_result,
        current_subchain=current,
        route_graph=graph,
        profile=profile,
        depth=depth,
        manual_issues=manual_issues,
        result_summary=result_summary,
        artifacts=artifacts,
        next_subchains=next_subchains,
    )
    expert_reasons = expert_escalation_reasons(current, depth, gate_vector)
    base_gate = deep_loop_gate_decision(
        gate_result=effective_gate_result,
        current_subchain=current,
        route_graph=graph,
        profile=profile,
        depth=depth,
        round_index=round_index,
        max_rounds=max_rounds,
        quality_score=quality_score,
        pass_threshold=float(threshold),
        manual_issues=manual_issues,
        result_summary=result_summary,
        next_subchains=next_subchains,
        gate_vector=gate_vector,
        expert_reasons=expert_reasons,
    )
    council = research_council_review(
        cwd=cwd,
        passport=passport,
        route_graph=graph,
        current_subchain=current,
        next_subchains=next_subchains,
        gate_vector=gate_vector,
        result_summary=result_summary,
        manual_issues=manual_issues,
        harness_evidence=harness_evidence,
        enabled=not bool(getattr(args, "skip_research_council", False)),
    )
    adversarial = adversarial_gate_review(
        cwd=cwd,
        route_graph=graph,
        current_subchain=current,
        gate_vector=gate_vector,
        base_gate=base_gate,
        result_summary=result_summary,
        manual_issues=manual_issues,
        artifacts=artifacts,
        harness_evidence=harness_evidence,
        enabled=not bool(getattr(args, "skip_adversarial_gate", False)),
    )
    gate, arbiter = arbiter_decision(
        base_gate=base_gate,
        current_subchain=current,
        gate_vector=gate_vector,
        council=council,
        adversarial=adversarial,
        manual_issues=manual_issues,
        result_summary=result_summary,
    )
    review = deep_loop_review_directive(cwd, graph, current, next_subchains, gate, result_summary, manual_issues, harness_evidence)
    handoff = deep_loop_handoff_package(graph, current, next_subchains, gate, review, artifacts)
    continuation = deep_loop_continuation_contract(
        current_subchain=current,
        gate=gate,
        handoff=handoff,
        subchain_agent=subchain_agent,
        gate_vector=gate_vector,
        research_council=council,
        adversarial_gate=adversarial,
        arbiter=arbiter,
    )
    loop_id = args.loop_id or f"deep-{timestamp()}-{slug(str(current.get('id', 'subchain')))}"
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "loop_id": loop_id,
        "project_root": psafe(cwd),
        "stage": state.get("current_stage", "INTAKE"),
        "intent": args.intent,
        "current_subchain": current,
        "subchain_agent": subchain_agent,
        "depth_level": depth,
        "route_graph": graph,
        "gate_input": {
            "gate_result": args.gate_result,
            "effective_gate_result": effective_gate_result,
            "quality_score": quality_score,
            "pass_threshold": threshold,
            "result_summary": result_summary,
            "manual_issues": manual_issues,
            "artifacts": artifacts,
            "harness_reports": list(getattr(args, "harness_report", None) or []),
            "harness_evidence": harness_evidence,
        },
        "harness_evidence": harness_evidence,
        "gate_vector": gate_vector,
        "research_council": council,
        "adversarial_gate": adversarial,
        "arbiter": arbiter,
        "gate": gate,
        "review_directive": review,
        "next_subchains": next_subchains if gate.get("decision") == "route_next" else [],
        "handoff_package": handoff,
        "continuation_contract": continuation,
        "safety": {
            "unattended_safe": gate.get("decision") in {"route_next", "retry_same_route", "escalate_problem_loop"},
            "requires_human": gate.get("decision") == "pause_for_human",
            "core_files_mutable": False,
            "note": "Deep-loop dispatch only produces review and routing directives. Core file edits remain gated by downstream validation or problem-loop promotion.",
        },
    }


def deep_loop_markdown(payload: dict[str, Any]) -> list[str]:
    current = payload.get("current_subchain") or {}
    agent = payload.get("subchain_agent") or {}
    gate = payload.get("gate") or {}
    review = payload.get("review_directive") or {}
    handoff = payload.get("handoff_package") or {}
    continuation = payload.get("continuation_contract") or {}
    lines = [
        "# Research Deep Loop Gate",
        "",
        f"- Created at UTC: {payload.get('timestamp')}",
        f"- Project root: {payload.get('project_root')}",
        f"- Loop id: `{payload.get('loop_id')}`",
        f"- Stage: `{payload.get('stage')}`",
        f"- Current subchain: `{current.get('id')}` {current.get('name')}",
        f"- Subchain agent: `{agent.get('agent_id')}` {agent.get('title') or ''}".rstrip(),
        f"- Depth: `{payload.get('depth_level')}`",
        f"- Gate decision: `{gate.get('decision')}`",
        f"- Review mode: `{review.get('mode')}`",
        f"- Round: {gate.get('round_index')}/{gate.get('max_rounds')}",
        f"- Quality score: {gate.get('quality_score') if gate.get('quality_score') is not None else '(not supplied)'}",
        f"- Pass threshold: {gate.get('pass_threshold')}",
    ]
    if payload.get("intent"):
        lines.append(f"- Intent: {payload.get('intent')}")
    lines.extend(["", "## Gate Reasons", ""])
    reasons = gate.get("reasons") or []
    if reasons:
        lines.extend(f"- {item}" for item in reasons)
    else:
        lines.append("- No gate issues recorded.")
    gate_input = payload.get("gate_input") or {}
    if gate_input.get("result_summary"):
        lines.extend(["", "## Result Summary", "", str(gate_input.get("result_summary"))])
    if gate_input.get("manual_issues"):
        lines.extend(["", "## Supplied Gate Issues", ""])
        lines.extend(f"- {item}" for item in gate_input.get("manual_issues") or [])
    harness_evidence = payload.get("harness_evidence") if isinstance(payload.get("harness_evidence"), dict) else {}
    if harness_evidence and (harness_evidence.get("reports") or harness_evidence.get("summary") or harness_evidence.get("errors")):
        lines.extend(["", "## Harness Evidence", ""])
        lines.append(f"- Gate result from evidence: `{harness_evidence.get('gate_result')}`")
        if harness_evidence.get("pass_rate") is not None:
            lines.append(f"- Pass rate: `{harness_evidence.get('pass_rate')}`")
        if harness_evidence.get("quality_score") is not None:
            lines.append(f"- Quality score: `{harness_evidence.get('quality_score')}`")
        failures_by_tag = harness_evidence.get("failures_by_tag") if isinstance(harness_evidence.get("failures_by_tag"), dict) else {}
        if failures_by_tag:
            lines.append("- Failures by tag: " + ", ".join(f"{key}={value}" for key, value in sorted(failures_by_tag.items())))
        if harness_evidence.get("reports"):
            lines.append("- Reports:")
            lines.extend(f"  - `{item}`" for item in harness_evidence.get("reports") or [])
        if harness_evidence.get("errors"):
            lines.append("- Adapter errors:")
            lines.extend(f"  - {item}" for item in harness_evidence.get("errors") or [])
    lines.extend(["", "## Gate Vector", ""])
    for key, value in (payload.get("gate_vector") or {}).items():
        if isinstance(value, dict):
            signals = "; ".join(str(item) for item in value.get("signals") or [])
            lines.append(f"- `{key}`: {value.get('level')} - {signals}")
    council = payload.get("research_council") if isinstance(payload.get("research_council"), dict) else {}
    if council:
        lines.extend(["", "## Research Council", ""])
        lines.append(f"- Council id: `{council.get('council_id')}`")
        lines.append(f"- Experts: {len(council.get('experts') or [])}")
        council_rec = council.get("route_recommendation") if isinstance(council.get("route_recommendation"), dict) else {}
        lines.append(f"- Recommendation: `{council_rec.get('action')}` reason=`{council_rec.get('semantic_reason')}`")
        lines.append("- Target subchains: " + (", ".join(str(item) for item in council_rec.get("target_subchains") or []) or "(none)"))
        for expert in (council.get("experts") or [])[:12]:
            lines.append(f"- `{expert.get('expert_id')}` {expert.get('role')}: {expert.get('domain_scope')}")
    adversarial = payload.get("adversarial_gate") if isinstance(payload.get("adversarial_gate"), dict) else {}
    if adversarial:
        lines.extend(["", "## Adversarial Gate", ""])
        lines.append(f"- Review id: `{adversarial.get('review_id')}`")
        lines.append(f"- Premature convergence risk: `{adversarial.get('premature_convergence_risk')}`")
        fatal = adversarial.get("fatal_objections") or []
        nonfatal = adversarial.get("nonfatal_objections") or []
        lines.append(f"- Fatal objections: {len(fatal)}")
        for item in fatal[:8]:
            lines.append(f"  - {item}")
        if nonfatal:
            lines.append(f"- Nonfatal objections: {len(nonfatal)}")
            for item in nonfatal[:8]:
                lines.append(f"  - {item}")
        if adversarial.get("missing_counterfactuals"):
            lines.append("- Missing counterfactuals:")
            lines.extend(f"  - {item}" for item in adversarial.get("missing_counterfactuals") or [])
        if adversarial.get("killer_tests"):
            lines.append("- Killer tests:")
            lines.extend(f"  - {item}" for item in adversarial.get("killer_tests") or [])
    arbiter = payload.get("arbiter") if isinstance(payload.get("arbiter"), dict) else {}
    if arbiter:
        lines.extend(["", "## Arbiter", ""])
        lines.append(f"- Final decision: `{arbiter.get('decision')}`")
        lines.append(f"- Base decision: `{arbiter.get('base_decision')}`")
        lines.append(f"- Decision source: `{arbiter.get('decision_source')}`")
        lines.append(f"- Semantic reason: `{arbiter.get('semantic_reason')}`")
        arbiter_rec = arbiter.get("route_recommendation") if isinstance(arbiter.get("route_recommendation"), dict) else {}
        lines.append("- Recommended targets: " + (", ".join(str(item) for item in arbiter_rec.get("target_subchains") or []) or "(none)"))
    lines.extend(["", "## Subchain Agent Contract", ""])
    lines.append(f"- Mission: {agent.get('mission')}")
    lines.append(f"- Planning mode: {agent.get('planning_mode')}")
    lines.append("- Required outputs: " + ", ".join(agent.get("required_outputs") or []))
    lines.append("- Handoff contract: " + ", ".join(agent.get("handoff_contract") or []))
    lines.extend(["", "## Review Directive", ""])
    lines.append(f"- Purpose: {review.get('purpose')}")
    lines.append("- Review roles: " + ", ".join(review.get("review_roles") or []))
    lines.extend(["", "### Focus Questions", ""])
    for item in review.get("focus_questions") or []:
        lines.append(f"- {item}")
    lines.extend(["", "### Output Contract", ""])
    for key, value in (review.get("output_contract") or {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Target Subchains", ""])
    targets = handoff.get("target_subchains") or []
    if targets:
        for target in targets:
            info = DEEP_LOOP_SUBCHAIN_BY_ID.get(str(target), {})
            lines.append(f"- `{target}` {info.get('name', '')}".rstrip())
    else:
        lines.append("- No automatic target. Human checkpoint required.")
    lines.extend(["", "## Next Work Prompt", "", handoff.get("next_work_prompt") or "(not generated)"])
    lines.extend(["", "## Continuation Contract", ""])
    lines.append(f"- Decision: `{continuation.get('decision')}`")
    lines.append(f"- From agent: `{continuation.get('from_agent')}`")
    lines.append("- Target subchains: " + (", ".join(continuation.get("target_subchains") or []) or "(none)"))
    lines.append("- Blocking dimensions: " + (", ".join(continuation.get("blocking_dimensions") or []) or "(none)"))
    harness = continuation.get("harness_protocol") if isinstance(continuation.get("harness_protocol"), dict) else {}
    if harness:
        lines.extend(["", "## Harness Protocol", ""])
        lines.append(f"- Execution profile: `{harness.get('execution_profile')}`")
        lines.append("- Validation surfaces: " + (", ".join(str(item) for item in harness.get("validation_surfaces") or []) or "(none)"))
        feedback_summary = harness.get("feedback_summary") if isinstance(harness.get("feedback_summary"), dict) else {}
        lines.append("- Gate feedback metrics: " + (", ".join(str(item) for item in feedback_summary.get("preferred_metrics") or []) or "(none)"))
        lines.append("- Report fields: " + (", ".join(str(item) for item in harness.get("report_fields") or []) or "(none)"))
    lines.extend(["", "## Required Reads", ""])
    for item in handoff.get("must_read") or []:
        lines.append(f"- `{item}`")
    artifacts = handoff.get("artifact_refs") or []
    if artifacts:
        lines.extend(["", "## Artifact References", ""])
        lines.extend(f"- `{item}`" for item in artifacts)
    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- Unattended safe: {payload.get('safety', {}).get('unattended_safe')}",
            f"- Requires human: {payload.get('safety', {}).get('requires_human')}",
            f"- Core files mutable now: {payload.get('safety', {}).get('core_files_mutable')}",
            f"- Note: {payload.get('safety', {}).get('note')}",
        ]
    )
    return lines


def research_council_markdown(council: dict[str, Any]) -> list[str]:
    lines = [
        "# Research Council Review",
        "",
        f"- Council id: `{council.get('council_id')}`",
        f"- Created at UTC: {council.get('created_at')}",
        f"- Project root: {council.get('project_root')}",
        f"- Current subchain: `{council.get('current_subchain')}`",
        "",
        "## Route Recommendation",
        "",
    ]
    rec = council.get("route_recommendation") if isinstance(council.get("route_recommendation"), dict) else {}
    lines.append(f"- Action: `{rec.get('action')}`")
    lines.append(f"- Semantic reason: `{rec.get('semantic_reason')}`")
    lines.append("- Target subchains: " + (", ".join(str(item) for item in rec.get("target_subchains") or []) or "(none)"))
    if rec.get("rationale"):
        lines.append(f"- Rationale: {rec.get('rationale')}")
    lines.extend(["", "## Experts", ""])
    for expert in council.get("experts") or []:
        lines.append(f"### {expert.get('expert_id')} - {expert.get('role')}")
        lines.append("")
        lines.append(f"- Source: {expert.get('source')}")
        lines.append(f"- Domain scope: {expert.get('domain_scope')}")
        lines.append("- Required reads: " + ", ".join(str(item) for item in expert.get("required_reads") or []))
        lines.append("- Red flags: " + "; ".join(str(item) for item in expert.get("red_flags") or []))
        lines.append("")
    lines.extend(["## Synthesis Contract", ""])
    synthesis = council.get("synthesis_contract") if isinstance(council.get("synthesis_contract"), dict) else {}
    for key, value in synthesis.items():
        if isinstance(value, list):
            lines.append(f"- `{key}`: " + ", ".join(str(item) for item in value))
        else:
            lines.append(f"- `{key}`: {value}")
    return lines


def adversarial_gate_markdown(adversarial: dict[str, Any]) -> list[str]:
    lines = [
        "# Adversarial Gate Review",
        "",
        f"- Review id: `{adversarial.get('review_id')}`",
        f"- Created at UTC: {adversarial.get('created_at')}",
        f"- Project root: {adversarial.get('project_root')}",
        f"- Current subchain: `{adversarial.get('current_subchain')}`",
        f"- Premature convergence risk: `{adversarial.get('premature_convergence_risk')}`",
        "",
        "## Fatal Objections",
        "",
    ]
    fatal = adversarial.get("fatal_objections") or []
    lines.extend(f"- {item}" for item in fatal) if fatal else lines.append("- None.")
    lines.extend(["", "## Nonfatal Objections", ""])
    nonfatal = adversarial.get("nonfatal_objections") or []
    lines.extend(f"- {item}" for item in nonfatal) if nonfatal else lines.append("- None.")
    lines.extend(["", "## Missing Counterfactuals", ""])
    counterfactuals = adversarial.get("missing_counterfactuals") or []
    lines.extend(f"- {item}" for item in counterfactuals) if counterfactuals else lines.append("- None.")
    lines.extend(["", "## Killer Tests", ""])
    tests = adversarial.get("killer_tests") or []
    lines.extend(f"- {item}" for item in tests) if tests else lines.append("- None.")
    rec = adversarial.get("route_recommendation") if isinstance(adversarial.get("route_recommendation"), dict) else {}
    lines.extend(["", "## Route Recommendation", ""])
    lines.append(f"- Action: `{rec.get('action')}`")
    lines.append(f"- Semantic reason: `{rec.get('semantic_reason')}`")
    lines.append("- Target subchains: " + (", ".join(str(item) for item in rec.get("target_subchains") or []) or "(none)"))
    return lines


def persist_deep_loop_auxiliary_reviews(cwd: Path, payload: dict[str, Any]) -> None:
    council = payload.get("research_council") if isinstance(payload.get("research_council"), dict) else {}
    if council and council.get("enabled", True):
        ensure_dir(research_councils_root(cwd))
        paths = council.setdefault("paths", {})
        json_path = Path(str(paths.get("json") or (research_councils_root(cwd) / f"{council.get('council_id')}.json")))
        md_path = Path(str(paths.get("markdown") or (research_councils_root(cwd) / f"{council.get('council_id')}.md")))
        write_json(json_path, council)
        write_lines(md_path, research_council_markdown(council))
        paths["json"] = psafe(json_path)
        paths["markdown"] = psafe(md_path)
    adversarial = payload.get("adversarial_gate") if isinstance(payload.get("adversarial_gate"), dict) else {}
    if adversarial and adversarial.get("enabled", True):
        ensure_dir(adversarial_gates_root(cwd))
        paths = adversarial.setdefault("paths", {})
        json_path = Path(str(paths.get("json") or (adversarial_gates_root(cwd) / f"{adversarial.get('review_id')}.json")))
        md_path = Path(str(paths.get("markdown") or (adversarial_gates_root(cwd) / f"{adversarial.get('review_id')}.md")))
        write_json(json_path, adversarial)
        write_lines(md_path, adversarial_gate_markdown(adversarial))
        paths["json"] = psafe(json_path)
        paths["markdown"] = psafe(md_path)


def persist_deep_loop_payload(
    cwd: Path,
    state: dict[str, Any],
    passport: dict[str, Any],
    payload: dict[str, Any],
    *,
    source: str = "deep-loop",
) -> dict[str, Any]:
    report_stem = f"{timestamp()}-{slug(payload['loop_id'], 'deep-loop')}"
    json_path = deep_loops_root(cwd) / f"{report_stem}.json"
    md_path = deep_loops_root(cwd) / f"{report_stem}.md"
    persist_deep_loop_auxiliary_reviews(cwd, payload)
    write_json(json_path, payload)
    write_lines(md_path, deep_loop_markdown(payload))
    payload["report_json"] = psafe(json_path)
    payload["report_markdown"] = psafe(md_path)
    payload["source"] = source
    write_json(json_path, payload)
    gate = payload.get("gate") or {}
    current = payload.get("current_subchain") or {}
    agent = payload.get("subchain_agent") or {}
    handoff = payload.get("handoff_package") or {}
    continuation = payload.get("continuation_contract") or {}
    append_jsonl(
        decisions_path(cwd),
        {
            "id": record_id("deep-loop", str(payload.get("loop_id"))),
            "timestamp": utc_now(),
            "type": "deep_loop_gate",
            "source": source,
            "loop_id": payload.get("loop_id"),
            "stage": payload.get("stage"),
            "current_subchain": current.get("id"),
            "subchain_agent": agent.get("agent_id"),
            "gate_decision": gate.get("decision"),
            "review_mode": payload.get("review_directive", {}).get("mode"),
            "target_subchains": handoff.get("target_subchains") or [],
            "gate_vector_summary": continuation.get("gate_vector_summary") or {},
            "blocking_dimensions": continuation.get("blocking_dimensions") or [],
            "harness_evidence": {
                "gate_result": (payload.get("harness_evidence") or {}).get("gate_result"),
                "pass_rate": (payload.get("harness_evidence") or {}).get("pass_rate"),
                "quality_score": (payload.get("harness_evidence") or {}).get("quality_score"),
                "failures_by_tag": (payload.get("harness_evidence") or {}).get("failures_by_tag"),
                "reports": (payload.get("harness_evidence") or {}).get("reports"),
            },
            "continuation_contract": {
                "target_subchains": continuation.get("target_subchains") or [],
                "blocking_dimensions": continuation.get("blocking_dimensions") or [],
                "requires_human": continuation.get("requires_human"),
            },
            "path": psafe(md_path),
        },
    )
    append_jsonl(
        artifacts_path(cwd),
        {
            "timestamp": utc_now(),
            "type": "deep_loop_report",
            "source": source,
            "loop_id": payload.get("loop_id"),
            "gate_decision": gate.get("decision"),
            "path": psafe(md_path),
        },
    )
    update_list_item(
        passport["next_actions"],
        {
            "id": f"next-deep-loop-{short_digest(str(payload.get('loop_id')) + str(gate.get('decision')))}",
            "text": handoff.get("next_work_prompt") or f"Continue deep-loop decision {gate.get('decision')}.",
            "stage": state.get("current_stage", "INTAKE"),
            "status": "todo" if gate.get("decision") != "pause_for_human" else "blocked",
            "owner": "agent" if gate.get("decision") != "pause_for_human" else "human",
            "created_at": utc_now(),
            "note": f"Deep-loop report: {psafe(md_path)}",
        },
    )
    save_passport(cwd, passport)
    state.setdefault("counters", {}).setdefault("deep_loops", 0)
    state["counters"]["deep_loops"] = int(state["counters"].get("deep_loops", 0)) + 1
    if gate.get("decision") in {"retry_same_route", "escalate_problem_loop", "pause_for_human"}:
        state["counters"]["failures"] = int(state["counters"].get("failures", 0)) + 1
    save_state(cwd, state)
    return payload


def command_deep_loop(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    payload = build_deep_loop_payload(args, cwd, state, passport)
    if args.write:
        payload = persist_deep_loop_payload(cwd, state, passport, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    else:
        print("\n".join(deep_loop_markdown(payload)).rstrip() + "\n")
    return 0


def capabilities_markdown(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# Research Loop Capability Matrix",
        "",
        f"- Generated at UTC: {payload['generated_at']}",
        f"- Available capabilities: {len(payload['available_capabilities'])}",
        f"- Missing tools: {len(payload['missing_tools'])}",
        "",
        "## Subchains",
        "",
    ]
    for chain in payload["subchains"]:
        lines.append(f"- `{chain['id']}` {chain['name']}: {', '.join(chain.get('task_types') or [])}")
    lines.extend(["", "## Available Capabilities", ""])
    for item in payload["available_capabilities"]:
        lines.append(f"- `{item['id']}` [{item.get('status')}/{item.get('kind')}] {item.get('use_for')}")
    lines.extend(["", "## Missing Tools", ""])
    for item in payload["missing_tools"]:
        lines.append(f"- `{item['name']}` ({item.get('priority', 'P?')}): {item.get('use_for')}")
    return lines


def command_capabilities(args: argparse.Namespace) -> int:
    payload = capability_matrix_payload()
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    else:
        print("\n".join(capabilities_markdown(payload)).rstrip() + "\n")
    return 0


def command_normalize(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    payload = normalize_task_input(cwd, state, passport, args.input)
    if args.format == "json":
        output = json.dumps(payload, indent=2, ensure_ascii=True, default=str) + "\n"
    else:
        output = "\n".join(normalized_prompt_markdown(payload)).rstrip() + "\n"
    if args.write:
        suffix = "json" if args.format == "json" else "md"
        path = reports_root(cwd) / f"{timestamp()}-normalized-prompt.{suffix}"
        if args.format == "json":
            write_json(path, payload)
        else:
            write_lines(path, output.splitlines())
        append_jsonl(
            decisions_path(cwd),
            {
                "id": record_id("prompt", payload.get("raw_input") or payload.get("task_type") or ""),
                "timestamp": utc_now(),
                "type": "normalized_prompt",
                "stage": state.get("current_stage", "INTAKE"),
                "task_type": payload.get("task_type"),
                "depth_level": payload.get("depth_level"),
                "path": psafe(path),
            },
        )
        print(f"Normalized prompt: {path}")
    else:
        print(output)
    return 0


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"\b(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)\b", re.IGNORECASE)


def clean_identifier(value: str | None) -> str:
    return (value or "").strip().strip(".,;:()[]{}<>")


def extract_doi(text: str) -> str | None:
    match = DOI_RE.search(text or "")
    return clean_identifier(match.group(0)) if match else None


def extract_arxiv_id(text: str) -> str | None:
    match = ARXIV_RE.search(text or "")
    return clean_identifier(match.group(1)) if match else None


def http_get_text(url: str, params: dict[str, Any] | None = None, timeout: float = 20.0) -> tuple[int, str]:
    query = urllib.parse.urlencode({key: value for key, value in (params or {}).items() if value is not None})
    target = f"{url}?{query}" if query else url
    request = urllib.request.Request(
        target,
        headers={
            "User-Agent": "codex-research-loop/0.7 (+https://openai.com/codex)",
            "Accept": "application/json, application/atom+xml, text/xml;q=0.9, */*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        return int(response.status), data.decode(charset, errors="replace")


def http_get_json(url: str, params: dict[str, Any] | None = None, timeout: float = 20.0) -> dict[str, Any]:
    status, text = http_get_text(url, params, timeout)
    if status >= 400:
        raise RuntimeError(f"HTTP {status} for {url}")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected JSON object from {url}")
    return data


def first_text(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return None


def author_names_from_crossref(item: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for author in item.get("author") or []:
        if not isinstance(author, dict):
            continue
        given = str(author.get("given") or "").strip()
        family = str(author.get("family") or "").strip()
        name = " ".join(part for part in [given, family] if part)
        if name:
            names.append(name)
    return names


def year_from_crossref(item: dict[str, Any]) -> int | None:
    for key in ["published-print", "published-online", "published", "issued"]:
        parts = ((item.get(key) or {}).get("date-parts") or [])
        if parts and parts[0]:
            try:
                return int(parts[0][0])
            except Exception:
                continue
    return None


def normalize_crossref_item(item: dict[str, Any]) -> dict[str, Any]:
    doi = item.get("DOI")
    return {
        "provider": "crossref",
        "id": doi or item.get("URL"),
        "doi": doi,
        "title": first_text(item.get("title")),
        "authors": author_names_from_crossref(item),
        "year": year_from_crossref(item),
        "venue": first_text(item.get("container-title")),
        "type": item.get("type"),
        "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else None),
        "raw": item,
    }


def query_crossref(query: str, rows: int) -> dict[str, Any]:
    doi = extract_doi(query)
    if doi:
        data = http_get_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}")
        message = data.get("message") or {}
        items = [normalize_crossref_item(message)] if isinstance(message, dict) else []
    else:
        data = http_get_json("https://api.crossref.org/works", {"query.bibliographic": query, "rows": rows})
        message = data.get("message") or {}
        items = [normalize_crossref_item(item) for item in message.get("items") or [] if isinstance(item, dict)]
    return {"provider": "crossref", "status": "ok", "results": items[:rows]}


def author_names_from_openalex(item: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for row in item.get("authorships") or []:
        if isinstance(row, dict):
            author = row.get("author") or {}
            name = author.get("display_name") if isinstance(author, dict) else None
            if name:
                names.append(str(name))
    return names


def normalize_openalex_item(item: dict[str, Any]) -> dict[str, Any]:
    source = item.get("primary_location") or {}
    source_meta = source.get("source") if isinstance(source, dict) else {}
    if not isinstance(source_meta, dict):
        source_meta = {}
    return {
        "provider": "openalex",
        "id": item.get("id"),
        "doi": item.get("doi"),
        "title": item.get("display_name") or item.get("title"),
        "authors": author_names_from_openalex(item),
        "year": item.get("publication_year"),
        "venue": source_meta.get("display_name"),
        "type": item.get("type"),
        "url": item.get("doi") or item.get("id"),
        "cited_by_count": item.get("cited_by_count"),
        "raw": item,
    }


def query_openalex(query: str, rows: int) -> dict[str, Any]:
    data = http_get_json("https://api.openalex.org/works", {"search": query, "per-page": rows})
    items = [normalize_openalex_item(item) for item in data.get("results") or [] if isinstance(item, dict)]
    return {"provider": "openalex", "status": "ok", "results": items[:rows]}


def atom_text(element: ET.Element, name: str) -> str | None:
    child = element.find(f"atom:{name}", {"atom": "http://www.w3.org/2005/Atom"})
    if child is None or child.text is None:
        return None
    return " ".join(child.text.split())


def normalize_arxiv_entry(entry: ET.Element) -> dict[str, Any]:
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    authors = []
    for author in entry.findall("atom:author", ns):
        name = atom_text(author, "name")
        if name:
            authors.append(name)
    published = atom_text(entry, "published")
    year = None
    if published:
        try:
            year = int(published[:4])
        except Exception:
            year = None
    doi = None
    doi_node = entry.find("arxiv:doi", ns)
    if doi_node is not None and doi_node.text:
        doi = doi_node.text.strip()
    return {
        "provider": "arxiv",
        "id": atom_text(entry, "id"),
        "doi": doi,
        "title": atom_text(entry, "title"),
        "authors": authors,
        "year": year,
        "venue": "arXiv",
        "type": "preprint",
        "url": atom_text(entry, "id"),
        "summary": atom_text(entry, "summary"),
    }


def query_arxiv(query: str, rows: int) -> dict[str, Any]:
    arxiv_id = extract_arxiv_id(query)
    params = {"start": 0, "max_results": rows}
    if arxiv_id:
        params["id_list"] = arxiv_id
    else:
        params["search_query"] = f"all:{query}"
    status, text = http_get_text("https://export.arxiv.org/api/query", params)
    if status >= 400:
        raise RuntimeError(f"HTTP {status} from arXiv")
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    return {"provider": "arxiv", "status": "ok", "results": [normalize_arxiv_entry(entry) for entry in entries[:rows]]}


def source_hub_lookup(query: str, provider: str, rows: int) -> dict[str, Any]:
    providers = ["crossref", "openalex", "arxiv"] if provider == "auto" else [provider]
    lookups: list[dict[str, Any]] = []
    for name in providers:
        try:
            if name == "crossref":
                lookups.append(query_crossref(query, rows))
            elif name == "openalex":
                lookups.append(query_openalex(query, rows))
            elif name == "arxiv":
                lookups.append(query_arxiv(query, rows))
            else:
                lookups.append({"provider": name, "status": "error", "error": "unknown provider"})
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError, ET.ParseError) as exc:
            lookups.append({"provider": name, "status": "error", "error": repr(exc), "results": []})
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "query": query,
        "provider": provider,
        "rows": rows,
        "lookups": lookups,
    }


def source_hub_markdown(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# Research Source Hub Results",
        "",
        f"- Generated at UTC: {payload['timestamp']}",
        f"- Query: {payload['query']}",
        f"- Provider: {payload['provider']}",
        "",
    ]
    for lookup in payload["lookups"]:
        lines.extend([f"## {lookup['provider']}", ""])
        if lookup.get("status") != "ok":
            lines.append(f"- Error: {lookup.get('error')}")
            lines.append("")
            continue
        results = lookup.get("results") or []
        if not results:
            lines.append("- No results.")
            lines.append("")
            continue
        for index, item in enumerate(results, start=1):
            authors = ", ".join((item.get("authors") or [])[:4])
            if item.get("authors") and len(item.get("authors") or []) > 4:
                authors += ", et al."
            lines.append(f"{index}. {item.get('title') or '(untitled)'}")
            lines.append(f"   - Authors: {authors or '(not provided)'}")
            lines.append(f"   - Year: {item.get('year') or '(not provided)'}")
            lines.append(f"   - Venue: {item.get('venue') or '(not provided)'}")
            lines.append(f"   - DOI: {item.get('doi') or '(not provided)'}")
            lines.append(f"   - URL: {item.get('url') or '(not provided)'}")
        lines.append("")
    return lines


def record_source_hub_materials(cwd: Path, state: dict[str, Any], passport: dict[str, Any], payload: dict[str, Any]) -> int:
    count = 0
    for lookup in payload.get("lookups") or []:
        if lookup.get("status") != "ok":
            continue
        for item in lookup.get("results") or []:
            identity = item.get("doi") or item.get("url") or item.get("id") or item.get("title")
            if not identity:
                continue
            material = {
                "id": record_id("mat", str(identity)),
                "kind": "source-metadata",
                "title": item.get("title"),
                "path": None,
                "source": item.get("doi") or item.get("url") or item.get("id"),
                "status": "external",
                "note": f"Imported from research-source-hub provider={item.get('provider')}",
                "exists": None,
                "size": None,
                "sha256": None,
                "metadata": {key: value for key, value in item.items() if key != "raw"},
                "created_at": utc_now(),
            }
            update_list_item(passport["materials"], material)
            append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "material", **material})
            count += 1
    if count:
        state["counters"]["materials"] = int(state["counters"].get("materials", 0)) + count
        save_state(cwd, state)
        save_passport(cwd, passport)
    return count


def command_source_hub(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    rows = max(1, min(int(args.rows), 10))
    payload = source_hub_lookup(args.query, args.provider, rows)
    recorded = record_source_hub_materials(cwd, state, passport, payload) if args.record_materials else 0
    payload["recorded_materials"] = recorded
    if args.format == "json":
        output = json.dumps(payload, indent=2, ensure_ascii=True, default=str) + "\n"
    else:
        output = "\n".join(source_hub_markdown(payload)).rstrip() + "\n"
    if args.write:
        suffix = "json" if args.format == "json" else "md"
        path = reports_root(cwd) / f"{timestamp()}-source-hub.{suffix}"
        if args.format == "json":
            write_json(path, payload)
        else:
            write_lines(path, output.splitlines())
        append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "source_hub_lookup", "query": args.query, "path": psafe(path)})
        print(f"Source hub report: {path}")
    else:
        print(output)
    return 0


class SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name in {"script", "style", "noscript", "svg", "canvas"}:
            self._skip_depth += 1
        if name == "title":
            self._in_title = True
        if name in {"p", "div", "section", "article", "br", "li", "tr", "h1", "h2", "h3"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name in {"script", "style", "noscript", "svg", "canvas"} and self._skip_depth:
            self._skip_depth -= 1
        if name == "title":
            self._in_title = False
        if name in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3"}:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        self.text_parts.append(text)

    def title(self) -> str | None:
        text = " ".join(self.title_parts).strip()
        return html.unescape(text) if text else None

    def body_text(self, limit: int = 60000) -> str:
        text = "\n".join(self.text_parts)
        text = html.unescape(text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()[:limit]


def ingest_root(cwd: Path) -> Path:
    return storage_bucket_path(cwd, "ingest_cache")


def articles_root(cwd: Path) -> Path:
    return storage_bucket_path(cwd, "articles")


def data_root(cwd: Path) -> Path:
    return storage_bucket_path(cwd, "data_packages")


def is_url_source(source: str) -> bool:
    parsed = urllib.parse.urlparse(source)
    return parsed.scheme.lower() in {"http", "https"}


def source_basename(source: str, fallback: str = "content") -> str:
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme:
        name = Path(parsed.path).name or parsed.netloc or fallback
    else:
        name = Path(source).name or fallback
    return slug(name, fallback)


def guess_extension(content_type: str | None, source: str, family: str) -> str:
    lower_source = urllib.parse.urlparse(source).path.lower() if is_url_source(source) else source.lower()
    for ext in [".html", ".htm", ".json", ".jsonl", ".csv", ".tsv", ".parquet", ".xlsx", ".xls", ".md", ".txt", ".pdf", ".xml"]:
        if lower_source.endswith(ext):
            return ext
    content_type = (content_type or "").split(";", 1)[0].strip().lower()
    if content_type:
        guessed = mimetypes.guess_extension(content_type)
        if guessed:
            return ".html" if guessed in {".htm"} else guessed
    if family == "data":
        return ".dat"
    if family == "article":
        return ".html"
    return ".bin"


def decode_bytes(data: bytes, content_type: str | None = None) -> str:
    charset = None
    if content_type:
        match = re.search(r"charset=([^;\s]+)", content_type, flags=re.IGNORECASE)
        if match:
            charset = match.group(1).strip("\"'")
    for encoding in [charset, "utf-8", "utf-8-sig", "gb18030", "latin-1"]:
        if not encoding:
            continue
        try:
            return data.decode(encoding)
        except Exception:
            continue
    return data.decode("utf-8", errors="replace")


def fetch_or_read_source(source: str, max_bytes: int, base_dir: Path) -> dict[str, Any]:
    if is_url_source(source):
        request = urllib.request.Request(
            source,
            headers={
                "User-Agent": "codex-research-loop/0.7 (+https://openai.com/codex)",
                "Accept": "text/html,application/json,text/csv,text/plain,application/pdf,*/*;q=0.5",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise ValueError(f"Source exceeds max bytes: {source}")
            return {
                "source": source,
                "origin": "url",
                "final_url": response.geturl(),
                "content_type": response.headers.get("content-type"),
                "bytes": data,
            }
    path = Path(source).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    path = path.resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"Source file does not exist: {source}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"Source exceeds max bytes: {path}")
    return {
        "source": source,
        "origin": "file",
        "final_url": None,
        "path": psafe(path),
        "content_type": mimetypes.guess_type(str(path))[0],
        "bytes": path.read_bytes(),
    }


def infer_content_family(source: str, content_type: str | None, ext: str, requested: str) -> str:
    if requested != "auto":
        return requested
    content_type = (content_type or "").lower()
    if ext in {".csv", ".tsv", ".json", ".jsonl", ".parquet", ".xlsx", ".xls"} or any(token in content_type for token in ["json", "csv", "tab-separated-values", "parquet", "spreadsheet", "excel"]):
        return "data"
    if ext in {".html", ".htm", ".md", ".txt", ".pdf"} or any(token in content_type for token in ["html", "markdown", "pdf", "plain"]):
        return "article"
    return "file"


def csv_schema_from_text(text: str, delimiter: str) -> dict[str, Any]:
    sample = text[:200000]
    reader = csv.reader(io.StringIO(sample), delimiter=delimiter)
    rows = []
    for index, row in enumerate(reader):
        rows.append(row)
        if index >= 20:
            break
    headers = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []
    columns = []
    for column_index, name in enumerate(headers):
        values = [row[column_index] for row in data_rows if column_index < len(row)]
        non_empty = [value for value in values if value != ""]
        inferred = "string"
        if non_empty and all(re.fullmatch(r"[-+]?\d+", value or "") for value in non_empty):
            inferred = "integer"
        elif non_empty and all(re.fullmatch(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", value or "") for value in non_empty):
            inferred = "number"
        columns.append({"name": name or f"column_{column_index + 1}", "index": column_index, "inferred_type": inferred, "sample_values": values[:5]})
    return {"format": "csv" if delimiter == "," else "tsv", "columns": columns, "sample_row_count": len(data_rows), "sample_rows": data_rows[:5]}


def json_schema_from_text(text: str) -> dict[str, Any]:
    data = json.loads(text)
    rows = data if isinstance(data, list) else data.get("data") if isinstance(data, dict) and isinstance(data.get("data"), list) else None
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        columns = []
        keys = sorted({key for row in rows[:100] if isinstance(row, dict) for key in row.keys()})
        for key in keys:
            values = [row.get(key) for row in rows[:20] if isinstance(row, dict)]
            types = sorted({type(value).__name__ for value in values if value is not None})
            columns.append({"name": key, "inferred_types": types or ["null"], "sample_values": values[:5]})
        return {"format": "json", "top_level": "array" if isinstance(data, list) else "object", "columns": columns, "sample_row_count": min(len(rows), 100)}
    return {"format": "json", "top_level": type(data).__name__, "columns": [], "sample_row_count": 0}


def article_markdown(title: str | None, source: str, text: str, metadata: dict[str, Any]) -> list[str]:
    return [
        f"# {title or source_basename(source, 'article')}",
        "",
        "- Type: article-ingest",
        f"- Source: {source}",
        f"- Content type: {metadata.get('content_type') or '(unknown)'}",
        f"- Retrieved at UTC: {metadata.get('retrieved_at')}",
        "",
        "## Extracted Text",
        "",
        text or "(No text extracted. Store raw file and route to the appropriate reader skill.)",
    ]


def data_readme(dataset_id: str, source: str, schema: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    columns = schema.get("columns") or []
    lines = [
        f"# Dataset {dataset_id}",
        "",
        f"- Source: {source}",
        f"- Content type: {metadata.get('content_type') or '(unknown)'}",
        f"- Retrieved at UTC: {metadata.get('retrieved_at')}",
        f"- Format: {schema.get('format') or '(unknown)'}",
        f"- Columns: {len(columns)}",
        "",
        "## Storage Contract",
        "",
        "- `raw/` stores the original fetched or imported bytes.",
        "- `metadata.json` stores provenance, source, hashes, and route target.",
        "- `schema.json` stores lightweight inferred columns and sample values.",
        "- Downstream analysis should read this package instead of ad hoc temp files.",
        "",
        "## Columns",
        "",
    ]
    if not columns:
        lines.append("- (No tabular columns inferred.)")
    for column in columns[:80]:
        dtype = column.get("inferred_type") or ",".join(column.get("inferred_types") or [])
        lines.append(f"- `{column.get('name')}`: {dtype or 'unknown'}")
    return lines


def write_wiki_ingest_page(wiki_root: str, item: dict[str, Any]) -> str:
    root = Path(wiki_root).expanduser().resolve()
    sources = root / "sources"
    topics = root / "topics"
    ensure_dir(sources)
    ensure_dir(topics)
    page_name = f"{item['family']}-{slug(item.get('title') or item['source'], 'content')}-{item['id'][-8:]}.md"
    page = sources / page_name
    link_target = "Article Processing Inbox" if item["family"] == "article" else "Data Ingest Inbox"
    lines = [
        f"# {item.get('title') or item['source']}",
        "",
        f"- Type: {item['family']}",
        f"- Source: {item['source']}",
        f"- Route target: [[{link_target}]]",
        f"- Material id: {item.get('material_id') or ''}",
        f"- Package: {item.get('package_path') or item.get('content_path') or ''}",
        "",
        "## Summary",
        "",
        item.get("summary") or "(No summary generated.)",
        "",
        "## Links",
        "",
        f"- [[{link_target}]]",
    ]
    write_lines(page, lines)
    hub = topics / ("article-processing-inbox.md" if item["family"] == "article" else "data-ingest-inbox.md")
    existing = hub.read_text(encoding="utf-8", errors="replace").splitlines() if hub.exists() else [f"# {link_target}", "", "## Items", ""]
    link = f"- [[{page.stem}]]"
    if link not in existing:
        existing.append(link)
    write_lines(hub, existing)
    return psafe(page)


def ingest_one_source(cwd: Path, source: str, mode: str, max_bytes: int, write_wiki: bool, wiki_root: str | None) -> dict[str, Any]:
    fetched = fetch_or_read_source(source, max_bytes, cwd)
    content_type = fetched.get("content_type")
    ext = guess_extension(str(content_type or ""), source, mode)
    family = infer_content_family(source, str(content_type or ""), ext, mode)
    item_id = f"ing-{timestamp()}-{short_digest(source + str(time.time_ns()))}"
    package_name = f"{item_id}-{source_basename(source, family)}"
    raw_name = f"raw{ext}"
    retrieved_at = utc_now()
    raw_bytes = fetched["bytes"]
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "id": item_id,
        "source": source,
        "origin": fetched.get("origin"),
        "final_url": fetched.get("final_url"),
        "content_type": content_type,
        "retrieved_at": retrieved_at,
        "byte_count": len(raw_bytes),
        "sha256": raw_sha,
        "family": family,
        "route_target": "article-processing-chain" if family == "article" else "standard-data-package" if family == "data" else "material-registry",
        "storage_policy": psafe(storage_policy_path(cwd)),
        "storage_bucket": "articles" if family == "article" else "data_packages" if family == "data" else "ingest_cache",
    }
    ingest_dir = ingest_root(cwd) / package_name
    ensure_dir(ingest_dir)
    raw_path = ingest_dir / raw_name
    raw_path.write_bytes(raw_bytes)
    write_json(ingest_dir / "metadata.json", metadata)
    text = ""
    title = None
    content_path = None
    package_path = psafe(ingest_dir)
    summary = ""

    if family == "article":
        article_dir = articles_root(cwd) / package_name
        ensure_dir(article_dir)
        shutil.copy2(raw_path, article_dir / raw_name)
        if ext in {".html", ".htm"} or "html" in str(content_type or "").lower():
            extractor = SimpleHTMLTextExtractor()
            extractor.feed(decode_bytes(raw_bytes, str(content_type or "")))
            title = extractor.title()
            text = extractor.body_text()
        elif ext in {".md", ".txt"}:
            text = decode_bytes(raw_bytes, str(content_type or ""))[:60000]
            title = text.splitlines()[0].lstrip("# ").strip() if text.splitlines() else source_basename(source, "article")
        elif ext == ".pdf":
            title = source_basename(source, "article")
            text = "PDF stored as raw input. Use the `pdf` or `nature-reader` skill for layout-aware text, figure, and table extraction."
        else:
            title = source_basename(source, "article")
            text = decode_bytes(raw_bytes, str(content_type or ""))[:60000]
        summary = text[:800] if text else ""
        write_json(article_dir / "metadata.json", {**metadata, "title": title})
        write_lines(article_dir / "content.md", article_markdown(title, source, text, metadata))
        content_path = psafe(article_dir / "content.md")
        package_path = psafe(article_dir)
    elif family == "data":
        dataset_dir = data_root(cwd) / package_name
        raw_dir = dataset_dir / "raw"
        ensure_dir(raw_dir)
        shutil.copy2(raw_path, raw_dir / raw_name)
        text = decode_bytes(raw_bytes, str(content_type or ""))
        schema: dict[str, Any]
        try:
            if ext == ".json" or "json" in str(content_type or "").lower():
                schema = json_schema_from_text(text)
            elif ext == ".tsv":
                schema = csv_schema_from_text(text, "\t")
            else:
                schema = csv_schema_from_text(text, ",")
        except Exception as exc:
            schema = {"format": ext.lstrip(".") or "unknown", "columns": [], "sample_row_count": 0, "error": repr(exc)}
        write_json(dataset_dir / "metadata.json", metadata)
        write_json(dataset_dir / "schema.json", schema)
        write_lines(dataset_dir / "README.md", data_readme(item_id, source, schema, metadata))
        content_path = psafe(dataset_dir / "README.md")
        package_path = psafe(dataset_dir)
        summary = f"Data package with format={schema.get('format')} columns={len(schema.get('columns') or [])}."
    else:
        title = source_basename(source, "file")
        summary = f"Raw file stored with content_type={content_type or 'unknown'}."
        content_path = psafe(raw_path)

    item = {
        "id": item_id,
        "source": source,
        "family": family,
        "title": title,
        "content_type": content_type,
        "raw_path": psafe(raw_path),
        "content_path": content_path,
        "package_path": package_path,
        "metadata_path": psafe(ingest_dir / "metadata.json"),
        "sha256": raw_sha,
        "summary": summary,
        "route_target": metadata["route_target"],
        "storage_bucket": metadata["storage_bucket"],
        "storage_policy": metadata["storage_policy"],
    }
    if write_wiki and wiki_root:
        item["wiki_page"] = write_wiki_ingest_page(wiki_root, item)
    return item


def content_ingest_markdown(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# Content Ingest Report",
        "",
        f"- Created at UTC: {payload['timestamp']}",
        f"- Project root: {payload['project_root']}",
        f"- Items: {len(payload['items'])}",
        "",
        "## Items",
        "",
    ]
    for item in payload["items"]:
        lines.append(f"- `{item['id']}` {item['family']}: {item.get('title') or item['source']}")
        lines.append(f"  - Route target: {item.get('route_target')}")
        lines.append(f"  - Package: `{item.get('package_path')}`")
        if item.get("wiki_page"):
            lines.append(f"  - Wiki page: `{item.get('wiki_page')}`")
    return lines


def record_ingested_materials(cwd: Path, state: dict[str, Any], passport: dict[str, Any], items: list[dict[str, Any]]) -> int:
    count = 0
    for item in items:
        family = item.get("family")
        kind = "article" if family == "article" else "dataset" if family == "data" else "ingested-file"
        material = {
            "id": record_id("mat", item.get("source") or item["id"]),
            "kind": kind,
            "title": item.get("title") or item.get("source"),
            "path": item.get("content_path") or item.get("raw_path"),
            "source": item.get("source"),
            "status": "available",
            "note": f"Imported by content-ingest route_target={item.get('route_target')}",
            "exists": True,
            "size": None,
            "sha256": item.get("sha256"),
            "metadata": {key: value for key, value in item.items() if key not in {"summary"}},
            "created_at": utc_now(),
        }
        item["material_id"] = material["id"]
        update_list_item(passport["materials"], material)
        append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "material", **material})
        count += 1
    if count:
        state["counters"]["materials"] = int(state["counters"].get("materials", 0)) + count
        save_state(cwd, state)
        save_passport(cwd, passport)
    return count


def command_content_ingest(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    items: list[dict[str, Any]] = []
    for source in args.source:
        items.append(
            ingest_one_source(
                cwd,
                source,
                args.mode,
                max(1024, int(args.max_bytes)),
                False,
                None,
            )
        )
    recorded = record_ingested_materials(cwd, state, passport, items) if args.record_materials else 0
    if args.write_wiki and args.wiki_root:
        for item in items:
            item["wiki_page"] = write_wiki_ingest_page(args.wiki_root, item)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "mode": args.mode,
        "recorded_materials": recorded,
        "items": items,
    }
    if args.write:
        suffix = "json" if args.format == "json" else "md"
        path = reports_root(cwd) / f"{timestamp()}-content-ingest.{suffix}"
        if args.format == "json":
            write_json(path, payload)
        else:
            write_lines(path, content_ingest_markdown(payload))
        append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "content_ingest", "path": psafe(path), "item_count": len(items)})
        print(f"Content ingest report: {path}")
    else:
        if args.format == "json":
            print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
        else:
            print("\n".join(content_ingest_markdown(payload)).rstrip() + "\n")
    return 0


def problem_lab_root(cwd: Path) -> Path:
    return storage_bucket_path(cwd, "scratch") / "research-loop-labs"


def problem_case_path(cwd: Path, case_id: str) -> Path:
    return problem_cases_root(cwd) / f"{case_id}.json"


def problem_case_id(problem: str, explicit: str | None = None) -> str:
    if explicit:
        return slug(explicit, "problem-case")
    return f"prob-{timestamp()}-{short_digest(problem)}"


def read_text_sample(path: Path, limit: int = 4000) -> str | None:
    try:
        if not path.exists() or not path.is_file() or path.stat().st_size > HASH_LIMIT_BYTES * 10:
            return None
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return None


def project_manifest_context(cwd: Path) -> list[dict[str, Any]]:
    names = [
        "README.md",
        "AGENTS.md",
        "CONTEXT.md",
        "pyproject.toml",
        "requirements.txt",
        "environment.yml",
        "package.json",
        "Cargo.toml",
        "DESCRIPTION",
        "renv.lock",
    ]
    manifests: list[dict[str, Any]] = []
    for name in names:
        path = cwd / name
        sample = read_text_sample(path, 2400)
        if sample is None:
            continue
        manifests.append({"path": name, "sample": sample})
    for path in sorted((cwd / "docs").glob("*.md"))[:6] if (cwd / "docs").exists() else []:
        sample = read_text_sample(path, 1800)
        if sample:
            manifests.append({"path": psafe(path.relative_to(cwd)), "sample": sample})
    return manifests


def top_level_listing(cwd: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for path in sorted(cwd.iterdir(), key=lambda item: item.name.lower()):
            if path.name in {".git", ".venv", "node_modules", "__pycache__"}:
                continue
            rows.append(
                {
                    "name": path.name,
                    "kind": "directory" if path.is_dir() else "file",
                    "size": path.stat().st_size if path.is_file() else None,
                }
            )
            if len(rows) >= 80:
                break
    except Exception:
        pass
    return rows


def collect_problem_context(cwd: Path, state: dict[str, Any], passport: dict[str, Any], problem: str) -> dict[str, Any]:
    route_graph = build_route_graph(cwd, state, passport, problem)
    storage_policy = load_storage_policy(cwd)
    return {
        "project_root": psafe(cwd),
        "project_id": state.get("project_id"),
        "stage": state.get("current_stage"),
        "problem": problem,
        "git": git_info(cwd),
        "storage_policy": {
            "style": storage_policy.get("style"),
            "policy_path": psafe(storage_policy_path(cwd)),
            "buckets": [
                {
                    "id": bucket.get("id"),
                    "path": bucket.get("path"),
                    "exists": bucket.get("exists"),
                    "purpose": bucket.get("purpose"),
                }
                for bucket in storage_policy.get("buckets") or []
            ],
        },
        "passport_summary": {
            "title": passport.get("project_title"),
            "domain": passport.get("domain"),
            "research_question": passport.get("research_question"),
            "targets": passport.get("output_targets") or [],
            "profile": passport.get("profile") or {},
            "material_count": len(passport.get("materials") or []),
            "claim_count": len(passport.get("key_claims") or []),
            "open_risk_count": len([item for item in passport.get("risks") or [] if isinstance(item, dict) and item.get("status") == "open"]),
            "active_next_count": len(active_next_actions(passport)),
            "material_kinds": sorted(material_kinds(passport)),
        },
        "manifests": project_manifest_context(cwd),
        "top_level": top_level_listing(cwd),
        "route_graph": {
            "task_type": route_graph.get("task_type"),
            "depth_level": route_graph.get("depth_level"),
            "subchains": [{"id": item.get("id"), "name": item.get("name"), "depth": item.get("depth")} for item in route_graph.get("subchains") or []],
            "blockers": route_graph.get("blockers") or [],
            "warnings": route_graph.get("warnings") or [],
        },
    }


def problem_signal_text(context: dict[str, Any]) -> str:
    parts = [str(context.get("problem") or "")]
    for manifest in context.get("manifests") or []:
        parts.append(str(manifest.get("path") or ""))
    parts.extend(str(item.get("name") or "") for item in context.get("top_level") or [])
    passport = context.get("passport_summary") or {}
    parts.extend(str(value) for value in passport.get("material_kinds") or [])
    parts.extend(str(value) for value in passport.get("targets") or [])
    return " ".join(parts).lower()


def add_expert(experts: list[dict[str, Any]], seen: set[str], expert_id: str, title: str, source: str, focus: list[str], evaluation_questions: list[str]) -> None:
    if expert_id in seen:
        return
    seen.add(expert_id)
    experts.append(
        {
            "id": expert_id,
            "title": title,
            "source": source,
            "focus": focus,
            "evaluation_questions": evaluation_questions,
        }
    )


def construct_problem_experts(context: dict[str, Any]) -> list[dict[str, Any]]:
    text = problem_signal_text(context)
    experts: list[dict[str, Any]] = []
    seen: set[str] = set()
    native_sources = [item.get("path") for item in context.get("manifests") or [] if item.get("path") in {"AGENTS.md", "CONTEXT.md", "README.md"}]
    add_expert(
        experts,
        seen,
        "project-context-analyst",
        "Project Context Analyst",
        "repository-native" if native_sources else "constructed",
        ["project background", "current objectives", "missing assumptions"],
        ["What is the project trying to accomplish?", "Which background facts are missing before diagnosis?", "Which existing repository instructions constrain the fix?"],
    )
    add_expert(
        experts,
        seen,
        "repository-diagnostic-engineer",
        "Repository Diagnostic Engineer",
        "constructed",
        ["failure reproduction", "repository structure", "root cause isolation"],
        ["What is the likely failure boundary?", "Which files or subsystems should be inspected first?", "What minimal reproduction would separate symptoms from root cause?"],
    )
    add_expert(
        experts,
        seen,
        "test-validation-engineer",
        "Test and Validation Engineer",
        "constructed",
        ["test strategy", "smoke checks", "regression gates"],
        ["Which tests prove the issue is fixed?", "Which tests are too broad for the first pass?", "What failure logs must be preserved?"],
    )
    add_expert(
        experts,
        seen,
        "isolation-storage-guardian",
        "Isolation and Storage Guardian",
        "constructed",
        ["lab isolation", "artifact placement", "promotion safety"],
        ["Are analysis and adjustment files outside the core chain?", "Could test output pollute project state?", "What must be true before core files are touched?"],
    )
    add_expert(
        experts,
        seen,
        "implementation-gate-reviewer",
        "Implementation Gate Reviewer",
        "constructed",
        ["approval thresholds", "risk review", "promotion decision"],
        ["Does the evidence justify changing core files?", "Which risks remain open?", "Should the case be promoted, held, or escalated?"],
    )
    if any(token in text for token in ["data", "dataset", "csv", "json", "parquet", "数据"]):
        add_expert(
            experts,
            seen,
            "data-pipeline-expert",
            "Data Pipeline Expert",
            "constructed-on-demand",
            ["data contracts", "schema drift", "provenance"],
            ["Which data contract may be broken?", "Are raw, interim, processed, and package layers separated?", "What validation should run before downstream analysis?"],
        )
    if any(token in text for token in ["paper", "manuscript", "citation", "reviewer", "literature", "论文", "文献", "审稿"]):
        add_expert(
            experts,
            seen,
            "scientific-writing-evidence-expert",
            "Scientific Writing and Evidence Expert",
            "constructed-on-demand",
            ["claims", "citations", "review readiness"],
            ["Which claims or citations are implicated?", "What evidence must be read before revision?", "Does the proposed change affect manuscript integrity?"],
        )
    if any(token in text for token in ["pyproject", "requirements", ".py", "pytest", "python", "venv"]):
        add_expert(
            experts,
            seen,
            "python-runtime-expert",
            "Python Runtime Expert",
            "repository-signal",
            ["Python environment", "pytest", "dependency boundaries"],
            ["Which interpreter should run validation?", "Are dependencies or environment variables missing?", "Which Python tests are the narrowest reliable gate?"],
        )
    if any(token in text for token in ["package.json", "node", "npm", "react", "vite", "typescript", "frontend"]):
        add_expert(
            experts,
            seen,
            "frontend-runtime-expert",
            "Frontend Runtime Expert",
            "repository-signal",
            ["frontend build", "browser smoke tests", "UI regression"],
            ["Which build or browser smoke test should run?", "Could generated assets contaminate source files?", "Which viewport or interaction must be verified?"],
        )
    if any(token in text for token in ["model", "train", "gpu", "cuda", "experiment", "simulation", "notebook", "ml", "机器学习"]):
        add_expert(
            experts,
            seen,
            "ml-experiment-expert",
            "ML and Experiment Expert",
            "constructed-on-demand",
            ["experiment reproducibility", "metrics", "resource failures"],
            ["Which metric defines success?", "Which run artifacts are authoritative?", "Are failures caused by code, data, resources, or configuration?"],
        )
    return experts


def expert_prompt_lines(case_id: str, problem: str, expert: dict[str, Any], lab_dir: Path) -> list[str]:
    lines = [
        f"# Expert Evaluation Prompt: {expert['title']}",
        "",
        f"- Case id: `{case_id}`",
        f"- Source: {expert.get('source')}",
        f"- Lab directory: `{psafe(lab_dir)}`",
        "",
        "## Problem",
        "",
        problem,
        "",
        "## Focus",
        "",
    ]
    lines.extend(f"- {item}" for item in expert.get("focus") or [])
    lines.extend(["", "## Questions", ""])
    lines.extend(f"- {item}" for item in expert.get("evaluation_questions") or [])
    lines.extend(
        [
            "",
            "## Required Output",
            "",
            "- Root-cause hypothesis.",
            "- Evidence needed to confirm or reject it.",
            "- Tests to run inside the lab or with logs captured into the lab.",
            "- Adjustment proposal that does not mutate core files yet.",
            "- Promotion recommendation: approve, hold, or escalate.",
        ]
    )
    return lines


def write_expert_prompts(case_id: str, problem: str, experts: list[dict[str, Any]], lab_dir: Path) -> list[str]:
    prompts_dir = lab_dir / "experts"
    ensure_dir(prompts_dir)
    paths: list[str] = []
    for expert in experts:
        path = prompts_dir / f"{expert['id']}.md"
        write_lines(path, expert_prompt_lines(case_id, problem, expert, lab_dir))
        paths.append(psafe(path))
    write_json(prompts_dir / "expert-panel.json", {"case_id": case_id, "experts": experts})
    return paths


def run_problem_test_commands(cwd: Path, lab_dir: Path, commands: list[dict[str, Any] | str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    tests_dir = lab_dir / "tests"
    ensure_dir(tests_dir)
    for index, spec in enumerate(commands, start=1):
        if isinstance(spec, dict):
            command = str(spec.get("command") or "")
            role = str(spec.get("role") or "validation")
            expect_failure = bool(spec.get("expect_failure"))
        else:
            command = str(spec)
            role = "validation"
            expect_failure = False
        safe_name = f"{index:02d}-{slug(command.split()[0] if command.split() else 'command', 'command')}"
        stdout_path = tests_dir / f"{safe_name}.stdout.log"
        stderr_path = tests_dir / f"{safe_name}.stderr.log"
        started = time.monotonic()
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            capture_output=True,
            check=False,
        )
        elapsed = time.monotonic() - started
        stdout_path.write_text(proc.stdout or "", encoding="utf-8")
        stderr_path.write_text(proc.stderr or "", encoding="utf-8")
        gate_passed = (proc.returncode != 0) if expect_failure else (proc.returncode == 0)
        if expect_failure:
            status = "reproduced" if proc.returncode != 0 else "not_reproduced"
        else:
            status = "passed" if proc.returncode == 0 else "failed"
        results.append(
            {
                "index": index,
                "command": command,
                "role": role,
                "expect_failure": expect_failure,
                "exit_code": proc.returncode,
                "elapsed_seconds": round(elapsed, 3),
                "status": status,
                "gate_passed": gate_passed,
                "stdout": psafe(stdout_path),
                "stderr": psafe(stderr_path),
            }
        )
    write_json(tests_dir / "summary.json", {"timestamp": utc_now(), "results": results})
    return results


def deterministic_expert_evaluations(experts: list[dict[str, Any]], context: dict[str, Any], tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failed_tests = [item for item in tests if not item.get("gate_passed", item.get("exit_code") == 0)]
    route_warnings = (context.get("route_graph") or {}).get("warnings") or []
    route_blockers = (context.get("route_graph") or {}).get("blockers") or []
    storage_missing = [bucket for bucket in (context.get("storage_policy") or {}).get("buckets") or [] if not bucket.get("exists") and bucket.get("id") in {"scratch", "data_packages", "articles"}]
    evaluations: list[dict[str, Any]] = []
    for expert in experts:
        concerns: list[str] = []
        if failed_tests:
            concerns.append(f"{len(failed_tests)} gate command(s) failed; inspect lab test logs before promotion.")
        if route_blockers:
            concerns.append(f"{len(route_blockers)} route blocker(s) are present.")
        if expert["id"] == "isolation-storage-guardian" and storage_missing:
            concerns.append("Some isolation or material buckets were missing before this run; ensure lab artifacts remain in scratch.")
        if expert["id"] == "project-context-analyst" and not (context.get("passport_summary") or {}).get("title"):
            concerns.append("Project title is not set, which weakens cross-thread summaries.")
        if not concerns:
            concerns.append("No blocking concern detected by deterministic preflight.")
        recommendation = "approve" if not failed_tests and not route_blockers else "hold"
        if expert["id"] == "implementation-gate-reviewer" and (failed_tests or route_blockers):
            recommendation = "hold"
        if expert["id"] == "isolation-storage-guardian" and storage_missing and not failed_tests:
            recommendation = "approve-with-note"
        evaluations.append(
            {
                "expert_id": expert["id"],
                "title": expert["title"],
                "recommendation": recommendation,
                "concerns": concerns,
                "required_evidence": [
                    "project context snapshot",
                    "expert prompt",
                    "test logs" if tests else "explicit no-test rationale",
                    "adjustment plan",
                    "promotion gate",
                ],
                "suggested_tests": [item.get("command") for item in tests] or ["Run a narrow reproduction command before promoting core changes."],
            }
        )
    return evaluations


def problem_gate(evaluations: list[dict[str, Any]], tests: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    passed = len([item for item in tests if item.get("gate_passed", item.get("exit_code") == 0)])
    failed = len([item for item in tests if not item.get("gate_passed", item.get("exit_code") == 0)])
    reproduced = len([item for item in tests if item.get("role") == "reproduction" and item.get("status") == "reproduced"])
    test_score = 1.0 if not tests else passed / max(1, len(tests))
    approvals = len([item for item in evaluations if str(item.get("recommendation")).startswith("approve")])
    expert_score = approvals / max(1, len(evaluations))
    score = round((test_score * 0.55) + (expert_score * 0.45), 3)
    status = "approved" if score >= threshold and failed == 0 else "hold"
    if not tests:
        status = "analysis_only"
    return {
        "threshold": threshold,
        "score": score,
        "status": status,
        "test_score": round(test_score, 3),
        "expert_score": round(expert_score, 3),
        "passed_tests": passed,
        "failed_tests": failed,
        "reproduced_failures": reproduced,
        "approved_experts": approvals,
        "expert_count": len(evaluations),
        "promotion_allowed": status == "approved",
        "promotion_rule": "Only promote when score >= threshold, no gate command failures, and gate status is approved. Reproduction commands are expected to fail and count as passed when they reproduce the blocker.",
    }


def adjustment_plan_lines(case_id: str, problem: str, gate: dict[str, Any]) -> list[str]:
    return [
        "# Isolated Adjustment Plan",
        "",
        f"- Case id: `{case_id}`",
        f"- Gate status: {gate.get('status')}",
        f"- Gate score: {gate.get('score')} / threshold {gate.get('threshold')}",
        "",
        "## Problem",
        "",
        problem,
        "",
        "## Adjustment Boundary",
        "",
        "- Keep all analysis, test logs, candidate notes, and drafts inside this lab until promotion.",
        "- Do not edit project core files from this plan directly.",
        "- After promotion, apply the smallest verified change and rerun the listed tests.",
        "",
        "## Candidate Change Slots",
        "",
        "- Root-cause patch:",
        "- Configuration or storage fix:",
        "- Test or validation update:",
        "- Documentation or handoff update:",
        "",
        "## Promotion Checklist",
        "",
        "- Expert gate is approved.",
        "- Test commands pass or no-test rationale is accepted by the user.",
        "- Remaining risks are recorded or explicitly deferred.",
        "- Core file edits are small and trace back to this case.",
    ]


def problem_loop_markdown(payload: dict[str, Any]) -> list[str]:
    gate = payload.get("gate") or {}
    lines = [
        "# Problem Loop Report",
        "",
        f"- Case id: `{payload['case_id']}`",
        f"- Created at UTC: {payload['timestamp']}",
        f"- Project root: {payload['project_root']}",
        f"- Lab directory: `{payload['lab_directory']}`",
        f"- Gate status: {gate.get('status')}",
        f"- Gate score: {gate.get('score')} / threshold {gate.get('threshold')}",
        f"- Experts: {len(payload.get('experts') or [])}",
        f"- Tests: {len(payload.get('tests') or [])}",
        "",
        "## Problem",
        "",
        payload.get("problem") or "",
        "",
        "## Expert Recommendations",
        "",
    ]
    for evaluation in payload.get("evaluations") or []:
        lines.append(f"- `{evaluation['expert_id']}` {evaluation.get('recommendation')}")
        for concern in evaluation.get("concerns") or []:
            lines.append(f"  - {concern}")
    lines.extend(["", "## Tests", ""])
    if payload.get("tests"):
        for test in payload["tests"]:
            role = test.get("role") or "validation"
            gate = "gate-pass" if test.get("gate_passed") else "gate-fail"
            lines.append(f"- `{test['command']}` [{role}] -> {test['status']} ({test['exit_code']}, {gate})")
            lines.append(f"  - stdout: `{test['stdout']}`")
            lines.append(f"  - stderr: `{test['stderr']}`")
    else:
        lines.append("- No test commands were run; gate status remains analysis-only.")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Context: `{payload.get('context_path')}`",
            f"- Expert panel: `{payload.get('expert_panel_path')}`",
            f"- Adjustment plan: `{payload.get('adjustment_plan_path')}`",
            f"- Gate: `{payload.get('gate_path')}`",
        ]
    )
    return lines


def command_problem_loop(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    case_id = problem_case_id(args.problem, args.case_id)
    lab_dir = problem_lab_root(cwd) / case_id
    for child in ["context", "experts", "analysis", "tests", "adjustments", "gate"]:
        ensure_dir(lab_dir / child)
    context = collect_problem_context(cwd, state, passport, args.problem)
    experts = construct_problem_experts(context)
    prompt_paths = write_expert_prompts(case_id, args.problem, experts, lab_dir)
    context_path = lab_dir / "context" / "project-context.json"
    write_json(context_path, context)
    command_specs: list[dict[str, Any]] = []
    for command in args.repro_command or []:
        command_specs.append({"command": command, "role": "reproduction", "expect_failure": True})
    for command in args.test_command or []:
        command_specs.append({"command": command, "role": "validation", "expect_failure": False})
    tests = run_problem_test_commands(cwd, lab_dir, command_specs)
    evaluations = deterministic_expert_evaluations(experts, context, tests)
    gate = problem_gate(evaluations, tests, max(0.0, min(1.0, float(args.promote_threshold))))
    gate_path = lab_dir / "gate" / "promotion-gate.json"
    write_json(gate_path, gate)
    adjustment_path = lab_dir / "adjustments" / "adjustment-plan.md"
    write_lines(adjustment_path, adjustment_plan_lines(case_id, args.problem, gate))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "case_id": case_id,
        "project_root": psafe(cwd),
        "problem": args.problem,
        "lab_directory": psafe(lab_dir),
        "context_path": psafe(context_path),
        "expert_panel_path": psafe(lab_dir / "experts" / "expert-panel.json"),
        "expert_prompt_paths": prompt_paths,
        "adjustment_plan_path": psafe(adjustment_path),
        "gate_path": psafe(gate_path),
        "experts": experts,
        "evaluations": evaluations,
        "tests": tests,
        "gate": gate,
        "isolation": {
            "mode": "scratch-lab",
            "core_files_mutated": False,
            "promotion_required_before_core_change": True,
        },
    }
    write_json(lab_dir / "analysis" / "problem-loop-report.json", payload)
    write_lines(lab_dir / "analysis" / "problem-loop-report.md", problem_loop_markdown(payload))
    write_json(problem_case_path(cwd, case_id), payload)
    append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "problem_loop_case", "case_id": case_id, "path": psafe(problem_case_path(cwd, case_id)), "lab_directory": psafe(lab_dir)})
    if args.write:
        suffix = "json" if args.format == "json" else "md"
        report_path = problem_reports_root(cwd) / f"{timestamp()}-{case_id}.{suffix}"
        payload["report_path"] = psafe(report_path)
        if args.format == "json":
            write_json(report_path, payload)
        else:
            write_lines(report_path, problem_loop_markdown(payload))
        append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "problem_loop_report", "case_id": case_id, "path": psafe(report_path)})
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    elif args.write:
        print(f"Problem loop report: {report_path}")
    else:
        print("\n".join(problem_loop_markdown(payload)).rstrip() + "\n")
    return 0


def load_problem_case(cwd: Path, case_id: str) -> dict[str, Any]:
    path = problem_case_path(cwd, case_id)
    payload = read_json(path, None)
    if not isinstance(payload, dict):
        raise ValueError(f"Problem case not found: {case_id}")
    return payload


def command_problem_promote(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    payload = load_problem_case(cwd, args.case_id)
    gate = payload.get("gate") or {}
    if not gate.get("promotion_allowed") and not args.force:
        print(f"Problem case is not approved for promotion: {args.case_id}", file=sys.stderr)
        print(f"Gate status: {gate.get('status')} score={gate.get('score')} threshold={gate.get('threshold')}", file=sys.stderr)
        return 1
    if args.force and not (args.note or "").strip():
        print("--force requires --note with the human approval or emergency rationale.", file=sys.stderr)
        return 1
    promotion = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "case_id": args.case_id,
        "project_root": psafe(cwd),
        "forced": bool(args.force),
        "gate": gate,
        "lab_directory": payload.get("lab_directory"),
        "adjustment_plan_path": payload.get("adjustment_plan_path"),
        "decision": "Promote isolated problem-loop adjustment plan into the main research loop for core implementation.",
        "note": args.note,
    }
    promotion_path = promotions_root(cwd) / f"{timestamp()}-{args.case_id}.json"
    promotion["path"] = psafe(promotion_path)
    write_json(promotion_path, promotion)
    append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "problem_promotion", **promotion, "path": psafe(promotion_path)})
    update_list_item(
        passport["next_actions"],
        {
            "id": record_id("next", f"Implement promoted problem case {args.case_id}"),
            "text": f"Implement promoted problem-loop plan for case {args.case_id}; apply only changes traceable to {payload.get('adjustment_plan_path')}.",
            "stage": state.get("current_stage", "INTAKE"),
            "status": "todo",
            "owner": "agent",
            "created_at": utc_now(),
        },
    )
    save_passport(cwd, passport)
    append_jsonl(artifacts_path(cwd), {"timestamp": utc_now(), "type": "problem_promotion", "case_id": args.case_id, "path": psafe(promotion_path)})
    if args.format == "json":
        print(json.dumps(promotion, indent=2, ensure_ascii=True, default=str))
    else:
        lines = [
            "# Problem Promotion",
            "",
            f"- Case id: `{args.case_id}`",
            f"- Forced: {bool(args.force)}",
            f"- Gate status: {gate.get('status')}",
            f"- Promotion record: `{promotion_path}`",
            f"- Adjustment plan: `{payload.get('adjustment_plan_path')}`",
        ]
        print("\n".join(lines).rstrip() + "\n")
    return 0


def normalize_doi(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^doi:\s*", "", text, flags=re.IGNORECASE)
    match = DOI_RE.search(text)
    return match.group(0).rstrip(".,;").lower() if match else None


def title_key(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value).strip().lower())
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    text = re.sub(r"\b(the|a|an|and|of|for|to|in|on|with)\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:160] or None


def list_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def year_value(value: Any) -> int | None:
    if value is None:
        return None
    try:
        year = int(str(value)[:4])
    except Exception:
        return None
    if 1000 <= year <= 3000:
        return year
    return None


def material_to_zotero_candidate(cwd: Path, material: dict[str, Any]) -> dict[str, Any] | None:
    metadata = material.get("metadata") if isinstance(material.get("metadata"), dict) else {}
    source = material.get("source") or metadata.get("url") or metadata.get("id") or metadata.get("doi")
    title = material.get("title") or metadata.get("title")
    doi = normalize_doi(metadata.get("doi") or source)
    authors = list_text(metadata.get("authors") or material.get("authors"))
    year = year_value(metadata.get("year") or material.get("year"))
    venue = metadata.get("venue") or material.get("venue")
    url = metadata.get("url") or material.get("url")
    if not url and doi:
        url = f"https://doi.org/{doi}"
    if not url and source and not doi:
        url = str(source)
    kind = str(material.get("kind") or "").lower()
    has_bibliographic_signal = bool(title or doi or authors or venue or url)
    if kind not in {"source-metadata", "paper", "article", "reference", "citation", "literature", "pdf", "paper-pdf", "article-pdf"} and not has_bibliographic_signal:
        return None
    if not (title or doi or url):
        return None
    identity = doi or url or title or material.get("id") or source
    item_type = "article-journal"
    source_type = str(metadata.get("type") or material.get("type") or "").lower()
    if "preprint" in source_type or str(venue or "").lower() == "arxiv":
        item_type = "article"
    if "book" in source_type:
        item_type = "book"
    local_path = None
    if material.get("path"):
        path = Path(str(material["path"])).expanduser()
        if not path.is_absolute():
            path = cwd / path
        local_path = path.resolve()
    pdf_url = metadata.get("pdf_url")
    if not pdf_url and str(venue or "").lower() == "arxiv" and url:
        pdf_url = str(url).replace("/abs/", "/pdf/") if "/abs/" in str(url) else None
    return {
        "id": f"zot-{short_digest(str(identity).lower())}",
        "source_material_id": material.get("id"),
        "source_material_kind": material.get("kind"),
        "title": str(title).strip() if title else None,
        "authors": authors,
        "year": year,
        "venue": str(venue).strip() if venue else None,
        "doi": doi,
        "url": str(url).strip() if url else None,
        "abstract": metadata.get("summary") or metadata.get("abstract"),
        "provider": metadata.get("provider"),
        "item_type": item_type,
        "source": source,
        "local_path": psafe(local_path) if local_path else None,
        "local_path_exists": bool(local_path and local_path.exists()),
        "pdf_url": pdf_url,
        "raw_metadata": metadata,
    }


def zotero_candidates_from_passport(cwd: Path, passport: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen_materials: set[str] = set()
    for material in passport.get("materials") or []:
        if not isinstance(material, dict):
            continue
        item = material_to_zotero_candidate(cwd, material)
        if not item:
            continue
        source_id = str(item.get("source_material_id") or item.get("id"))
        if source_id in seen_materials:
            continue
        seen_materials.add(source_id)
        candidates.append(item)
    return candidates


def dedupe_key(item: dict[str, Any]) -> str:
    doi = normalize_doi(item.get("doi"))
    if doi:
        return f"doi:{doi}"
    key = title_key(item.get("title"))
    if key:
        return f"title:{key}"
    return f"id:{item.get('id')}"


def dedupe_zotero_candidates(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(dedupe_key(item), []).append(item)
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    for key, group in groups.items():
        group.sort(key=lambda row: (0 if row.get("doi") else 1, 0 if row.get("local_path_exists") else 1, str(row.get("title") or "")))
        canonical = dict(group[0])
        canonical["dedupe_key"] = key
        canonical["duplicate_source_material_ids"] = [row.get("source_material_id") for row in group[1:]]
        unique.append(canonical)
        if len(group) > 1:
            duplicates.append(
                {
                    "key": key,
                    "canonical_id": canonical.get("id"),
                    "canonical_title": canonical.get("title"),
                    "duplicate_count": len(group) - 1,
                    "members": [
                        {
                            "id": row.get("id"),
                            "source_material_id": row.get("source_material_id"),
                            "title": row.get("title"),
                            "doi": row.get("doi"),
                            "url": row.get("url"),
                            "provider": row.get("provider"),
                        }
                        for row in group
                    ],
                }
            )
    unique.sort(key=lambda row: (str(row.get("year") or ""), str(row.get("title") or "")))
    return unique, duplicates


def csl_author(name: str) -> dict[str, str]:
    text = " ".join(str(name).split())
    if "," in text:
        family, given = [part.strip() for part in text.split(",", 1)]
        return remove_none_values({"family": family or None, "given": given or None})
    parts = text.split()
    if len(parts) <= 1:
        return {"family": text}
    return {"given": " ".join(parts[:-1]), "family": parts[-1]}


def citation_key(item: dict[str, Any]) -> str:
    author = "source"
    authors = item.get("authors") or []
    if authors:
        first = str(authors[0])
        if "," in first:
            author = first.split(",", 1)[0]
        else:
            author = first.split()[-1]
    year = str(item.get("year") or "nd")
    base = slug(f"{author}-{year}-{item.get('title') or item.get('doi') or item.get('id')}", "source")
    return f"{base[:48]}-{short_digest(dedupe_key(item))[:6]}"


def zotero_csl_json(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        csl = {
            "id": citation_key(item),
            "type": item.get("item_type") or "article-journal",
            "title": item.get("title"),
            "author": [csl_author(name) for name in item.get("authors") or []],
            "container-title": item.get("venue"),
            "DOI": item.get("doi"),
            "URL": item.get("url"),
            "abstract": item.get("abstract"),
        }
        if item.get("year"):
            csl["issued"] = {"date-parts": [[item["year"]]]}
        rows.append(remove_none_values(csl))
    return rows


def bibtex_escape(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text.replace("{", "").replace("}", "")


def zotero_bibtex(items: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for item in items:
        entry_type = "article" if item.get("item_type") != "book" else "book"
        fields = {
            "title": item.get("title"),
            "author": " and ".join(item.get("authors") or []),
            "year": item.get("year"),
            "journal": item.get("venue") if entry_type == "article" else None,
            "doi": item.get("doi"),
            "url": item.get("url"),
        }
        lines = [f"@{entry_type}{{{citation_key(item)},"]
        for key, value in fields.items():
            if value is None or value == "":
                continue
            lines.append(f"  {key} = {{{bibtex_escape(value)}}},")
        if len(lines) > 1:
            lines[-1] = lines[-1].rstrip(",")
        lines.append("}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks).rstrip() + ("\n" if blocks else "")


def zotero_attachment_plan(items: list[dict[str, Any]], include_attachments: bool) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    if not include_attachments:
        return plan
    for item in items:
        local_path = item.get("local_path")
        local_is_pdf = bool(local_path and str(local_path).lower().endswith(".pdf"))
        status = "missing"
        action = "manual-locate-pdf"
        if local_path and item.get("local_path_exists") and local_is_pdf:
            status = "ready"
            action = "attach-local-pdf"
        elif item.get("pdf_url"):
            status = "remote-candidate"
            action = "download-or-link-pdf"
        plan.append(
            {
                "item_id": item.get("id"),
                "title": item.get("title"),
                "status": status,
                "action": action,
                "local_path": local_path,
                "pdf_url": item.get("pdf_url"),
                "source_material_id": item.get("source_material_id"),
            }
        )
    return plan


def zotero_collection_plan(collection: str, items: list[dict[str, Any]], attachment_plan: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "collection_name": collection,
        "mode": "offline-export-plan",
        "direct_zotero_write": False,
        "direct_write_reason": "No Zotero API key, user library id, and attachment upload handshake are assumed by the local loop.",
        "items": [
            {
                "id": item.get("id"),
                "citation_key": citation_key(item),
                "title": item.get("title"),
                "authors": item.get("authors"),
                "year": item.get("year"),
                "venue": item.get("venue"),
                "doi": item.get("doi"),
                "url": item.get("url"),
                "source_material_id": item.get("source_material_id"),
                "dedupe_key": item.get("dedupe_key"),
            }
            for item in items
        ],
        "attachments": attachment_plan,
    }


def zotero_bridge_payload(cwd: Path, passport: dict[str, Any], collection: str, include_attachments: bool, dedupe: bool, wiki_root: str | None) -> dict[str, Any]:
    candidates = zotero_candidates_from_passport(cwd, passport)
    items, duplicates = dedupe_zotero_candidates(candidates) if dedupe else (candidates, [])
    attachment_plan = zotero_attachment_plan(items, include_attachments)
    csl = zotero_csl_json(items)
    bibtex_text = zotero_bibtex(items)
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "collection": collection,
        "source_material_count": len(candidates),
        "item_count": len(items),
        "dedupe_enabled": dedupe,
        "duplicate_groups": duplicates,
        "items": items,
        "collection_plan": zotero_collection_plan(collection, items, attachment_plan),
        "exports": {
            "csl_json": csl,
            "bibtex": bibtex_text,
        },
        "attachment_plan": attachment_plan,
        "wiki_plan": {
            "enabled": bool(wiki_root),
            "wiki_root": wiki_root,
            "page_count": len(items) + (1 if wiki_root else 0),
            "mode": "llm-wiki-compatible-markdown",
        },
        "zotero_api_notes": [
            "Read access can use Zotero Web API or the local API; direct write requests require write-capable credentials.",
            "File attachments require creating a child attachment item and then performing the Zotero file upload process.",
            "This bridge writes deterministic export artifacts first; API ingestion can be added after credentials and library id are configured.",
        ],
    }


def zotero_bridge_markdown(payload: dict[str, Any], written_paths: dict[str, str] | None = None) -> list[str]:
    lines = [
        "# Zotero Bridge Plan",
        "",
        f"- Created at UTC: {payload['timestamp']}",
        f"- Collection: {payload['collection']}",
        f"- Source materials: {payload['source_material_count']}",
        f"- Exported unique items: {payload['item_count']}",
        f"- Duplicate groups: {len(payload['duplicate_groups'])}",
        f"- Attachment candidates: {len(payload['attachment_plan'])}",
        "",
        "## Items",
        "",
    ]
    for item in payload["collection_plan"]["items"][:80]:
        authors = ", ".join((item.get("authors") or [])[:3])
        if item.get("authors") and len(item.get("authors") or []) > 3:
            authors += ", et al."
        lines.append(f"- `{item.get('citation_key')}` {item.get('title') or '(untitled)'}")
        lines.append(f"  - Authors: {authors or '(not provided)'}")
        lines.append(f"  - Year: {item.get('year') or '(not provided)'}; DOI: {item.get('doi') or '(not provided)'}")
    if payload["duplicate_groups"]:
        lines.extend(["", "## Dedupe Groups", ""])
        for group in payload["duplicate_groups"]:
            lines.append(f"- `{group['key']}` duplicates={group['duplicate_count']} canonical={group['canonical_title']}")
    ready = [item for item in payload["attachment_plan"] if item.get("status") == "ready"]
    remote = [item for item in payload["attachment_plan"] if item.get("status") == "remote-candidate"]
    missing = [item for item in payload["attachment_plan"] if item.get("status") == "missing"]
    lines.extend(
        [
            "",
            "## Attachments",
            "",
            f"- Ready local PDFs: {len(ready)}",
            f"- Remote PDF candidates: {len(remote)}",
            f"- Missing PDFs: {len(missing)}",
            "",
            "## Zotero Write Boundary",
            "",
            "- This command does not write directly to Zotero SQLite or a Zotero library.",
            "- Use the generated BibTeX/CSL-JSON and collection plan for import, or add API credentials later for direct write mode.",
        ]
    )
    if written_paths:
        lines.extend(["", "## Written Files", ""])
        for key, path in written_paths.items():
            lines.append(f"- {key}: `{path}`")
    return lines


def write_zotero_exports(cwd: Path, payload: dict[str, Any], export_format: str) -> dict[str, str]:
    root = loop_root(cwd) / "zotero"
    ensure_dir(root)
    base = f"{timestamp()}-{short_digest(str(time.time_ns()))}-{slug(payload['collection'], 'zotero')}"
    paths: dict[str, str] = {}
    plan_path = root / f"{base}-collection-plan.json"
    dedupe_path = root / f"{base}-dedupe.json"
    attachments_path = root / f"{base}-attachments.json"
    write_json(plan_path, payload["collection_plan"])
    write_json(dedupe_path, {"duplicate_groups": payload["duplicate_groups"], "dedupe_enabled": payload["dedupe_enabled"]})
    write_json(attachments_path, payload["attachment_plan"])
    paths["collection_plan"] = psafe(plan_path)
    paths["dedupe"] = psafe(dedupe_path)
    paths["attachments"] = psafe(attachments_path)
    if export_format in {"csl-json", "all"}:
        csl_path = root / f"{base}-items.csl.json"
        write_json(csl_path, payload["exports"]["csl_json"])
        paths["csl_json"] = psafe(csl_path)
    if export_format in {"bibtex", "all"}:
        bib_path = root / f"{base}-items.bib"
        write_lines(bib_path, payload["exports"]["bibtex"].splitlines())
        paths["bibtex"] = psafe(bib_path)
    report_path = reports_root(cwd) / f"{base}-zotero-bridge.md"
    write_lines(report_path, zotero_bridge_markdown(payload, paths))
    paths["report"] = psafe(report_path)
    return paths


def wiki_page_name(item: dict[str, Any]) -> str:
    return f"paper-{slug(citation_key(item), 'paper')}.md"


def wiki_paper_page(collection: str, item: dict[str, Any]) -> list[str]:
    authors = ", ".join(item.get("authors") or [])
    lines = [
        f"# {item.get('title') or citation_key(item)}",
        "",
        "- Type: paper",
        f"- Collection: [[{collection}]]",
        "- Library hub: [[Zotero Paper Library]]",
        f"- Citation key: {citation_key(item)}",
        f"- Year: {item.get('year') or ''}",
        f"- Authors: {authors}",
        f"- Venue: {item.get('venue') or ''}",
        f"- DOI: {item.get('doi') or ''}",
        f"- URL: {item.get('url') or ''}",
        f"- Source material: {item.get('source_material_id') or ''}",
        "",
        "## Summary",
        "",
        item.get("abstract") or "(No abstract recorded.)",
        "",
        "## Links",
        "",
        "- [[Zotero Paper Library]]",
        f"- [[{collection}]]",
    ]
    return lines


def write_zotero_wiki_pages(wiki_root: str, collection: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    root = Path(wiki_root).expanduser().resolve()
    sources = root / "sources"
    topics = root / "topics"
    ensure_dir(sources)
    ensure_dir(topics)
    written: list[str] = []
    paper_links: list[str] = []
    for item in items:
        page = sources / wiki_page_name(item)
        write_lines(page, wiki_paper_page(collection, item))
        written.append(psafe(page))
        paper_links.append(f"[[{page.stem}]]")
    hub = topics / "zotero-paper-library.md"
    hub_lines = [
        "# Zotero Paper Library",
        "",
        f"- Collection: [[{collection}]]",
        f"- Generated at UTC: {utc_now()}",
        f"- Paper count: {len(items)}",
        "",
        "## Papers",
        "",
    ]
    hub_lines.extend(f"- {link}" for link in paper_links)
    write_lines(hub, hub_lines)
    written.append(psafe(hub))
    return {"wiki_root": psafe(root), "written_pages": written, "hub": psafe(hub)}


def command_zotero_bridge(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    payload = zotero_bridge_payload(cwd, passport, args.collection, args.include_attachments, not args.no_dedupe, args.wiki_root)
    written_paths: dict[str, str] = {}
    if args.write:
        written_paths.update(write_zotero_exports(cwd, payload, args.format))
        append_jsonl(
            artifacts_path(cwd),
            {
                "timestamp": utc_now(),
                "type": "zotero_bridge",
                "collection": args.collection,
                "item_count": payload["item_count"],
                "paths": written_paths,
            },
        )
    if args.write_wiki:
        if not args.wiki_root:
            raise ValueError("--write-wiki requires --wiki-root")
        wiki_result = write_zotero_wiki_pages(args.wiki_root, args.collection, payload["items"])
        payload["wiki_result"] = wiki_result
        written_paths["wiki_hub"] = wiki_result["hub"]
        append_jsonl(
            artifacts_path(cwd),
            {
                "timestamp": utc_now(),
                "type": "zotero_wiki_pages",
                "collection": args.collection,
                "item_count": payload["item_count"],
                "wiki_root": wiki_result["wiki_root"],
                "hub": wiki_result["hub"],
            },
        )
    if written_paths:
        payload["written_paths"] = written_paths
    if args.write:
        print(f"Zotero bridge report: {written_paths.get('report')}")
        if args.write_wiki:
            print(f"Wiki hub: {written_paths.get('wiki_hub')}")
        return 0
    if args.format == "csl-json":
        print(json.dumps(payload["exports"]["csl_json"], indent=2, ensure_ascii=True, default=str))
    elif args.format == "bibtex":
        print(payload["exports"]["bibtex"])
    elif args.format == "plan":
        print("\n".join(zotero_bridge_markdown(payload, written_paths)).rstrip() + "\n")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    return 0


def command_excerpt(text: str, limit: int = 1800) -> str:
    value = text or ""
    if len(value) <= limit:
        return value
    return value[:limit] + "\n... truncated ..."


def create_windows_kill_job() -> Any | None:
    if os.name != "nt":
        return None

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = ctypes.c_void_p
    job_handle = kernel32.CreateJobObjectW(None, None)
    if not job_handle:
        return None
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(
        ctypes.c_void_p(job_handle),
        9,  # JobObjectExtendedLimitInformation
        ctypes.byref(info),
        ctypes.sizeof(info),
    )
    if not ok:
        kernel32.CloseHandle(ctypes.c_void_p(job_handle))
        return None
    return job_handle


def assign_windows_job(job_handle: Any | None, proc: subprocess.Popen[Any]) -> bool:
    if os.name != "nt" or not job_handle:
        return False
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    return bool(kernel32.AssignProcessToJobObject(ctypes.c_void_p(job_handle), ctypes.c_void_p(proc._handle)))


def terminate_windows_job(job_handle: Any | None) -> None:
    if os.name != "nt" or not job_handle:
        return
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    try:
        kernel32.TerminateJobObject(ctypes.c_void_p(job_handle), 1)
    except Exception:
        pass


def close_windows_handle(handle: Any | None) -> None:
    if os.name != "nt" or not handle:
        return
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    try:
        kernel32.CloseHandle(ctypes.c_void_p(handle))
    except Exception:
        pass


def taskkill_windows_tree(pid: int) -> None:
    if os.name != "nt" or not pid:
        return
    try:
        proc = subprocess.Popen(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1)
    except Exception:
        pass


def kill_process_tree(proc: subprocess.Popen[Any], job_handle: Any | None = None) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        try:
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
        except Exception:
            pass
        if proc.poll() is None:
            taskkill_windows_tree(proc.pid)
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
        if job_handle:
            terminate_windows_job(job_handle)
            time.sleep(0.3)
            if proc.poll() is not None:
                return
        try:
            proc.kill()
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
        except Exception:
            pass
        if proc.poll() is None:
            taskkill_windows_tree(proc.pid)
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        proc.kill()


def monitored_popen_kwargs() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def command_to_text(command: str | list[str]) -> str:
    if isinstance(command, str):
        return command
    return " ".join(str(part) for part in command)


def run_monitored_process(
    cwd: Path,
    output_dir: Path,
    kind: str,
    command: str | list[str],
    index: int,
    *,
    shell: bool = True,
    idle_timeout_seconds: float = 0.0,
    wall_timeout_seconds: float = 0.0,
    poll_interval_seconds: float = 0.25,
) -> dict[str, Any]:
    ensure_dir(output_dir)
    command_text = command_to_text(command)
    name = f"{kind}-{index:02d}-{short_digest(command_text)}"
    stdout_path = output_dir / f"{name}-stdout.log"
    stderr_path = output_dir / f"{name}-stderr.log"
    started = time.monotonic()
    last_activity = started
    timed_out = False
    timeout_reason: str | None = None
    poll_seconds = max(float(poll_interval_seconds or 0.25), 0.05)
    popen_command: str | list[str]
    if shell:
        popen_command = command_text
    elif isinstance(command, list):
        popen_command = [str(part) for part in command]
    else:
        popen_command = command.split()
    stdout_size = 0
    stderr_size = 0
    job_handle: Any | None = None
    with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8", errors="replace"
    ) as stderr_handle:
        proc = subprocess.Popen(
            popen_command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=shell,
            stdout=stdout_handle,
            stderr=stderr_handle,
            **monitored_popen_kwargs(),
        )
        job_handle = create_windows_kill_job()
        if job_handle and not assign_windows_job(job_handle, proc):
            close_windows_handle(job_handle)
            job_handle = None
        try:
            while proc.poll() is None:
                now = time.monotonic()
                stdout_handle.flush()
                stderr_handle.flush()
                current_stdout_size = stdout_path.stat().st_size if stdout_path.exists() else 0
                current_stderr_size = stderr_path.stat().st_size if stderr_path.exists() else 0
                if current_stdout_size != stdout_size or current_stderr_size != stderr_size:
                    stdout_size = current_stdout_size
                    stderr_size = current_stderr_size
                    last_activity = now
                if wall_timeout_seconds and now - started >= float(wall_timeout_seconds):
                    timed_out = True
                    timeout_reason = "wall"
                    kill_process_tree(proc, job_handle)
                    break
                if idle_timeout_seconds and now - last_activity >= float(idle_timeout_seconds):
                    timed_out = True
                    timeout_reason = "idle"
                    kill_process_tree(proc, job_handle)
                    break
                time.sleep(poll_seconds)
            try:
                proc.wait(timeout=1 if timed_out else 5)
            except subprocess.TimeoutExpired:
                kill_process_tree(proc, job_handle)
                proc.wait(timeout=1)
        finally:
            close_windows_handle(job_handle)
    elapsed = time.monotonic() - started
    stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
    stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    exit_code = proc.returncode if proc.returncode is not None else TIMEOUT_EXIT_CODE
    if timed_out and exit_code == 0:
        exit_code = TIMEOUT_EXIT_CODE
    signature_text = f"{command_text}\n{exit_code}\n{command_excerpt(stdout_text, 1200)}\n{command_excerpt(stderr_text, 1200)}"
    return {
        "kind": kind,
        "command": command_text,
        "exit_code": exit_code,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_log": psafe(stdout_path),
        "stderr_log": psafe(stderr_path),
        "stdout_excerpt": command_excerpt(stdout_text, 1200),
        "stderr_excerpt": command_excerpt(stderr_text, 1200),
        "timed_out": timed_out,
        "timeout_reason": timeout_reason,
        "idle_timeout_seconds": float(idle_timeout_seconds or 0.0) or None,
        "wall_timeout_seconds": float(wall_timeout_seconds or 0.0) or None,
        "last_activity_seconds": round(time.monotonic() - last_activity, 3),
        "signature": short_digest(signature_text),
    }


def run_auto_command(
    cwd: Path,
    round_dir: Path,
    kind: str,
    command: str,
    index: int,
    shell: bool = True,
    idle_timeout_seconds: float = 0.0,
    wall_timeout_seconds: float = 0.0,
    poll_interval_seconds: float = 0.25,
) -> dict[str, Any]:
    return run_monitored_process(
        cwd,
        round_dir,
        kind,
        command,
        index,
        shell=shell,
        idle_timeout_seconds=idle_timeout_seconds,
        wall_timeout_seconds=wall_timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )


def run_auto_validate(cwd: Path, round_dir: Path, index: int) -> dict[str, Any]:
    command = f"{sys.executable} {Path(__file__).resolve()} --cwd {cwd} validate --fail-on-issue"
    started = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--cwd", str(cwd), "validate", "--fail-on-issue"],
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    stdout_path = round_dir / f"test-{index:02d}-validate-stdout.log"
    stderr_path = round_dir / f"test-{index:02d}-validate-stderr.log"
    stdout_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr_path.write_text(proc.stderr or "", encoding="utf-8")
    signature_text = f"{command}\n{proc.returncode}\n{command_excerpt(proc.stdout or '', 1200)}\n{command_excerpt(proc.stderr or '', 1200)}"
    return {
        "kind": "test",
        "command": command,
        "exit_code": proc.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_log": psafe(stdout_path),
        "stderr_log": psafe(stderr_path),
        "stdout_excerpt": command_excerpt(proc.stdout or "", 1200),
        "stderr_excerpt": command_excerpt(proc.stderr or "", 1200),
        "signature": short_digest(signature_text),
    }


def auto_loop_artifact_refs(round_dir: Path, results: list[dict[str, Any]], extra_paths: list[str] | None = None) -> list[str]:
    refs = [psafe(round_dir)]
    for result in results:
        for key in ["stdout_log", "stderr_log"]:
            value = result.get(key)
            if value:
                append_unique(refs, str(value))
    for path in extra_paths or []:
        if path:
            append_unique(refs, str(path))
    return refs


def auto_loop_deep_loop_payload(
    args: argparse.Namespace,
    cwd: Path,
    state: dict[str, Any],
    passport: dict[str, Any],
    *,
    auto_dir: Path,
    round_index: int,
    round_dir: Path,
    gate_result: str,
    result_summary: str,
    gate_issues: list[str] | None = None,
    test_results: list[dict[str, Any]] | None = None,
    extra_paths: list[str] | None = None,
) -> dict[str, Any]:
    quality_score = args.deep_loop_quality_score
    if gate_result == "pass" and quality_score is None:
        quality_score = 1.0
    deep_args = argparse.Namespace(
        stage=None,
        intent=args.deep_loop_intent or args.goal,
        loop_id=f"auto-{auto_dir.name}-round-{round_index:02d}",
        current_subchain=args.current_subchain,
        next_subchain=list(args.next_subchain or []),
        gate_result=gate_result,
        quality_score=quality_score,
        pass_threshold=args.deep_loop_pass_threshold,
        gate_issue=list(gate_issues or []),
        result_summary=result_summary,
        artifact=auto_loop_artifact_refs(round_dir, list(test_results or []), extra_paths),
        harness_report=list(getattr(args, "harness_report", None) or []),
        round_index=round_index,
        max_rounds=args.deep_loop_max_rounds or (None if args.allow_unbounded else args.max_rounds),
    )
    payload = build_deep_loop_payload(deep_args, cwd, state, passport)
    payload["auto_loop_context"] = {
        "goal": args.goal,
        "run_directory": psafe(auto_dir),
        "round_directory": psafe(round_dir),
        "round": round_index,
        "gate_result_source": gate_result,
        "harness_reports": list(getattr(args, "harness_report", None) or []),
    }
    return persist_deep_loop_payload(cwd, state, passport, payload, source="auto-loop")


def auto_loop_problem_escalation(
    args: argparse.Namespace,
    cwd: Path,
    round_dir: Path,
    deep_payload: dict[str, Any],
    tests: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    problem = auto_loop_problem_statement(args.goal, deep_payload, failures)
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--cwd",
        str(cwd),
        "problem-loop",
        "--problem",
        problem,
        "--format",
        "json",
        "--write",
        "--promote-threshold",
        str(args.problem_promote_threshold),
    ]
    repro_commands = [str(item.get("command")) for item in failures if item.get("command")]
    for command_text in repro_commands:
        command.extend(["--repro-command", command_text])
    validation_commands: list[str] = []
    if not args.skip_validate:
        validation_commands.append(f"{sys.executable} {Path(__file__).resolve()} --cwd {cwd} validate --fail-on-issue")
    validation_commands.extend(str(command_text) for command_text in args.test_command or [])
    for command_text in validation_commands:
        command.extend(["--test-command", command_text])
    started = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    stdout_path = round_dir / "problem-loop-stdout.log"
    stderr_path = round_dir / "problem-loop-stderr.log"
    stdout_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr_path.write_text(proc.stderr or "", encoding="utf-8")
    parsed: dict[str, Any] | None = None
    try:
        value = json.loads(proc.stdout or "{}")
        if isinstance(value, dict):
            parsed = value
    except Exception:
        parsed = None
    return {
        "decision": (deep_payload.get("gate") or {}).get("decision"),
        "exit_code": proc.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_log": psafe(stdout_path),
        "stderr_log": psafe(stderr_path),
        "stdout_excerpt": command_excerpt(proc.stdout or "", 1200),
        "stderr_excerpt": command_excerpt(proc.stderr or "", 1200),
        "case_id": parsed.get("case_id") if parsed else None,
        "lab_directory": parsed.get("lab_directory") if parsed else None,
        "report_path": parsed.get("report_path") if parsed else None,
        "gate_status": (parsed.get("gate") or {}).get("status") if parsed else None,
    }


def auto_loop_problem_statement(goal: str, deep_payload: dict[str, Any], failures: list[dict[str, Any]]) -> str:
    gate = deep_payload.get("gate") or {}
    handoff = deep_payload.get("handoff_package") or {}
    continuation = deep_payload.get("continuation_contract") or {}
    gate_vector = deep_payload.get("gate_vector") or {}
    issue_lines = [str(item) for item in gate.get("reasons") or []]
    for failure in failures:
        issue_lines.append(
            f"Failed gate: {failure.get('command')} exit={failure.get('exit_code')} signature={failure.get('signature')}"
        )
        if failure.get("stderr_excerpt"):
            issue_lines.append(f"stderr excerpt: {command_excerpt(str(failure.get('stderr_excerpt')), 900)}")
    vector_summary = continuation.get("gate_vector_summary") or {
        key: value.get("level")
        for key, value in gate_vector.items()
        if isinstance(value, dict)
    }
    blocking_dimensions = list(continuation.get("blocking_dimensions") or [])
    next_agent = continuation.get("next_agent") or {}
    harness = continuation.get("harness_protocol") if isinstance(continuation.get("harness_protocol"), dict) else {}
    harness_feedback = harness.get("feedback_summary") if isinstance(harness.get("feedback_summary"), dict) else {}
    harness_evidence = deep_payload.get("harness_evidence") if isinstance(deep_payload.get("harness_evidence"), dict) else {}
    return "\n\n".join(
        [
            f"Auto-loop escalated by deep-loop for goal: {goal}",
            f"Deep-loop decision: {gate.get('decision')}",
            f"Review mode: {(deep_payload.get('review_directive') or {}).get('mode')}",
            "Issues:\n" + "\n".join(f"- {item}" for item in issue_lines) if issue_lines else "Issues: none recorded.",
            "Gate vector summary:\n" + "\n".join(f"- {key}: {value}" for key, value in vector_summary.items()),
            "Gate vector blocking dimensions:\n" + ("\n".join(f"- {item}" for item in blocking_dimensions) if blocking_dimensions else "- none"),
            "Continuation contract:\n" + json.dumps(
                {
                    "decision": continuation.get("decision"),
                    "from_agent": continuation.get("from_agent"),
                    "target_subchains": continuation.get("target_subchains") or [],
                    "next_agent": next_agent.get("agent_id"),
                    "requires_human": continuation.get("requires_human"),
                    "unattended_safe": continuation.get("unattended_safe"),
                },
                indent=2,
                ensure_ascii=True,
            ),
            "Harness evidence:\n" + json.dumps(
                {
                    "gate_result": harness_evidence.get("gate_result"),
                    "pass_rate": harness_evidence.get("pass_rate"),
                    "quality_score": harness_evidence.get("quality_score"),
                    "failures_by_tag": harness_evidence.get("failures_by_tag") or {},
                    "reports": harness_evidence.get("reports") or [],
                    "errors": harness_evidence.get("errors") or [],
                },
                indent=2,
                ensure_ascii=True,
            ),
            "Harness protocol:\n" + json.dumps(
                {
                    "execution_profile": harness.get("execution_profile"),
                    "validation_surfaces": harness.get("validation_surfaces") or [],
                    "feedback_metrics": harness_feedback.get("preferred_metrics") or [],
                    "routing_use": harness_feedback.get("routing_use"),
                },
                indent=2,
                ensure_ascii=True,
            ),
            f"Next work prompt:\n{handoff.get('next_work_prompt') or '(not generated)'}",
            f"Deep-loop report: {deep_payload.get('report_markdown') or deep_payload.get('report_json')}",
        ]
    )


def summarize_deep_loop_dispatch(deep_payload: dict[str, Any]) -> dict[str, Any]:
    gate = deep_payload.get("gate") or {}
    review = deep_payload.get("review_directive") or {}
    handoff = deep_payload.get("handoff_package") or {}
    agent = deep_payload.get("subchain_agent") or {}
    continuation = deep_payload.get("continuation_contract") or {}
    harness = continuation.get("harness_protocol") if isinstance(continuation.get("harness_protocol"), dict) else {}
    harness_evidence = deep_payload.get("harness_evidence") if isinstance(deep_payload.get("harness_evidence"), dict) else {}
    return {
        "decision": gate.get("decision"),
        "review_mode": review.get("mode"),
        "subchain_agent": agent.get("agent_id"),
        "target_subchains": handoff.get("target_subchains") or [],
        "next_work_prompt": command_excerpt(handoff.get("next_work_prompt") or "", 900),
        "gate_vector": continuation.get("gate_vector_summary") or {},
        "blocking_dimensions": continuation.get("blocking_dimensions") or [],
        "execution_profile": harness.get("execution_profile"),
        "harness_protocol": harness,
        "harness_evidence": harness_evidence,
        "continuation_contract": continuation,
        "report_json": deep_payload.get("report_json"),
        "report_markdown": deep_payload.get("report_markdown"),
    }


def auto_route_template_value(
    value: str,
    *,
    cwd: Path,
    subchain: str,
    goal: str,
    prompt: str,
    prompt_file: Path | None,
    round_index: int,
) -> str:
    return value.format(
        cwd=str(cwd),
        subchain=subchain,
        goal=goal,
        prompt=prompt,
        prompt_file=str(prompt_file) if prompt_file else "",
        round=round_index,
    )


def cmd_quote(value: str | Path) -> str:
    text = str(value)
    return '"' + text.replace('"', r'\"') + '"'


def discover_codex_cli() -> Path | None:
    override = os.environ.get("RESEARCH_LOOP_CODEX_CLI") or os.environ.get("CODEX_CLI")
    if override:
        path = Path(override).expanduser()
        if path.exists():
            return path
    local_appdata = os.environ.get("LOCALAPPDATA")
    candidates: list[Path] = []
    if local_appdata:
        root = Path(local_appdata) / "OpenAI" / "Codex" / "bin"
        if root.exists():
            candidates.extend(path for path in root.glob("*/codex.exe") if path.exists())
    for name in ["codex.exe", "codex"]:
        found = shutil.which(name)
        if found:
            path = Path(found)
            if "WindowsApps" not in str(path):
                candidates.append(path)
    if not candidates:
        return None
    candidates = sorted(set(candidates), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    return candidates[0]


def build_codex_route_agent_command(args: argparse.Namespace, cwd: Path, prompt_file: Path) -> str:
    codex_path = Path(args.route_codex_path).expanduser() if args.route_codex_path else discover_codex_cli()
    if not codex_path or not codex_path.exists():
        raise ValueError("Codex CLI executable was not found. Set --route-codex-path or RESEARCH_LOOP_CODEX_CLI.")
    parts = [
        "type",
        cmd_quote(prompt_file),
        "|",
        cmd_quote(codex_path),
        "--ask-for-approval",
        str(args.route_codex_approval),
        "exec",
        "--cd",
        cmd_quote(cwd),
        "--sandbox",
        str(args.route_codex_sandbox),
    ]
    if args.route_codex_skip_git_check:
        parts.append("--skip-git-repo-check")
    if args.route_codex_ephemeral:
        parts.append("--ephemeral")
    if args.route_codex_json:
        parts.append("--json")
    if args.route_codex_output:
        parts.extend(["--output-last-message", cmd_quote(Path(args.route_codex_output))])
    parts.append("-")
    return " ".join(parts)


def auto_loop_route_agent_commands(args: argparse.Namespace, cwd: Path, prompt_file: Path) -> list[str]:
    commands = list(args.route_agent_command or [])
    if args.route_agent == "codex":
        commands.insert(0, build_codex_route_agent_command(args, cwd, prompt_file))
    return commands


def auto_loop_report_markdown(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# Research Auto Loop Report",
        "",
        f"- Created at UTC: {payload['timestamp']}",
        f"- Goal: {payload['goal']}",
        f"- Status: {payload['status']}",
        f"- Rounds: {payload['round_count']}",
        f"- Run directory: `{payload['run_directory']}`",
        "",
        "## Rounds",
        "",
    ]
    if payload.get("resume"):
        resume = payload["resume"]
        lines[7:7] = [
            f"- Resumed from: `{resume.get('source_report')}`",
            f"- Resume source status: `{resume.get('source_status')}`",
        ]
    for round_item in payload.get("rounds") or []:
        lines.append(f"- Round {round_item['round']}: {round_item['status']}")
        if round_item.get("subchain") or round_item.get("goal"):
            lines.append(f"  - subchain: `{round_item.get('subchain') or '(unset)'}`")
            lines.append(f"  - goal: {command_excerpt(str(round_item.get('goal') or ''), 220)}")
        for result in round_item.get("executors") or []:
            lines.append(f"  - executor `{result['command']}` exit={result['exit_code']} signature={result['signature']}")
        for result in round_item.get("tests") or []:
            lines.append(f"  - test `{result['command']}` exit={result['exit_code']} signature={result['signature']}")
        for result in round_item.get("repairs") or []:
            lines.append(f"  - repair `{result['command']}` exit={result['exit_code']} signature={result['signature']}")
        deep_loop = round_item.get("deep_loop") or {}
        if deep_loop:
            lines.append(
                f"  - deep-loop `{deep_loop.get('decision')}` review={deep_loop.get('review_mode')} targets={', '.join(deep_loop.get('target_subchains') or []) or '(none)'}"
            )
            if deep_loop.get("subchain_agent"):
                lines.append(f"  - subchain agent: `{deep_loop.get('subchain_agent')}`")
            if deep_loop.get("blocking_dimensions"):
                lines.append(f"  - blocking dimensions: {', '.join(deep_loop.get('blocking_dimensions') or [])}")
            if deep_loop.get("report_markdown"):
                lines.append(f"  - deep-loop report: `{deep_loop.get('report_markdown')}`")
        problem_loop = round_item.get("problem_loop") or {}
        if problem_loop:
            lines.append(
                f"  - problem-loop case={problem_loop.get('case_id') or '(unknown)'} gate={problem_loop.get('gate_status') or '(unknown)'} exit={problem_loop.get('exit_code')}"
            )
            if problem_loop.get("report_path"):
                lines.append(f"  - problem-loop report: `{problem_loop.get('report_path')}`")
        if round_item.get("next_prompt"):
            lines.append(f"  - next prompt: {round_item['next_prompt']}")
        if round_item.get("auto_route"):
            route = round_item["auto_route"]
            lines.append(
                f"  - auto-route: `{route.get('from_subchain') or '(unset)'}` -> `{route.get('to_subchain') or '(unset)'}` remaining_budget={route.get('remaining_budget')}"
            )
    if payload.get("routed_transitions"):
        lines.extend(["", "## Routed Transitions", ""])
        for item in payload.get("routed_transitions") or []:
            lines.append(
                f"- Round {item.get('round')}: `{item.get('from_subchain') or '(unset)'}` -> `{item.get('to_subchain') or '(unset)'}`"
            )
            if item.get("next_goal"):
                lines.append(f"  - next goal: {command_excerpt(str(item.get('next_goal')), 260)}")
    if payload.get("final_message"):
        lines.extend(["", "## Final Message", "", payload["final_message"]])
    return lines


def latest_auto_loop_report(cwd: Path) -> Path | None:
    files = sorted(
        reports_root(cwd).glob("*-auto-loop.json"),
        key=lambda path: path.stat().st_mtime if path.exists() else 0,
        reverse=True,
    )
    return files[0] if files else None


def auto_loop_resume_seed(payload: dict[str, Any]) -> dict[str, Any]:
    status = str(payload.get("status") or "")
    rounds = list(payload.get("rounds") or [])
    if not rounds:
        raise ValueError("auto-loop report has no rounds to resume from")
    if status == "passed":
        raise ValueError("auto-loop report is already passed and does not need resume")
    last_round = rounds[-1]
    last_route = last_round.get("auto_route") or {}
    deep_loop = last_round.get("deep_loop") or {}
    continuation = deep_loop.get("continuation_contract") or {}
    decision = str(deep_loop.get("decision") or last_route.get("decision") or "")
    target_subchains = list(continuation.get("target_subchains") or deep_loop.get("target_subchains") or [])
    source_subchain = last_round.get("subchain")

    if status in RESUMABLE_AUTO_LOOP_STATUSES and last_route:
        target = str(last_route.get("to_subchain") or source_subchain or "")
        prompt = str(last_route.get("next_goal") or last_round.get("goal") or payload.get("goal") or "")
        decision = str(last_route.get("decision") or decision or "route_next")
    elif decision in {"route_next", "retry_same_route", "escalate_problem_loop"}:
        if not target_subchains and decision == "retry_same_route":
            target_subchains = [str(source_subchain or "")]
        if not target_subchains and decision == "escalate_problem_loop":
            target_subchains = ["P10"]
        if not target_subchains:
            raise ValueError("auto-loop report does not contain a resumable target subchain")
        target = str(target_subchains[0])
        prompt = str(continuation.get("next_work_prompt") or deep_loop.get("next_work_prompt") or payload.get("goal") or "")
    elif status in {"route-next-handoff-required", "retry-same-route-handoff-required"} and deep_loop:
        if not target_subchains:
            raise ValueError("handoff-required report does not contain a target subchain")
        target = str(target_subchains[0])
        prompt = str(continuation.get("next_work_prompt") or deep_loop.get("next_work_prompt") or payload.get("goal") or "")
    else:
        raise ValueError(f"auto-loop status is not automatically resumable: {status}")

    if not target:
        raise ValueError("auto-loop resume target subchain is empty")
    if not prompt:
        prompt = str(payload.get("goal") or f"Resume subchain {target}")
    pending_route = {
        "round": last_round.get("round"),
        "decision": decision or "resume",
        "from_subchain": source_subchain,
        "to_subchain": target,
        "remaining_budget": None,
        "next_goal": prompt,
        "deep_loop_report": deep_loop.get("report_markdown") or deep_loop.get("report_json") or last_route.get("deep_loop_report"),
        "resume_source_status": status,
    }
    return {
        "source_status": status,
        "source_round": last_round.get("round"),
        "source_subchain": source_subchain,
        "decision": decision or "resume",
        "goal": prompt,
        "current_subchain": target,
        "next_subchains": [],
        "initial_agent_prompt": prompt,
        "initial_pending_route": pending_route,
    }


def command_auto_loop_resume(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    if args.latest:
        report_path = latest_auto_loop_report(cwd)
        if not report_path:
            raise ValueError("no auto-loop report found under .research-loop/reports")
    elif args.report:
        report_path = Path(args.report).expanduser()
        if not report_path.is_absolute():
            report_path = cwd / report_path
        if not report_path.exists():
            raise ValueError(f"auto-loop report not found: {report_path}")
    else:
        raise ValueError("auto-loop-resume requires --latest or --report")

    previous = read_json(report_path, {})
    if not isinstance(previous, dict):
        raise ValueError(f"auto-loop report is not a JSON object: {report_path}")
    seed = auto_loop_resume_seed(previous)
    route_agent = args.route_agent or previous.get("route_agent") or "codex"
    route_agent_commands = list(args.route_agent_command or previous.get("route_agent_commands") or [])
    resume_args = argparse.Namespace(
        cwd=str(cwd),
        goal=seed["goal"],
        test_command=list(args.test_command or previous.get("test_commands") or []),
        repair_command=list(args.repair_command or previous.get("repair_commands") or []),
        max_rounds=int(args.extra_rounds),
        max_minutes=float(args.max_minutes or 0.0),
        format=args.format,
        skip_validate=bool(previous.get("skip_validate", False) or args.skip_validate),
        allow_unbounded=bool(args.allow_unbounded),
        skip_deep_loop=not bool(previous.get("deep_loop_enabled", True)),
        deep_loop_intent=seed["goal"],
        current_subchain=seed["current_subchain"],
        next_subchain=list(seed["next_subchains"]),
        auto_route_next=not bool(args.no_auto_route_next),
        route_depth_budget=int(args.extra_route_depth),
        allow_unbounded_routes=bool(args.allow_unbounded_routes or previous.get("allow_unbounded_routes", False)),
        route_agent=route_agent,
        route_agent_command=route_agent_commands,
        route_codex_path=args.route_codex_path or previous.get("route_codex_path"),
        route_codex_sandbox=args.route_codex_sandbox,
        route_codex_approval=args.route_codex_approval,
        route_codex_skip_git_check=not bool(args.route_codex_require_git),
        route_codex_ephemeral=bool(args.route_codex_ephemeral),
        route_codex_json=bool(args.route_codex_json),
        route_codex_output=args.route_codex_output,
        route_agent_idle_timeout=float(
            args.route_agent_idle_timeout
            if args.route_agent_idle_timeout is not None
            else previous.get("route_agent_idle_timeout", DEFAULT_ROUTE_AGENT_IDLE_TIMEOUT_SECONDS)
        ),
        route_agent_wall_timeout=float(
            args.route_agent_wall_timeout
            if args.route_agent_wall_timeout is not None
            else previous.get("route_agent_wall_timeout", DEFAULT_ROUTE_AGENT_WALL_TIMEOUT_SECONDS)
        ),
        route_agent_poll_seconds=float(
            args.route_agent_poll_seconds
            if args.route_agent_poll_seconds is not None
            else previous.get("route_agent_poll_seconds", DEFAULT_ROUTE_AGENT_POLL_SECONDS)
        ),
        deep_loop_quality_score=None,
        deep_loop_pass_threshold=None,
        deep_loop_max_rounds=args.deep_loop_max_rounds,
        harness_report=list(args.harness_report or previous.get("harness_reports") or []),
        skip_problem_escalation=bool(args.skip_problem_escalation),
        problem_promote_threshold=float(args.problem_promote_threshold),
        initial_agent_prompt=seed["initial_agent_prompt"],
        initial_pending_route=seed["initial_pending_route"],
        resume_metadata={
            "source_report": psafe(report_path),
            "source_status": seed["source_status"],
            "source_round": seed["source_round"],
            "source_subchain": seed["source_subchain"],
            "decision": seed["decision"],
        },
    )
    return command_auto_loop(resume_args)


def command_auto_loop(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    test_commands = list(args.test_command or [])
    repair_commands = list(args.repair_command or [])
    if args.skip_validate and not test_commands:
        raise ValueError("auto-loop needs validation or at least one --test-command")
    if args.max_rounds <= 0 and not args.allow_unbounded:
        raise ValueError("--max-rounds must be positive unless --allow-unbounded is set")
    if args.route_depth_budget < 0:
        raise ValueError("--route-depth-budget must be non-negative")
    if args.route_agent not in ROUTE_AGENT_CHOICES:
        raise ValueError(f"--route-agent must be one of: {', '.join(sorted(ROUTE_AGENT_CHOICES))}")
    if args.allow_unbounded and not repair_commands and not args.max_minutes:
        raise ValueError("--allow-unbounded requires at least one --repair-command or --max-minutes")
    round_limit = 10**9 if args.allow_unbounded else int(args.max_rounds)
    started = time.monotonic()
    auto_dir = runs_root(cwd) / run_name("auto-loop", args.goal, "goal")
    ensure_dir(auto_dir)
    write_json(auto_dir / "pre-snapshot.json", {"created_at": utc_now(), "inventory": inventory(cwd), "git": git_info(cwd)})
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "goal": args.goal,
        "status": "running",
        "run_directory": psafe(auto_dir),
        "max_rounds": None if args.allow_unbounded else args.max_rounds,
        "max_minutes": args.max_minutes,
        "test_commands": test_commands,
        "repair_commands": repair_commands,
        "skip_validate": bool(args.skip_validate),
        "deep_loop_enabled": not args.skip_deep_loop,
        "harness_reports": list(getattr(args, "harness_report", None) or []),
        "current_subchain": args.current_subchain,
        "next_subchains": list(args.next_subchain or []),
        "auto_route_next": bool(args.auto_route_next),
        "route_depth_budget": args.route_depth_budget,
        "allow_unbounded_routes": bool(args.allow_unbounded_routes),
        "route_agent": args.route_agent,
        "route_codex_path": str(args.route_codex_path or discover_codex_cli() or "") if args.route_agent == "codex" else None,
        "route_agent_commands": list(args.route_agent_command or []),
        "route_agent_idle_timeout": float(getattr(args, "route_agent_idle_timeout", 0.0) or 0.0),
        "route_agent_wall_timeout": float(getattr(args, "route_agent_wall_timeout", 0.0) or 0.0),
        "route_agent_poll_seconds": float(getattr(args, "route_agent_poll_seconds", DEFAULT_ROUTE_AGENT_POLL_SECONDS) or DEFAULT_ROUTE_AGENT_POLL_SECONDS),
        "routed_transitions": [],
        "rounds": [],
    }
    if getattr(args, "resume_metadata", None):
        payload["resume"] = getattr(args, "resume_metadata")
    seen_failure_signatures: dict[str, int] = {}
    status = "failed"
    final_message = ""
    active_goal = str(args.goal)
    active_subchain = args.current_subchain
    active_next_subchains = list(args.next_subchain or [])
    pending_agent_prompt: str | None = getattr(args, "initial_agent_prompt", None)
    pending_route: dict[str, Any] | None = getattr(args, "initial_pending_route", None)
    unbounded_routes = bool(args.auto_route_next and args.allow_unbounded_routes)
    remaining_route_budget = int(args.route_depth_budget or 0) if args.auto_route_next else 0

    for round_index in range(1, round_limit + 1):
        if args.max_minutes and (time.monotonic() - started) / 60.0 > float(args.max_minutes):
            status = "timeout"
            final_message = "Stopped because max_minutes was reached before the next round."
            break
        args.goal = active_goal
        args.deep_loop_intent = active_goal
        args.current_subchain = active_subchain
        args.next_subchain = list(active_next_subchains)
        round_dir = auto_dir / f"round-{round_index:02d}"
        ensure_dir(round_dir)
        executors: list[dict[str, Any]] = []
        if pending_agent_prompt:
            prompt_file = round_dir / "route-agent-prompt.md"
            prompt_file.write_text(pending_agent_prompt, encoding="utf-8")
            route_commands = auto_loop_route_agent_commands(args, cwd, prompt_file)
            if not route_commands:
                status = "route-next-executor-missing"
                final_message = "Deep-loop requested route_next, but no route agent was configured for automatic subchain execution."
                payload["rounds"].append(
                    {
                        "round": round_index,
                        "round_directory": psafe(round_dir),
                        "goal": active_goal,
                        "subchain": active_subchain,
                        "executors": [],
                        "tests": [],
                        "repairs": [],
                        "status": status,
                        "auto_route": pending_route,
                    }
                )
                break
            for executor_index, command_template in enumerate(route_commands, start=1):
                command = auto_route_template_value(
                    str(command_template),
                    cwd=cwd,
                    subchain=str(active_subchain or ""),
                    goal=active_goal,
                    prompt=pending_agent_prompt,
                    prompt_file=prompt_file,
                    round_index=round_index,
                )
                executors.append(
                    run_auto_command(
                        cwd,
                        round_dir,
                        "route-executor",
                        command,
                        executor_index,
                        idle_timeout_seconds=float(getattr(args, "route_agent_idle_timeout", 0.0) or 0.0),
                        wall_timeout_seconds=float(getattr(args, "route_agent_wall_timeout", 0.0) or 0.0),
                        poll_interval_seconds=float(
                            getattr(args, "route_agent_poll_seconds", DEFAULT_ROUTE_AGENT_POLL_SECONDS)
                            or DEFAULT_ROUTE_AGENT_POLL_SECONDS
                        ),
                    )
                )
            pending_agent_prompt = None
            route_executor_failures = [item for item in executors if item.get("exit_code") != 0]
            if route_executor_failures:
                failure = route_executor_failures[0]
                status = "route-agent-timeout" if failure.get("timed_out") else "route-agent-failed"
                final_message = (
                    "Auto-routed subchain executor timed out before validation. "
                    if failure.get("timed_out")
                    else "Auto-routed subchain executor failed before validation. "
                ) + (
                    f"Target subchain: {active_subchain or '(unset)'}. "
                    f"Command exit={failure.get('exit_code')} signature={failure.get('signature')}."
                )
                round_record = {
                    "round": round_index,
                    "round_directory": psafe(round_dir),
                    "goal": active_goal,
                    "subchain": active_subchain,
                    "executors": executors,
                    "tests": [],
                    "repairs": [],
                    "status": status,
                }
                if pending_route:
                    round_record["auto_route"] = pending_route
                    pending_route = None
                append_jsonl(
                    decisions_path(cwd),
                    {
                        "id": record_id("auto-loop-route-agent-failure", final_message),
                        "timestamp": utc_now(),
                        "type": "auto_loop_route_agent_timeout" if failure.get("timed_out") else "auto_loop_route_agent_failure",
                        "goal": active_goal,
                        "subchain": active_subchain,
                        "round": round_index,
                        "failure": final_message,
                        "command": failure.get("command"),
                        "exit_code": failure.get("exit_code"),
                        "timed_out": bool(failure.get("timed_out")),
                        "timeout_reason": failure.get("timeout_reason"),
                        "signature": failure.get("signature"),
                        "stdout_log": failure.get("stdout_log"),
                        "stderr_log": failure.get("stderr_log"),
                    },
                )
                payload["rounds"].append(round_record)
                break
        tests: list[dict[str, Any]] = []
        test_number = 1
        if not args.skip_validate:
            tests.append(run_auto_validate(cwd, round_dir, test_number))
            test_number += 1
        for command in test_commands:
            tests.append(run_auto_command(cwd, round_dir, "test", command, test_number))
            test_number += 1
        gate_results = executors + tests
        failures = [item for item in gate_results if item.get("exit_code") != 0]
        round_record: dict[str, Any] = {
            "round": round_index,
            "round_directory": psafe(round_dir),
            "goal": active_goal,
            "subchain": active_subchain,
            "executors": executors,
            "tests": tests,
            "repairs": [],
            "status": "passed" if not failures else "failed",
        }
        if pending_route:
            round_record["auto_route"] = pending_route
            pending_route = None
        if not failures:
            if not args.skip_deep_loop:
                result_summary = f"Auto-loop round {round_index} passed all validation and test gates for goal: {active_goal}"
                deep_payload = auto_loop_deep_loop_payload(
                    args,
                    cwd,
                    state,
                    passport,
                    auto_dir=auto_dir,
                    round_index=round_index,
                    round_dir=round_dir,
                    gate_result="pass",
                    result_summary=result_summary,
                    test_results=gate_results,
                )
                deep_dispatch = summarize_deep_loop_dispatch(deep_payload)
                round_record["deep_loop"] = deep_dispatch
                decision = deep_dispatch.get("decision")
                if decision == "route_next" and args.auto_route_next:
                    target_subchains = list(deep_dispatch.get("target_subchains") or [])
                    if not target_subchains:
                        status = "passed"
                        final_message = "All validation and test commands passed; no next subchain is available."
                        payload["rounds"].append(round_record)
                        break
                    if not unbounded_routes and remaining_route_budget <= 0:
                        status = "route-depth-budget-exhausted"
                        final_message = "Deep-loop requested route_next, but route_depth_budget was exhausted."
                        payload["rounds"].append(round_record)
                        break
                    next_subchain = str(target_subchains[0])
                    handoff = deep_payload.get("handoff_package") or {}
                    next_prompt = str(handoff.get("next_work_prompt") or deep_dispatch.get("next_work_prompt") or active_goal)
                    route_record = {
                        "round": round_index,
                        "from_subchain": active_subchain,
                        "to_subchain": next_subchain,
                        "remaining_budget": None if unbounded_routes else remaining_route_budget - 1,
                        "next_goal": next_prompt,
                        "deep_loop_report": deep_payload.get("report_markdown") or deep_payload.get("report_json"),
                    }
                    round_record["auto_route"] = route_record
                    payload["routed_transitions"].append(route_record)
                    active_goal = next_prompt
                    active_subchain = next_subchain
                    active_next_subchains = []
                    pending_agent_prompt = next_prompt
                    pending_route = route_record
                    if not unbounded_routes:
                        remaining_route_budget -= 1
                    round_record["status"] = "route-next-auto-started"
                    payload["rounds"].append(round_record)
                    continue
                if decision == "route_next" and not args.auto_route_next:
                    target_subchains = list(deep_dispatch.get("target_subchains") or [])
                    target_text = ", ".join(target_subchains) if target_subchains else "(none)"
                    status = "route-next-handoff-required"
                    final_message = (
                        "Deep-loop requested route_next, but automatic route consumption is disabled. "
                        f"Next target subchain(s): {target_text}."
                    )
                    payload["rounds"].append(round_record)
                    break
                if decision == "retry_same_route":
                    if repair_commands:
                        for repair_index, command in enumerate(repair_commands, start=1):
                            repair_result = run_auto_command(cwd, round_dir, "repair", command, repair_index)
                            round_record["repairs"].append(repair_result)
                    if args.auto_route_next:
                        target_subchains = list(deep_dispatch.get("target_subchains") or [])
                        retry_subchain = str(target_subchains[0] if target_subchains else (active_subchain or ""))
                        handoff = deep_payload.get("handoff_package") or {}
                        next_prompt = str(handoff.get("next_work_prompt") or deep_dispatch.get("next_work_prompt") or active_goal)
                        retry_record = {
                            "round": round_index,
                            "decision": "retry_same_route",
                            "from_subchain": active_subchain,
                            "to_subchain": retry_subchain,
                            "remaining_budget": None,
                            "next_goal": next_prompt,
                            "deep_loop_report": deep_payload.get("report_markdown") or deep_payload.get("report_json"),
                        }
                        round_record["auto_route"] = retry_record
                        payload["routed_transitions"].append(retry_record)
                        active_goal = next_prompt
                        active_subchain = retry_subchain or active_subchain
                        pending_agent_prompt = next_prompt
                        pending_route = retry_record
                        round_record["status"] = "retry-same-route-auto-started"
                        payload["rounds"].append(round_record)
                        continue
                    status = "retry-same-route-handoff-required"
                    final_message = "Deep-loop requested retry_same_route, but automatic continuation is disabled."
                    payload["rounds"].append(round_record)
                    break
                if decision == "escalate_problem_loop":
                    if not args.skip_problem_escalation:
                        problem_result = auto_loop_problem_escalation(args, cwd, round_dir, deep_payload, tests, [])
                        round_record["problem_loop"] = problem_result
                        if (
                            args.auto_route_next
                            and problem_result.get("exit_code") == 0
                            and problem_result.get("gate_status") == "approved"
                        ):
                            target_subchains = list(deep_dispatch.get("target_subchains") or ["P10"])
                            problem_subchain = str(target_subchains[0] if target_subchains else "P10")
                            handoff = deep_payload.get("handoff_package") or {}
                            problem_prompt = str(handoff.get("next_work_prompt") or deep_dispatch.get("next_work_prompt") or active_goal)
                            problem_record = {
                                "round": round_index,
                                "decision": "escalate_problem_loop",
                                "from_subchain": active_subchain,
                                "to_subchain": problem_subchain,
                                "remaining_budget": None,
                                "next_goal": problem_prompt,
                                "deep_loop_report": deep_payload.get("report_markdown") or deep_payload.get("report_json"),
                                "problem_case_id": problem_result.get("case_id"),
                                "problem_report": problem_result.get("report_path"),
                            }
                            round_record["auto_route"] = problem_record
                            payload["routed_transitions"].append(problem_record)
                            active_goal = problem_prompt
                            active_subchain = problem_subchain
                            active_next_subchains = []
                            pending_agent_prompt = problem_prompt
                            pending_route = problem_record
                            round_record["status"] = "problem-loop-auto-started"
                            payload["rounds"].append(round_record)
                            continue
                        status = "problem-loop-escalated"
                        final_message = "Tests passed, but the deep-loop gate escalated the result into an isolated problem-loop case."
                    else:
                        status = "problem-loop-required"
                        final_message = "Tests passed, but the deep-loop gate requires problem-loop escalation and automatic case creation was skipped."
                    payload["rounds"].append(round_record)
                    break
                if decision == "pause_for_human":
                    status = "human-checkpoint"
                    final_message = "Tests passed, but the deep-loop gate requires a human checkpoint before continuing."
                    payload["rounds"].append(round_record)
                    break
            status = "passed"
            final_message = "All validation and test commands passed."
            payload["rounds"].append(round_record)
            break
        failure = failures[0]
        failure_signature = str(failure["signature"])
        seen_failure_signatures[failure_signature] = seen_failure_signatures.get(failure_signature, 0) + 1
        failure_text = f"Auto-loop gate failed: {failure['command']} exit={failure['exit_code']} signature={failure_signature}"
        route_intent = f"Repair failed test for goal: {args.goal}\n\nFailure: {failure_text}\n\nstderr excerpt:\n{failure.get('stderr_excerpt') or '(none)'}"
        graph = build_route_graph(cwd, state, passport, route_intent)
        route_path = round_dir / "failure-route.json"
        write_json(route_path, graph)
        next_prompt = (graph.get("normalized_input") or {}).get("downstream_prompt") or route_intent
        round_record["route_path"] = psafe(route_path)
        round_record["next_prompt"] = command_excerpt(next_prompt, 900)
        append_jsonl(
            decisions_path(cwd),
            {
                "id": record_id("auto-loop-failure", failure_text),
                "timestamp": utc_now(),
                "type": "auto_loop_failure",
                "goal": args.goal,
                "round": round_index,
                "failure": failure_text,
                "route_path": psafe(route_path),
            },
        )
        next_id = f"next-auto-loop-{failure_signature}"
        update_list_item(
            passport["next_actions"],
            {
                "id": next_id,
                "text": f"Repair auto-loop failure for goal: {args.goal}",
                "stage": state.get("current_stage", "EXECUTION"),
                "status": "todo",
                "owner": "agent",
                "created_at": utc_now(),
                "note": failure_text,
            },
        )
        save_passport(cwd, passport)
        deep_decision = None
        if not args.skip_deep_loop:
            gate_issues = [failure_text]
            if failure.get("stderr_excerpt"):
                gate_issues.append(f"stderr excerpt: {command_excerpt(str(failure.get('stderr_excerpt')), 900)}")
            if failure.get("stdout_excerpt"):
                gate_issues.append(f"stdout excerpt: {command_excerpt(str(failure.get('stdout_excerpt')), 900)}")
            deep_payload = auto_loop_deep_loop_payload(
                args,
                cwd,
                state,
                passport,
                auto_dir=auto_dir,
                round_index=round_index,
                round_dir=round_dir,
                gate_result="fail",
                result_summary=route_intent,
                gate_issues=gate_issues,
                test_results=gate_results,
                extra_paths=[psafe(route_path)],
            )
            deep_dispatch = summarize_deep_loop_dispatch(deep_payload)
            round_record["deep_loop"] = deep_dispatch
            deep_decision = deep_dispatch.get("decision")
            if deep_decision == "escalate_problem_loop":
                if not args.skip_problem_escalation:
                    problem_result = auto_loop_problem_escalation(args, cwd, round_dir, deep_payload, tests, failures)
                    round_record["problem_loop"] = problem_result
                    if (
                        args.auto_route_next
                        and problem_result.get("exit_code") == 0
                        and problem_result.get("gate_status") == "approved"
                    ):
                        target_subchains = list(deep_dispatch.get("target_subchains") or ["P10"])
                        problem_subchain = str(target_subchains[0] if target_subchains else "P10")
                        handoff = deep_payload.get("handoff_package") or {}
                        problem_prompt = str(handoff.get("next_work_prompt") or deep_dispatch.get("next_work_prompt") or route_intent)
                        problem_record = {
                            "round": round_index,
                            "decision": "escalate_problem_loop",
                            "from_subchain": active_subchain,
                            "to_subchain": problem_subchain,
                            "remaining_budget": None,
                            "next_goal": problem_prompt,
                            "deep_loop_report": deep_payload.get("report_markdown") or deep_payload.get("report_json"),
                            "problem_case_id": problem_result.get("case_id"),
                            "problem_report": problem_result.get("report_path"),
                        }
                        round_record["auto_route"] = problem_record
                        payload["routed_transitions"].append(problem_record)
                        active_goal = problem_prompt
                        active_subchain = problem_subchain
                        active_next_subchains = []
                        pending_agent_prompt = problem_prompt
                        pending_route = problem_record
                        round_record["status"] = "problem-loop-auto-started"
                        payload["rounds"].append(round_record)
                        continue
                    status = "problem-loop-escalated"
                    final_message = "Stopped because deep-loop escalated the failed gate into an isolated problem-loop case."
                else:
                    status = "problem-loop-required"
                    final_message = "Stopped because deep-loop requires problem-loop escalation and automatic case creation was skipped."
                payload["rounds"].append(round_record)
                break
            if deep_decision == "pause_for_human":
                status = "human-checkpoint"
                final_message = "Stopped because deep-loop requires a human checkpoint before another auto-loop round."
                payload["rounds"].append(round_record)
                break
            if deep_decision == "retry_same_route":
                if repair_commands:
                    for repair_index, command in enumerate(repair_commands, start=1):
                        repair_result = run_auto_command(cwd, round_dir, "repair", command, repair_index)
                        round_record["repairs"].append(repair_result)
                if args.auto_route_next:
                    target_subchains = list(deep_dispatch.get("target_subchains") or [])
                    retry_subchain = str(target_subchains[0] if target_subchains else (active_subchain or ""))
                    handoff = deep_payload.get("handoff_package") or {}
                    retry_prompt = str(handoff.get("next_work_prompt") or deep_dispatch.get("next_work_prompt") or route_intent)
                    retry_record = {
                        "round": round_index,
                        "decision": "retry_same_route",
                        "from_subchain": active_subchain,
                        "to_subchain": retry_subchain,
                        "remaining_budget": None,
                        "next_goal": retry_prompt,
                        "deep_loop_report": deep_payload.get("report_markdown") or deep_payload.get("report_json"),
                    }
                    round_record["auto_route"] = retry_record
                    payload["routed_transitions"].append(retry_record)
                    active_goal = retry_prompt
                    active_subchain = retry_subchain or active_subchain
                    pending_agent_prompt = retry_prompt
                    pending_route = retry_record
                    round_record["status"] = "retry-same-route-auto-started"
                    payload["rounds"].append(round_record)
                    continue
                status = "retry-same-route-handoff-required"
                final_message = "Stopped because deep-loop requested retry_same_route and automatic continuation is disabled."
                payload["rounds"].append(round_record)
                break
        if seen_failure_signatures[failure_signature] >= 2 and not args.allow_unbounded and deep_decision != "retry_same_route":
            status = "no-progress"
            final_message = f"Stopped because the same failure signature repeated: {failure_signature}."
            payload["rounds"].append(round_record)
            break
        if repair_commands:
            for repair_index, command in enumerate(repair_commands, start=1):
                repair_result = run_auto_command(cwd, round_dir, "repair", command, repair_index)
                round_record["repairs"].append(repair_result)
            round_record["status"] = "repair-attempted"
        else:
            round_record["status"] = "failed-no-repair-command"
        payload["rounds"].append(round_record)
    else:
        status = "round-limit"
        final_message = "Stopped because max_rounds was exhausted."

    write_json(auto_dir / "post-state.json", {"captured_at": utc_now(), "inventory": inventory(cwd), "git": git_info(cwd)})
    payload["status"] = status
    payload["round_count"] = len(payload["rounds"])
    payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
    payload["final_message"] = final_message
    if status == "passed":
        checkpoint_note = f"Auto-loop passed for goal: {args.goal}"
        checkpoint_proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--cwd", str(cwd), "checkpoint", "--name", "auto-loop-pass", "--note", checkpoint_note],
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        handoff_proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--cwd", str(cwd), "handoff", "--name", "auto-loop-pass", "--note", checkpoint_note],
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        payload["completion_records"] = {
            "checkpoint_exit_code": checkpoint_proc.returncode,
            "checkpoint_output": (checkpoint_proc.stdout or checkpoint_proc.stderr or "").strip(),
            "handoff_exit_code": handoff_proc.returncode,
            "handoff_output": (handoff_proc.stdout or handoff_proc.stderr or "").strip(),
        }
    report_json = reports_root(cwd) / f"{timestamp()}-auto-loop.json"
    report_md = reports_root(cwd) / f"{timestamp()}-auto-loop.md"
    write_json(report_json, payload)
    write_lines(report_md, auto_loop_report_markdown(payload))
    payload["report_json"] = psafe(report_json)
    payload["report_markdown"] = psafe(report_md)
    state = load_state(cwd)
    state["active_run_id"] = auto_dir.name
    state["counters"]["runs"] = int(state["counters"].get("runs", 0)) + 1
    if status != "passed":
        state["counters"]["failures"] = int(state["counters"].get("failures", 0)) + 1
    save_state(cwd, state)
    append_jsonl(
        artifacts_path(cwd),
        {
            "timestamp": utc_now(),
            "type": "auto_loop",
            "goal": args.goal,
            "status": status,
            "run_directory": psafe(auto_dir),
            "report": psafe(report_md),
        },
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    else:
        print("\n".join(auto_loop_report_markdown(payload)).rstrip() + "\n")
    return 0 if status == "passed" else 1


def add_cli_option(command: list[str], flag: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str) and value == "":
        return
    command.extend([flag, str(value)])


def add_cli_repeated(command: list[str], flag: str, values: list[Any] | None) -> None:
    for value in values or []:
        add_cli_option(command, flag, value)


def append_auto_loop_common_cli_options(command: list[str], args: argparse.Namespace, *, include_goal: bool) -> None:
    if include_goal:
        add_cli_option(command, "--goal", args.goal)
    add_cli_repeated(command, "--test-command", list(args.test_command or []))
    add_cli_repeated(command, "--repair-command", list(args.repair_command or []))
    add_cli_option(command, "--max-minutes", args.max_minutes)
    command.extend(["--format", "json"])
    if getattr(args, "skip_validate", False):
        command.append("--skip-validate")
    if getattr(args, "allow_unbounded", False):
        command.append("--allow-unbounded")
    if getattr(args, "skip_deep_loop", False):
        command.append("--skip-deep-loop")
    add_cli_option(command, "--deep-loop-intent", getattr(args, "deep_loop_intent", None))
    add_cli_option(command, "--current-subchain", getattr(args, "current_subchain", None))
    add_cli_repeated(command, "--next-subchain", list(getattr(args, "next_subchain", None) or []))
    if not getattr(args, "auto_route_next", True):
        command.append("--no-auto-route-next")
    add_cli_option(command, "--route-depth-budget", getattr(args, "route_depth_budget", None))
    if getattr(args, "allow_unbounded_routes", False):
        command.append("--allow-unbounded-routes")
    add_cli_option(command, "--route-agent", getattr(args, "route_agent", None))
    add_cli_repeated(command, "--route-agent-command", list(getattr(args, "route_agent_command", None) or []))
    add_cli_option(command, "--route-codex-path", getattr(args, "route_codex_path", None))
    add_cli_option(command, "--route-codex-sandbox", getattr(args, "route_codex_sandbox", None))
    add_cli_option(command, "--route-codex-approval", getattr(args, "route_codex_approval", None))
    if getattr(args, "route_codex_require_git", False):
        command.append("--route-codex-require-git")
    if getattr(args, "route_codex_ephemeral", False):
        command.append("--route-codex-ephemeral")
    if getattr(args, "route_codex_json", False):
        command.append("--route-codex-json")
    add_cli_option(command, "--route-codex-output", getattr(args, "route_codex_output", None))
    add_cli_option(command, "--route-agent-idle-timeout", getattr(args, "route_agent_idle_timeout", None))
    add_cli_option(command, "--route-agent-wall-timeout", getattr(args, "route_agent_wall_timeout", None))
    add_cli_option(command, "--route-agent-poll-seconds", getattr(args, "route_agent_poll_seconds", None))
    add_cli_option(command, "--deep-loop-quality-score", getattr(args, "deep_loop_quality_score", None))
    add_cli_option(command, "--deep-loop-pass-threshold", getattr(args, "deep_loop_pass_threshold", None))
    add_cli_option(command, "--deep-loop-max-rounds", getattr(args, "deep_loop_max_rounds", None))
    add_cli_repeated(command, "--harness-report", list(getattr(args, "harness_report", None) or []))
    if getattr(args, "skip_problem_escalation", False):
        command.append("--skip-problem-escalation")
    add_cli_option(command, "--problem-promote-threshold", getattr(args, "problem_promote_threshold", None))


def build_watchdog_auto_loop_command(args: argparse.Namespace, cwd: Path) -> list[str]:
    command = [sys.executable, str(Path(__file__).resolve()), "--cwd", str(cwd), "auto-loop"]
    append_auto_loop_common_cli_options(command, args, include_goal=True)
    add_cli_option(command, "--max-rounds", args.max_rounds)
    return command


def build_watchdog_resume_command(args: argparse.Namespace, cwd: Path) -> list[str]:
    command = [sys.executable, str(Path(__file__).resolve()), "--cwd", str(cwd), "auto-loop-resume", "--latest"]
    add_cli_option(command, "--extra-rounds", args.resume_extra_rounds)
    add_cli_option(command, "--extra-route-depth", args.resume_extra_route_depth)
    resume_minutes = args.resume_max_minutes if args.resume_max_minutes is not None else args.max_minutes
    add_cli_option(command, "--max-minutes", resume_minutes)
    command.extend(["--format", "json"])
    if getattr(args, "skip_validate", False):
        command.append("--skip-validate")
    if getattr(args, "allow_unbounded", False):
        command.append("--allow-unbounded")
    if getattr(args, "allow_unbounded_routes", False):
        command.append("--allow-unbounded-routes")
    if not getattr(args, "auto_route_next", True):
        command.append("--no-auto-route-next")
    add_cli_option(command, "--route-agent", getattr(args, "route_agent", None))
    add_cli_repeated(command, "--route-agent-command", list(getattr(args, "route_agent_command", None) or []))
    add_cli_option(command, "--route-codex-path", getattr(args, "route_codex_path", None))
    add_cli_option(command, "--route-codex-sandbox", getattr(args, "route_codex_sandbox", None))
    add_cli_option(command, "--route-codex-approval", getattr(args, "route_codex_approval", None))
    if getattr(args, "route_codex_require_git", False):
        command.append("--route-codex-require-git")
    if getattr(args, "route_codex_ephemeral", False):
        command.append("--route-codex-ephemeral")
    if getattr(args, "route_codex_json", False):
        command.append("--route-codex-json")
    add_cli_option(command, "--route-codex-output", getattr(args, "route_codex_output", None))
    add_cli_option(command, "--route-agent-idle-timeout", getattr(args, "route_agent_idle_timeout", None))
    add_cli_option(command, "--route-agent-wall-timeout", getattr(args, "route_agent_wall_timeout", None))
    add_cli_option(command, "--route-agent-poll-seconds", getattr(args, "route_agent_poll_seconds", None))
    add_cli_option(command, "--deep-loop-max-rounds", getattr(args, "deep_loop_max_rounds", None))
    add_cli_repeated(command, "--harness-report", list(getattr(args, "harness_report", None) or []))
    if getattr(args, "skip_problem_escalation", False):
        command.append("--skip-problem-escalation")
    add_cli_option(command, "--problem-promote-threshold", getattr(args, "problem_promote_threshold", None))
    return command


def parse_child_auto_loop_payload(result: dict[str, Any]) -> dict[str, Any] | None:
    stdout_log = result.get("stdout_log")
    if not stdout_log:
        return None
    try:
        text = Path(str(stdout_log)).read_text(encoding="utf-8", errors="replace")
        value = json.loads(text or "{}")
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def report_path_from_child_payload(payload: dict[str, Any] | None) -> Path | None:
    if not payload:
        return None
    report = payload.get("report_json")
    if not report:
        return None
    path = Path(str(report))
    return path if path.exists() else None


def watchdog_report_markdown(payload: dict[str, Any]) -> list[str]:
    lines = [
        "# Research Auto Loop Watchdog Report",
        "",
        f"- Created at UTC: {payload['timestamp']}",
        f"- Goal: {payload['goal']}",
        f"- Status: {payload['status']}",
        f"- Attempts: {payload['attempt_count']}",
        f"- Resumes: {payload['resume_count']}",
        f"- Watchdog directory: `{payload['watchdog_directory']}`",
        "",
        "## Attempts",
        "",
    ]
    for item in payload.get("attempts") or []:
        lines.append(
            f"- Attempt {item.get('attempt')}: {item.get('kind')} exit={item.get('exit_code')} status={item.get('source_status') or '(unknown)'}"
        )
        if item.get("timed_out"):
            lines.append(f"  - timeout: {item.get('timeout_reason')}")
        if item.get("report_json"):
            lines.append(f"  - report: `{item.get('report_json')}`")
        if item.get("stdout_log"):
            lines.append(f"  - stdout: `{item.get('stdout_log')}`")
        if item.get("stderr_log"):
            lines.append(f"  - stderr: `{item.get('stderr_log')}`")
        supervisor = item.get("external_supervisor") if isinstance(item.get("external_supervisor"), dict) else {}
        if supervisor:
            lines.append(
                "  - external supervisor: "
                f"{supervisor.get('provider')} status={supervisor.get('status')} "
                f"recommendation={supervisor.get('recommendation')} "
                f"effective_resumable={supervisor.get('effective_resumable')}"
            )
            if supervisor.get("report_json"):
                lines.append(f"  - supervisor report: `{supervisor.get('report_json')}`")
    if payload.get("final_message"):
        lines.extend(["", "## Final Message", "", payload["final_message"]])
    return lines


def auto_loop_payload_has_unattended_continuation(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    if str(payload.get("status") or "") == "passed":
        return False
    rounds = list(payload.get("rounds") or [])
    if not rounds:
        return False
    last_round = rounds[-1] if isinstance(rounds[-1], dict) else {}
    route = last_round.get("auto_route") if isinstance(last_round.get("auto_route"), dict) else {}
    if route and route.get("next_goal") and route.get("to_subchain"):
        return True
    deep_loop = last_round.get("deep_loop") if isinstance(last_round.get("deep_loop"), dict) else {}
    continuation = deep_loop.get("continuation_contract") if isinstance(deep_loop.get("continuation_contract"), dict) else {}
    if continuation.get("requires_human") is True:
        return False
    if continuation.get("unattended_safe") is False:
        return False
    decision = str(continuation.get("decision") or deep_loop.get("decision") or "")
    if decision not in {"route_next", "retry_same_route", "escalate_problem_loop"}:
        return False
    prompt = continuation.get("next_work_prompt") or deep_loop.get("next_work_prompt") or route.get("next_goal")
    targets = list(continuation.get("target_subchains") or deep_loop.get("target_subchains") or [])
    if decision == "retry_same_route":
        return bool(prompt)
    if decision == "escalate_problem_loop":
        return bool(prompt or targets or deep_loop)
    return bool(prompt and targets)


def watchdog_child_is_resumable(source_status: str, child_payload: dict[str, Any] | None) -> bool:
    if source_status == "passed":
        return False
    return source_status in RESUMABLE_AUTO_LOOP_STATUSES or auto_loop_payload_has_unattended_continuation(child_payload)


def external_supervisor_secret_redact(text: str, secret: str | None) -> str:
    value = str(text or "")
    if secret:
        value = value.replace(secret, "[redacted]")
    return value


def read_windows_user_environment_variable(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
    except ImportError:
        return ""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _kind = winreg.QueryValueEx(key, name)
    except OSError:
        return ""
    return str(value or "")


def external_supervisor_api_key() -> str:
    return os.environ.get("DEEPSEEK_API_KEY", "") or read_windows_user_environment_variable("DEEPSEEK_API_KEY")


def external_supervisor_resume_seed_available(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    try:
        auto_loop_resume_seed(payload)
    except Exception:
        return False
    return True


def external_supervisor_result(
    *,
    cwd: Path,
    attempt_index: int,
    provider: str,
    status: str,
    goal: str,
    source_status: str,
    local_resumable: bool,
    effective_resumable: bool,
    fail_open: bool,
    model: str | None = None,
    recommendation: str = "local_decision",
    confidence: float | None = None,
    reasons: list[Any] | None = None,
    risk_flags: list[Any] | None = None,
    next_prompt_patch: str | None = None,
    error: str | None = None,
    error_type: str | None = None,
    usage: dict[str, Any] | None = None,
    raw_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "provider": provider,
        "status": status,
        "model": model,
        "goal": goal,
        "source_status": source_status,
        "local_resumable": bool(local_resumable),
        "effective_resumable": bool(effective_resumable),
        "fail_open": bool(fail_open),
        "recommendation": recommendation,
        "confidence": confidence,
        "reasons": list(reasons or []),
        "risk_flags": list(risk_flags or []),
        "next_prompt_patch": next_prompt_patch or "",
    }
    if error:
        result["error"] = error
    if error_type:
        result["error_type"] = error_type
    if usage:
        result["usage"] = usage
    if raw_decision:
        result["raw_decision"] = raw_decision
    if provider != "none":
        report_path = supervisor_root(cwd) / f"{timestamp()}-watchdog-attempt-{attempt_index:02d}-{slug(provider)}.json"
        result["report_json"] = psafe(report_path)
        write_json(report_path, result)
    return result


def external_supervisor_prompt(
    *,
    goal: str,
    source_status: str,
    child_payload: dict[str, Any] | None,
    local_resumable: bool,
    max_chars: int,
) -> str:
    compact_payload = {
        "status": source_status,
        "goal": (child_payload or {}).get("goal") if isinstance(child_payload, dict) else goal,
        "final_message": (child_payload or {}).get("final_message") if isinstance(child_payload, dict) else "",
        "rounds": [],
        "routed_transitions": (child_payload or {}).get("routed_transitions") if isinstance(child_payload, dict) else [],
    }
    if isinstance(child_payload, dict):
        for round_item in list(child_payload.get("rounds") or [])[-3:]:
            if not isinstance(round_item, dict):
                continue
            deep_loop = round_item.get("deep_loop") if isinstance(round_item.get("deep_loop"), dict) else {}
            compact_payload["rounds"].append(
                {
                    "round": round_item.get("round"),
                    "goal": round_item.get("goal"),
                    "subchain": round_item.get("subchain"),
                    "status": round_item.get("status"),
                    "auto_route": round_item.get("auto_route"),
                    "deep_loop_decision": deep_loop.get("decision"),
                    "continuation_contract": deep_loop.get("continuation_contract"),
                    "blocking_dimensions": deep_loop.get("blocking_dimensions"),
                    "problem_loop": round_item.get("problem_loop"),
                    "tests": round_item.get("tests"),
                    "executors": round_item.get("executors"),
                }
            )
    payload_text = command_excerpt(json.dumps(compact_payload, indent=2, ensure_ascii=True, default=str), max_chars)
    return (
        "Return json only. Review this unattended research loop watchdog attempt as a supplemental supervisor.\n"
        "Do not recommend pausing unless there is a real human-only blocker, safety issue, or missing credential.\n"
        "Never execute tools or edit files. Judge whether the local watchdog should keep its local continuation decision.\n"
        "Expected JSON shape:\n"
        "{\n"
        '  "recommendation": "local_decision|continue_same_route|retry_same_route|route_next|escalate_problem_loop|pause_for_human",\n'
        '  "confidence": 0.0,\n'
        '  "unattended_safe": true,\n'
        '  "requires_human": false,\n'
        '  "reasons": ["short reason"],\n'
        '  "risk_flags": ["short risk"],\n'
        '  "next_prompt_patch": ""\n'
        "}\n\n"
        f"Project goal: {goal}\n"
        f"Child status: {source_status or '(unknown)'}\n"
        f"Local watchdog says resumable: {bool(local_resumable)}\n"
        "Child auto-loop report excerpt:\n"
        f"{payload_text}"
    )


def deepseek_supervisor_request_payload(args: argparse.Namespace, prompt: str) -> dict[str, Any]:
    return {
        "model": str(getattr(args, "external_supervisor_model", DEFAULT_EXTERNAL_SUPERVISOR_MODEL) or DEFAULT_EXTERNAL_SUPERVISOR_MODEL),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a supplemental watchdog supervisor for an autonomous research loop. "
                    "Output strict json only. You are advisory and fail-open: preserve local continuation unless a true human-only blocker exists."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "thinking": {"type": "enabled"},
        "reasoning_effort": str(getattr(args, "external_supervisor_reasoning_effort", "high") or "high"),
        "max_tokens": 1600,
        "stream": False,
    }


def parse_deepseek_supervisor_content(content: str) -> dict[str, Any]:
    parsed = json.loads(content or "{}")
    if not isinstance(parsed, dict):
        raise ValueError("external supervisor response content is not a JSON object")
    return parsed


def normalize_external_supervisor_decision(decision: dict[str, Any]) -> tuple[str, float | None, bool | None, bool | None]:
    recommendation = str(decision.get("recommendation") or decision.get("next_action") or "local_decision").strip().lower()
    recommendation = recommendation.replace("-", "_").replace(" ", "_")
    if recommendation not in EXTERNAL_SUPERVISOR_CONTINUE_RECOMMENDATIONS and recommendation not in {
        "local_decision",
        "pause_for_human",
        "observe",
    }:
        recommendation = "local_decision"
    confidence = decision.get("confidence")
    try:
        confidence_value = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        confidence_value = None
    unattended_safe = decision.get("unattended_safe")
    requires_human = decision.get("requires_human")
    return (
        recommendation,
        confidence_value,
        unattended_safe if isinstance(unattended_safe, bool) else None,
        requires_human if isinstance(requires_human, bool) else None,
    )


def external_supervisor_effective_resumable(
    *,
    child_payload: dict[str, Any] | None,
    local_resumable: bool,
    recommendation: str,
    unattended_safe: bool | None,
    requires_human: bool | None,
) -> bool:
    if local_resumable:
        return True
    if recommendation not in EXTERNAL_SUPERVISOR_CONTINUE_RECOMMENDATIONS:
        return False
    if unattended_safe is False or requires_human is True:
        return False
    return external_supervisor_resume_seed_available(child_payload)


def external_supervisor_review(
    args: argparse.Namespace,
    cwd: Path,
    *,
    attempt_index: int,
    goal: str,
    source_status: str,
    child_payload: dict[str, Any] | None,
    local_resumable: bool,
) -> dict[str, Any]:
    provider = str(getattr(args, "external_supervisor", "none") or "none").strip().lower()
    if provider == "none":
        return external_supervisor_result(
            cwd=cwd,
            attempt_index=attempt_index,
            provider="none",
            status="disabled",
            goal=goal,
            source_status=source_status,
            local_resumable=local_resumable,
            effective_resumable=local_resumable,
            fail_open=True,
        )
    if provider != "deepseek":
        return external_supervisor_result(
            cwd=cwd,
            attempt_index=attempt_index,
            provider=provider,
            status="failed",
            goal=goal,
            source_status=source_status,
            local_resumable=local_resumable,
            effective_resumable=local_resumable,
            fail_open=True,
            error=f"unsupported external supervisor provider: {provider}",
            error_type="unsupported_provider",
        )

    api_key = external_supervisor_api_key()
    model = str(getattr(args, "external_supervisor_model", DEFAULT_EXTERNAL_SUPERVISOR_MODEL) or DEFAULT_EXTERNAL_SUPERVISOR_MODEL)
    if not api_key:
        return external_supervisor_result(
            cwd=cwd,
            attempt_index=attempt_index,
            provider=provider,
            status="skipped",
            model=model,
            goal=goal,
            source_status=source_status,
            local_resumable=local_resumable,
            effective_resumable=local_resumable,
            fail_open=True,
            error="DeepSeek supervisor credential is not set; continuing with local watchdog decision.",
            error_type="missing_credential",
        )

    timeout_seconds = float(getattr(args, "external_supervisor_timeout", DEFAULT_EXTERNAL_SUPERVISOR_TIMEOUT_SECONDS) or 0.0)
    max_chars = int(getattr(args, "external_supervisor_max_chars", DEFAULT_EXTERNAL_SUPERVISOR_MAX_CHARS) or DEFAULT_EXTERNAL_SUPERVISOR_MAX_CHARS)
    base_url = str(getattr(args, "external_supervisor_base_url", DEFAULT_EXTERNAL_SUPERVISOR_BASE_URL) or DEFAULT_EXTERNAL_SUPERVISOR_BASE_URL).rstrip("/")
    request_payload = deepseek_supervisor_request_payload(
        args,
        external_supervisor_prompt(
            goal=goal,
            source_status=source_status,
            child_payload=child_payload,
            local_resumable=local_resumable,
            max_chars=max_chars,
        ),
    )
    endpoint = f"{base_url}/chat/completions"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(request_payload, ensure_ascii=True, default=str).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds if timeout_seconds > 0 else None) as response:
            raw_response = response.read().decode("utf-8", errors="replace")
        response_payload = json.loads(raw_response or "{}")
        choices = response_payload.get("choices") if isinstance(response_payload, dict) else []
        choice = choices[0] if choices and isinstance(choices[0], dict) else {}
        message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
        content = str(message.get("content") or "")
        if not content.strip():
            raise ValueError("external supervisor returned empty content")
        decision = parse_deepseek_supervisor_content(content)
        recommendation, confidence, unattended_safe, requires_human = normalize_external_supervisor_decision(decision)
        effective_resumable = external_supervisor_effective_resumable(
            child_payload=child_payload,
            local_resumable=local_resumable,
            recommendation=recommendation,
            unattended_safe=unattended_safe,
            requires_human=requires_human,
        )
        return external_supervisor_result(
            cwd=cwd,
            attempt_index=attempt_index,
            provider=provider,
            status="ok",
            model=model,
            goal=goal,
            source_status=source_status,
            local_resumable=local_resumable,
            effective_resumable=effective_resumable,
            fail_open=True,
            recommendation=recommendation,
            confidence=confidence,
            reasons=list(decision.get("reasons") or []),
            risk_flags=list(decision.get("risk_flags") or []),
            next_prompt_patch=str(decision.get("next_prompt_patch") or ""),
            usage=response_payload.get("usage") if isinstance(response_payload.get("usage"), dict) else None,
            raw_decision=decision,
        )
    except Exception as exc:
        return external_supervisor_result(
            cwd=cwd,
            attempt_index=attempt_index,
            provider=provider,
            status="failed",
            model=model,
            goal=goal,
            source_status=source_status,
            local_resumable=local_resumable,
            effective_resumable=local_resumable,
            fail_open=True,
            error=external_supervisor_secret_redact(repr(exc), api_key),
            error_type=exc.__class__.__name__,
        )


def watchdog_resume_allowed(args: argparse.Namespace, resume_count: int) -> bool:
    if bool(getattr(args, "allow_unbounded_resumes", False)):
        return True
    return resume_count < int(getattr(args, "max_resumes", 0))


def command_auto_loop_watchdog(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    if args.max_resumes < 0:
        raise ValueError("--max-resumes must be non-negative")
    watchdog_dir = watchdog_root(cwd) / run_name("auto-loop-watchdog", args.goal, "goal")
    ensure_dir(watchdog_dir)
    active_path = watchdog_root(cwd) / "active-run.json"
    started = time.monotonic()
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "goal": args.goal,
        "status": "running",
        "watchdog_directory": psafe(watchdog_dir),
        "max_resumes": args.max_resumes,
        "allow_unbounded_resumes": bool(args.allow_unbounded_resumes),
        "resume_extra_rounds": args.resume_extra_rounds,
        "resume_extra_route_depth": args.resume_extra_route_depth,
        "child_idle_timeout": float(args.child_idle_timeout or 0.0),
        "child_wall_timeout": float(args.child_wall_timeout or 0.0),
        "poll_seconds": float(args.poll_seconds or DEFAULT_WATCHDOG_POLL_SECONDS),
        "external_supervisor": str(getattr(args, "external_supervisor", "none") or "none"),
        "external_supervisor_model": (
            str(getattr(args, "external_supervisor_model", "") or DEFAULT_EXTERNAL_SUPERVISOR_MODEL)
            if str(getattr(args, "external_supervisor", "none") or "none") != "none"
            else None
        ),
        "attempts": [],
        "resume_count": 0,
    }
    write_json(active_path, payload)
    command = build_watchdog_auto_loop_command(args, cwd)
    kind = "auto-loop"
    status = "failed"
    final_message = ""
    resume_count = 0

    while True:
        attempt_index = len(payload["attempts"]) + 1
        result = run_monitored_process(
            cwd,
            watchdog_dir,
            f"watchdog-{kind}",
            command,
            attempt_index,
            shell=False,
            idle_timeout_seconds=float(args.child_idle_timeout or 0.0),
            wall_timeout_seconds=float(args.child_wall_timeout or 0.0),
            poll_interval_seconds=float(args.poll_seconds or DEFAULT_WATCHDOG_POLL_SECONDS),
        )
        child_payload = parse_child_auto_loop_payload(result)
        report_path = report_path_from_child_payload(child_payload)
        source_status = str((child_payload or {}).get("status") or "")
        local_child_resumable = watchdog_child_is_resumable(source_status, child_payload)
        supervisor_review = external_supervisor_review(
            args,
            cwd,
            attempt_index=attempt_index,
            goal=args.goal,
            source_status=source_status,
            child_payload=child_payload,
            local_resumable=local_child_resumable,
        )
        child_resumable = bool(supervisor_review.get("effective_resumable", local_child_resumable))
        attempt = {
            "attempt": attempt_index,
            "kind": kind,
            "command": result.get("command"),
            "exit_code": result.get("exit_code"),
            "timed_out": bool(result.get("timed_out")),
            "timeout_reason": result.get("timeout_reason"),
            "stdout_log": result.get("stdout_log"),
            "stderr_log": result.get("stderr_log"),
            "source_status": source_status or None,
            "report_json": psafe(report_path) if report_path else None,
            "resumable": bool(child_resumable),
            "local_resumable": bool(local_child_resumable),
        }
        if supervisor_review.get("status") != "disabled":
            attempt["external_supervisor"] = supervisor_review
        payload["attempts"].append(attempt)
        payload["attempt_count"] = len(payload["attempts"])
        payload["resume_count"] = resume_count
        payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
        write_json(active_path, payload)

        if result.get("timed_out") and not report_path:
            status = "watchdog-child-timeout"
            final_message = "Watchdog stopped because the child auto-loop process timed out before writing a resumable report."
            break
        if source_status == "passed":
            status = "passed"
            final_message = "The watched auto-loop reached a passed terminal state."
            break
        if child_resumable:
            if not watchdog_resume_allowed(args, resume_count):
                status = "watchdog-max-resumes-exhausted"
                final_message = f"Watchdog stopped because max_resumes={args.max_resumes} was exhausted at status {source_status}."
                break
            resume_count += 1
            payload["resume_count"] = resume_count
            command = build_watchdog_resume_command(args, cwd)
            kind = "auto-loop-resume"
            continue
        status = source_status or ("watchdog-child-failed" if result.get("exit_code") else "watchdog-stopped")
        final_message = f"Watchdog stopped at non-resumable child status: {status}."
        break

    payload["status"] = status
    payload["resume_count"] = resume_count
    payload["attempt_count"] = len(payload["attempts"])
    payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
    payload["final_message"] = final_message
    report_json = reports_root(cwd) / f"{timestamp()}-auto-loop-watchdog.json"
    report_md = reports_root(cwd) / f"{timestamp()}-auto-loop-watchdog.md"
    write_json(report_json, payload)
    write_lines(report_md, watchdog_report_markdown(payload))
    payload["report_json"] = psafe(report_json)
    payload["report_markdown"] = psafe(report_md)
    write_json(active_path, payload)
    append_jsonl(
        artifacts_path(cwd),
        {
            "timestamp": utc_now(),
            "type": "auto_loop_watchdog",
            "goal": args.goal,
            "status": status,
            "watchdog_directory": psafe(watchdog_dir),
            "report": psafe(report_md),
        },
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    else:
        print("\n".join(watchdog_report_markdown(payload)).rstrip() + "\n")
    return 0 if status == "passed" else 1


def latest_file(root: Path, pattern: str = "*.md") -> Path | None:
    files = sorted(root.glob(pattern), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    return files[0] if files else None


def command_resume(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    profile = passport.get("profile") or {}
    handoff = Path(state["latest_handoff"]) if state.get("latest_handoff") else latest_file(handoffs_root(cwd))
    checkpoint = Path(state["latest_checkpoint"]) if state.get("latest_checkpoint") else latest_file(checkpoints_root(cwd))
    lines = [
        "# Research Loop Resume Brief",
        "",
        f"- Project root: {cwd}",
        f"- Project id: {state.get('project_id')}",
        f"- Current stage: {state.get('current_stage')}",
        f"- Updated at UTC: {state.get('updated_at')}",
        "",
        "## Project",
        "",
        f"- Title: {passport.get('project_title') or '(not set)'}",
        f"- Domain: {passport.get('domain') or '(not set)'}",
        f"- Output targets: {', '.join(passport.get('output_targets') or []) or '(not set)'}",
        f"- Target venue: {profile.get('target_venue') or '(not set)'}",
        f"- Citation style: {profile.get('citation_style') or '(not set)'}",
        f"- Preferred language: {profile.get('preferred_language') or '(not set)'}",
        f"- Data sensitivity: {profile.get('data_sensitivity') or 'normal'}",
        f"- Verification strictness: {profile.get('verification_strictness') or 'standard'}",
        f"- Route mode: {profile.get('route_mode') or 'standard'}",
        "",
        "## Active Research Question",
        "",
        passport.get("research_question") or "(not set)",
        "",
        "## Summary",
        "",
        passport.get("project_summary") or "(not set)",
        "",
        "## Counts",
        "",
        f"- Materials: {len(passport.get('materials') or [])}",
        f"- Claims: {len(passport.get('key_claims') or [])}",
        f"- Evidence records: {len(current_evidence_records(cwd))}",
        f"- Decisions: {len([r for r in read_jsonl(decisions_path(cwd)) if r.get('type') == 'decision'])}",
        f"- Open questions: {len([q for q in passport.get('open_questions') or [] if q.get('status') == 'open'])}",
        f"- Open risks: {len([r for r in passport.get('risks') or [] if r.get('status') == 'open'])}",
        "",
        "## Next Actions",
        "",
    ]
    next_actions = [item for item in passport.get("next_actions") or [] if item.get("status") in {"todo", "in-progress", "blocked"}]
    if next_actions:
        for item in next_actions[:12]:
            lines.append(f"- [{item.get('status')}] {item.get('text')} ({item.get('id')})")
    else:
        lines.append("- (No active next actions recorded.)")
    if handoff and handoff.exists():
        lines.extend(["", "## Latest Handoff Excerpt", "", text_excerpt(handoff, args.excerpt_chars)])
    if checkpoint and checkpoint.exists():
        lines.extend(["", "## Latest Checkpoint Excerpt", "", text_excerpt(checkpoint, args.excerpt_chars)])
    output = "\n".join(lines).rstrip() + "\n"
    if args.write:
        path = reports_root(cwd) / f"{timestamp()}-resume-brief.md"
        write_lines(path, output.splitlines())
        print(f"Resume brief: {path}")
    else:
        print(output)
    return 0


CLAIM_VERDICT_ORDER = {"verified": 0, "partial": 1, "unsupported": 2, "failed": 3}


def source_material_keys(passport: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for material in passport.get("materials") or []:
        if not isinstance(material, dict):
            continue
        for key in ["id", "source", "path", "title"]:
            value = material.get(key)
            if value:
                keys.add(str(value).strip().lower())
        metadata = material.get("metadata") if isinstance(material.get("metadata"), dict) else {}
        for key in ["doi", "url", "id", "title"]:
            value = metadata.get(key)
            if value:
                keys.add(str(value).strip().lower())
        doi = normalize_doi(metadata.get("doi") or material.get("source"))
        if doi:
            keys.add(doi)
            keys.add(f"https://doi.org/{doi}")
    return keys


def evidence_source_registered(source: str | None, material_keys: set[str]) -> bool:
    if not source:
        return False
    raw = str(source).strip().lower()
    if raw in material_keys:
        return True
    doi = normalize_doi(raw)
    if doi and (doi in material_keys or f"https://doi.org/{doi}" in material_keys):
        return True
    return False


def claim_verdict_from_issues(evidence_checks: list[dict[str, Any]], issues: list[dict[str, Any]]) -> str:
    if any(issue.get("code") == "missing_evidence_ids" for issue in issues):
        return "unsupported"
    if any(issue.get("severity") == "high" for issue in issues):
        return "failed"
    if issues:
        return "partial"
    if evidence_checks and all(check.get("status") == "verified" for check in evidence_checks):
        return "verified"
    return "partial" if evidence_checks else "unsupported"


def claim_evidence_report(cwd: Path, state: dict[str, Any], passport: dict[str, Any], require_source_material: bool = False) -> dict[str, Any]:
    evidence_records = current_evidence_records(cwd)
    material_keys = source_material_keys(passport)
    claims = [
        claim
        for claim in passport.get("key_claims") or []
        if isinstance(claim, dict) and claim.get("status") != "retracted"
    ]
    claim_reports: list[dict[str, Any]] = []
    all_issues: list[dict[str, Any]] = []

    for claim in claims:
        claim_id = str(claim.get("id") or "")
        evidence_ids = [str(value) for value in claim.get("evidence_ids") or [] if str(value).strip()]
        evidence_checks: list[dict[str, Any]] = []
        issues: list[dict[str, Any]] = []
        if not evidence_ids:
            issues.append(
                {
                    "severity": "high",
                    "code": "missing_evidence_ids",
                    "claim_id": claim_id,
                    "text": "Claim has no evidence ids.",
                }
            )
        for evidence_id in evidence_ids:
            record = evidence_records.get(evidence_id)
            if not record:
                issues.append(
                    {
                        "severity": "high",
                        "code": "missing_evidence_record",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Claim references missing evidence record: {evidence_id}.",
                    }
                )
                evidence_checks.append({"evidence_id": evidence_id, "exists": False, "verdict": "failed"})
                continue
            source = record.get("source")
            locator = record.get("locator")
            status = str(record.get("status") or "unverified")
            registered = evidence_source_registered(str(source) if source else None, material_keys)
            check_issues: list[str] = []
            if not source:
                issues.append(
                    {
                        "severity": "high",
                        "code": "missing_source",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Evidence {evidence_id} has no source.",
                    }
                )
                check_issues.append("missing_source")
            if not locator:
                issues.append(
                    {
                        "severity": "medium",
                        "code": "missing_locator",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Evidence {evidence_id} has no locator.",
                    }
                )
                check_issues.append("missing_locator")
            if status == "failed":
                issues.append(
                    {
                        "severity": "high",
                        "code": "evidence_failed",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Evidence {evidence_id} failed verification.",
                    }
                )
                check_issues.append("evidence_failed")
            elif status == "unverified":
                issues.append(
                    {
                        "severity": "medium",
                        "code": "evidence_unverified",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Evidence {evidence_id} is unverified.",
                    }
                )
                check_issues.append("evidence_unverified")
            elif status == "partial":
                issues.append(
                    {
                        "severity": "medium",
                        "code": "evidence_partial",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Evidence {evidence_id} is only partially verified.",
                    }
                )
                check_issues.append("evidence_partial")
            if require_source_material and source and not registered:
                issues.append(
                    {
                        "severity": "medium",
                        "code": "unregistered_source",
                        "claim_id": claim_id,
                        "evidence_id": evidence_id,
                        "text": f"Evidence {evidence_id} source is not registered as a project material.",
                    }
                )
                check_issues.append("unregistered_source")
            evidence_checks.append(
                {
                    "evidence_id": evidence_id,
                    "exists": True,
                    "kind": record.get("kind"),
                    "source": source,
                    "locator": locator,
                    "status": status,
                    "source_registered": registered,
                    "issues": check_issues,
                }
            )
        verdict = claim_verdict_from_issues(evidence_checks, issues)
        for issue in issues:
            all_issues.append(issue)
        claim_reports.append(
            {
                "claim_id": claim_id,
                "text": claim.get("text"),
                "status": claim.get("status"),
                "stage": claim.get("stage"),
                "verdict": verdict,
                "evidence_ids": evidence_ids,
                "evidence_checks": evidence_checks,
                "issues": issues,
            }
        )

    summary = {"verified": 0, "partial": 0, "unsupported": 0, "failed": 0}
    for item in claim_reports:
        verdict = item.get("verdict")
        if verdict in summary:
            summary[verdict] += 1
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for issue in all_issues:
        severity = str(issue.get("severity") or "medium")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "project_root": psafe(cwd),
        "stage": state.get("current_stage", "INTAKE"),
        "claim_count": len(claim_reports),
        "evidence_count": len(evidence_records),
        "require_source_material": require_source_material,
        "summary": summary,
        "severity_counts": severity_counts,
        "issues": all_issues,
        "claims": claim_reports,
    }


def claim_evidence_markdown(report: dict[str, Any]) -> list[str]:
    lines = [
        "# Claim Evidence Verification Report",
        "",
        f"- Created at UTC: {report['timestamp']}",
        f"- Project root: {report['project_root']}",
        f"- Stage: {report['stage']}",
        f"- Claims checked: {report['claim_count']}",
        f"- Evidence records: {report['evidence_count']}",
        f"- Issues: {len(report['issues'])}",
        "",
        "## Summary",
        "",
    ]
    summary = report.get("summary") or {}
    for verdict in ["verified", "partial", "unsupported", "failed"]:
        lines.append(f"- {verdict}: {summary.get(verdict, 0)}")
    if report.get("issues"):
        lines.extend(["", "## Issues", ""])
        for issue in report["issues"]:
            evidence_suffix = f" evidence={issue.get('evidence_id')}" if issue.get("evidence_id") else ""
            lines.append(f"- [{issue.get('severity')}] `{issue.get('code')}` claim={issue.get('claim_id')}{evidence_suffix}: {issue.get('text')}")
    lines.extend(["", "## Claims", ""])
    if not report.get("claims"):
        lines.append("- No active claims recorded.")
    for claim in report.get("claims") or []:
        lines.append(f"- `{claim.get('claim_id')}` {claim.get('verdict')}: {claim.get('text')}")
        for check in claim.get("evidence_checks") or []:
            if check.get("exists"):
                locator = check.get("locator") or "(missing locator)"
                source = check.get("source") or "(missing source)"
                issues = ", ".join(check.get("issues") or []) or "none"
                lines.append(f"  - `{check.get('evidence_id')}` status={check.get('status')} locator={locator} source={source} issues={issues}")
            else:
                lines.append(f"  - `{check.get('evidence_id')}` missing evidence record")
    return lines


def write_claim_evidence_report(cwd: Path, report: dict[str, Any], output_format: str) -> Path:
    suffix = "json" if output_format == "json" else "md"
    path = reports_root(cwd) / f"{timestamp()}-claim-evidence-report.{suffix}"
    if output_format == "json":
        write_json(path, report)
    else:
        write_lines(path, claim_evidence_markdown(report))
    append_jsonl(
        artifacts_path(cwd),
        {
            "timestamp": utc_now(),
            "type": "claim_evidence_report",
            "path": psafe(path),
            "claim_count": report.get("claim_count"),
            "issue_count": len(report.get("issues") or []),
        },
    )
    return path


def claim_evidence_validate_issues(report: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for issue in report.get("issues") or []:
        severity = str(issue.get("severity") or "medium")
        text = str(issue.get("text") or issue.get("code") or "Claim evidence verification issue.")
        claim_id = issue.get("claim_id")
        evidence_id = issue.get("evidence_id")
        prefix = f"Claim evidence issue"
        if claim_id:
            prefix += f" claim={claim_id}"
        if evidence_id:
            prefix += f" evidence={evidence_id}"
        issues.append({"severity": severity, "text": f"{prefix}: {text}"})
    return issues


def strict_requires_source_material(passport: dict[str, Any], explicit_flag: bool = False) -> bool:
    profile = passport.get("profile") or {}
    return bool(explicit_flag or profile.get("verification_strictness") == "strict")


def command_claim_evidence(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    require_source_material = strict_requires_source_material(passport, args.require_source_material)
    report = claim_evidence_report(cwd, state, passport, require_source_material=require_source_material)
    if args.write:
        path = write_claim_evidence_report(cwd, report, args.format)
        print(f"Claim evidence report: {path}")
    else:
        if args.format == "json":
            print(json.dumps(report, indent=2, ensure_ascii=True, default=str))
        else:
            print("\n".join(claim_evidence_markdown(report)).rstrip() + "\n")
    if args.fail_on_issue and report.get("issues"):
        return 1
    return 0


def command_validate(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    issues: list[dict[str, str]] = []
    require_source_material = strict_requires_source_material(passport, getattr(args, "require_source_material", False))

    if state.get("current_stage") not in STAGES:
        issues.append({"severity": "high", "text": "Current stage is invalid."})
    for ledger_path in [evidence_path(cwd), decisions_path(cwd), artifacts_path(cwd), lifecycle_path(cwd)]:
        _records, jsonl_errors = read_jsonl_with_errors(ledger_path)
        for error in jsonl_errors:
            issues.append(
                {
                    "severity": "high",
                    "text": f"JSONL ledger has invalid record: {error.get('path')}:{error.get('line')} {error.get('error')}",
                }
            )
    for storage_issue in storage_policy_issues(cwd, load_storage_policy(cwd)):
        if storage_issue.get("severity") in {"medium", "high", "blocking"}:
            issues.append({"severity": storage_issue.get("severity", "medium"), "text": f"Storage policy issue: {storage_issue.get('text')}"})
    if not passport.get("research_question") and state.get("current_stage") not in {"INTAKE", "SCOPING"}:
        issues.append({"severity": "medium", "text": "No active research question is recorded."})
    for material in passport.get("materials") or []:
        path = material.get("path")
        if path and material.get("status") == "available" and not Path(path).exists():
            issues.append({"severity": "medium", "text": f"Material path is missing: {path}"})
    evidence_records = list(current_evidence_records(cwd).values())
    evidence_ids = {record.get("id") for record in evidence_records}
    claim_evidence_payload: dict[str, Any] | None = None
    if getattr(args, "skip_claim_evidence", False):
        for claim in passport.get("key_claims") or []:
            ids = claim.get("evidence_ids") or []
            if claim.get("status") in {"supported", "contested"} and not ids:
                issues.append({"severity": "high", "text": f"Claim has status {claim.get('status')} but no evidence ids: {claim.get('id')}"})
            for evidence_id in ids:
                if evidence_id not in evidence_ids:
                    issues.append({"severity": "medium", "text": f"Claim references missing evidence id: {evidence_id}"})
        if any(record.get("status") == "failed" for record in evidence_records):
            issues.append({"severity": "high", "text": "At least one evidence record has failed verification."})
    else:
        claim_evidence_payload = claim_evidence_report(
            cwd,
            state,
            passport,
            require_source_material=require_source_material,
        )
        issues.extend(claim_evidence_validate_issues(claim_evidence_payload))
    open_flags = [flag for flag in passport.get("integrity_flags") or [] if flag.get("status") == "open"]
    for flag in open_flags:
        issues.append({"severity": flag.get("severity", "medium"), "text": f"Open integrity flag: {flag.get('text')}"})

    report_id = f"{timestamp()}-integrity-report"
    report_path = reports_root(cwd) / f"{report_id}.md"
    lines = [
        "# Research Loop Integrity Report",
        "",
        f"- Created at UTC: {utc_now()}",
        f"- Project root: {cwd}",
        f"- Stage: {state.get('current_stage')}",
        f"- Issues: {len(issues)}",
        "",
    ]
    if issues:
        lines.extend(["## Issues", ""])
        for issue in issues:
            lines.append(f"- [{issue['severity']}] {issue['text']}")
    else:
        lines.extend(["## Issues", "", "- No structural integrity issues found."])
    if claim_evidence_payload is not None:
        summary = claim_evidence_payload.get("summary") or {}
        lines.extend(
            [
                "",
                "## Claim Evidence Summary",
                "",
                f"- Claims checked: {claim_evidence_payload.get('claim_count')}",
                f"- Claim evidence issues: {len(claim_evidence_payload.get('issues') or [])}",
                f"- Verified: {summary.get('verified', 0)}",
                f"- Partial: {summary.get('partial', 0)}",
                f"- Unsupported: {summary.get('unsupported', 0)}",
                f"- Failed: {summary.get('failed', 0)}",
            ]
        )
    write_lines(report_path, lines)
    print(f"Integrity report: {report_path}")
    if issues and args.fail_on_issue:
        return 1
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd, args.stage)
    state = load_state(cwd)
    note = args.note or ""
    stamp = timestamp()
    checkpoint_id = f"{stamp}-{slug(args.name or state.get('current_stage', 'checkpoint'), 'checkpoint')}"
    md_path = checkpoints_root(cwd) / f"{checkpoint_id}.md"
    json_path = checkpoints_root(cwd) / f"{checkpoint_id}.json"
    record = {
        "schema_version": SCHEMA_VERSION,
        "id": checkpoint_id,
        "created_at": utc_now(),
        "stage": state.get("current_stage", "INTAKE"),
        "note": note,
        "git": git_info(cwd),
    }
    write_json(json_path, record)
    write_lines(
        md_path,
        [
            "# Research Loop Checkpoint",
            "",
            f"- ID: {checkpoint_id}",
            f"- Created at UTC: {record['created_at']}",
            f"- Stage: {record['stage']}",
            f"- Working directory: {cwd}",
            "",
            "## Note",
            "",
            note or "(No note provided.)",
        ],
    )
    state["latest_checkpoint"] = psafe(md_path)
    state["counters"]["checkpoints"] = int(state["counters"].get("checkpoints", 0)) + 1
    save_state(cwd, state)
    passport = load_passport(cwd, state)
    passport["stage"] = state.get("current_stage", "INTAKE")
    passport["latest_checkpoint"] = psafe(md_path)
    if args.research_question:
        passport["research_question"] = args.research_question
        question_id = record_id("rq", args.research_question)
        update_list_item(
            passport["research_questions"],
            {
                "id": question_id,
                "text": args.research_question,
                "status": "active",
                "stage": state.get("current_stage", "INTAKE"),
                "created_at": utc_now(),
            },
        )
        passport["active_question_id"] = question_id
    if args.summary:
        passport["project_summary"] = args.summary
    save_passport(cwd, passport)
    append_jsonl(decisions_path(cwd), {"timestamp": utc_now(), "type": "checkpoint", "path": psafe(md_path), "note": note})
    print(f"Checkpoint: {md_path}")
    return 0


def command_handoff(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    state = load_state(cwd)
    passport = load_passport(cwd, state)
    stamp = timestamp()
    handoff_id = f"{stamp}-{slug(args.name or 'handoff', 'handoff')}"
    path = handoffs_root(cwd) / f"{handoff_id}.md"
    latest_runs = sorted(runs_root(cwd).glob("*"), reverse=True)[:5]
    lines = [
        "# Research Loop Handoff",
        "",
        f"- Created at UTC: {utc_now()}",
        f"- Project root: {cwd}",
        f"- Project id: {state.get('project_id')}",
        f"- Current stage: {state.get('current_stage')}",
        f"- Latest checkpoint: {state.get('latest_checkpoint') or '(none)'}",
        "",
        "## Project Summary",
        "",
        passport.get("project_summary") or "(Not set.)",
        "",
        "## Research Question",
        "",
        passport.get("research_question") or "(Not set.)",
        "",
        "## Materials",
        "",
    ]
    materials = passport.get("materials") or []
    if materials:
        for item in materials[:20]:
            label = item.get("title") or item.get("path") or item.get("source") or item.get("id")
            lines.append(f"- [{item.get('kind')}] {label} ({item.get('status')})")
    else:
        lines.append("- (None recorded.)")
    lines.extend(
        [
            "",
            "## Key Claims",
            "",
        ]
    )
    claims = passport.get("key_claims") or []
    if claims:
        for item in claims[:20]:
            lines.append(f"- [{item.get('status')}] {item.get('text')} ({item.get('id')})")
    else:
        lines.append("- (None recorded.)")
    lines.extend(
        [
            "",
            "## Risks",
            "",
        ]
    )
    risks = passport.get("risks") or []
    open_risks = [item for item in risks if item.get("status") == "open"]
    if open_risks:
        for item in open_risks[:20]:
            lines.append(f"- [{item.get('severity')}] {item.get('text')} ({item.get('id')})")
    else:
        lines.append("- (No open risks recorded.)")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )
    next_actions = [item for item in passport.get("next_actions") or [] if item.get("status") in {"todo", "in-progress", "blocked"}]
    if next_actions:
        for item in next_actions[:20]:
            lines.append(f"- [{item.get('status')}] {item.get('text')} ({item.get('stage')})")
    else:
        lines.append("- (None recorded.)")
    lines.extend(
        [
            "",
            "## Open Questions",
            "",
        ]
    )
    open_questions = passport.get("open_questions") or []
    if open_questions:
        for item in open_questions[:20]:
            if isinstance(item, dict):
                lines.append(f"- [{item.get('status')}] {item.get('text')} ({item.get('id')})")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("- (None recorded.)")
    lines.extend(["", "## Recent Runs", ""])
    if latest_runs:
        for run in latest_runs:
            summary = run / "summary.md"
            lines.append(f"- {run.name}: {summary if summary.exists() else '(summary missing)'}")
    else:
        lines.append("- (No runs recorded.)")
    lines.extend(
        [
            "",
            "## Resume Instructions",
            "",
            "1. Open a new Codex thread in this project directory.",
            "2. Ask: `resume the research loop from the latest handoff`.",
            "3. Read `.research-loop/material-passport.json`, this handoff, and the latest checkpoint before making changes.",
        ]
    )
    if args.note:
        lines.extend(["", "## Handoff Note", "", args.note])
    write_lines(path, lines)
    state["latest_handoff"] = psafe(path)
    state["counters"]["handoffs"] = int(state["counters"].get("handoffs", 0)) + 1
    save_state(cwd, state)
    passport["latest_handoff"] = psafe(path)
    save_passport(cwd, passport)
    print(f"Handoff: {path}")
    return 0


def command_run(args: argparse.Namespace) -> int:
    cwd = resolve_workspace(args.cwd)
    init_project(cwd)
    command_parts = list(args.command)
    if command_parts and command_parts[0] == "--":
        command_parts = command_parts[1:]
    command = " ".join(command_parts).strip()
    if not command:
        print("No command provided. Use: research_loop.py run -- <command>", file=sys.stderr)
        return 2
    name = slug(args.name or command.split()[0], "run")
    run_dir = runs_root(cwd) / f"{timestamp()}-{name}"
    ensure_dir(run_dir)
    before = {"created_at": utc_now(), "working_directory": psafe(cwd), "inventory": inventory(cwd), "git": git_info(cwd)}
    write_json(run_dir / "pre-snapshot.json", before)
    started = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    (run_dir / "stdout.log").write_text(proc.stdout or "", encoding="utf-8")
    (run_dir / "stderr.log").write_text(proc.stderr or "", encoding="utf-8")
    after = {"captured_at": utc_now(), "inventory": inventory(cwd), "git": git_info(cwd)}
    write_json(run_dir / "post-state.json", after)
    changes = compare_inventory(before["inventory"], after["inventory"])
    lines = [
        "# Research Loop Command Run",
        "",
        f"- Command: `{command}`",
        f"- Exit code: {proc.returncode}",
        f"- Elapsed seconds: {elapsed:.2f}",
        f"- Working directory: {cwd}",
        f"- Added files: {len(changes['added'])}",
        f"- Changed files: {len(changes['changed'])}",
        f"- Removed files: {len(changes['removed'])}",
        "",
        "## Logs",
        "",
        "- stdout: stdout.log",
        "- stderr: stderr.log",
    ]
    write_lines(run_dir / "summary.md", lines)
    if proc.returncode != 0:
        write_lines(
            run_dir / "failure.md",
            [
                "# Research Loop Command Failure",
                "",
                f"- Command: `{command}`",
                f"- Exit code: {proc.returncode}",
                f"- Working directory: {cwd}",
                "",
                "Check `stderr.log` and `stdout.log` in this run directory.",
            ],
        )
    state = load_state(cwd)
    state["active_run_id"] = run_dir.name
    state["counters"]["runs"] = int(state["counters"].get("runs", 0)) + 1
    if proc.returncode != 0:
        state["counters"]["failures"] = int(state["counters"].get("failures", 0)) + 1
    save_state(cwd, state)
    append_jsonl(
        artifacts_path(cwd),
        {
            "timestamp": utc_now(),
            "type": "command_run",
            "command": command,
            "exit_code": proc.returncode,
            "run_directory": psafe(run_dir),
        },
    )
    passport = load_passport(cwd, state)
    update_list_item(
        passport["experiments"],
        {
            "id": run_dir.name,
            "kind": "command_run",
            "command": command,
            "exit_code": proc.returncode,
            "status": "passed" if proc.returncode == 0 else "failed",
            "run_directory": psafe(run_dir),
            "created_at": utc_now(),
        },
    )
    save_passport(cwd, passport)
    print(f"Run: {run_dir}")
    print(f"Summary: {run_dir / 'summary.md'}")
    return proc.returncode


def lifecycle_main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    event = argv[0] if argv else "Unknown"
    data = read_stdin_json()
    cwd = resolve_cwd_from_payload(data)
    key = session_key(data, cwd)
    try:
        if event.lower() == "sessionstart":
            create_pre_snapshot(cwd, key, event, data)
        elif event.lower() == "posttooluse":
            post_tool_use(cwd, key, event, data)
        elif event.lower() == "stop":
            stop_summary(cwd, key, event, data)
        else:
            init_project(cwd)
            append_lifecycle(cwd, event, data, {"session_key": key})
    except Exception as exc:
        fallback = Path.home() / ".codex" / "hooks" / "codex-research-loop" / "errors.log"
        ensure_dir(fallback.parent)
        with fallback.open("a", encoding="utf-8") as handle:
            handle.write(f"{utc_now()} {event} {cwd} {exc!r}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex Research Loop runtime")
    parser.add_argument("--cwd", help="Project directory. Defaults to current directory.")
    sub = parser.add_subparsers(dest="command_name", required=True)

    p_init = sub.add_parser("init", help="Initialize .research-loop in a project.")
    p_init.add_argument("--stage", help=f"Initial stage. Allowed: {', '.join(STAGES)}")
    p_init.add_argument("--storage-style", choices=["adaptive", "canonical", "minimal", "loop-local"], default=None, help="Storage policy style for new or rebuilt project layouts.")
    p_init.add_argument("--init-storage", action="store_true", help="Create the project-facing storage directories from the storage policy.")
    p_init.set_defaults(func=command_init)

    p_status = sub.add_parser("status", help="Print current research loop status.")
    p_status.set_defaults(func=command_status)

    p_storage = sub.add_parser("storage", help="Show, create, or rebuild the project storage policy.")
    p_storage.add_argument("--style", choices=["adaptive", "canonical", "minimal", "loop-local"], default=None, help="Storage style to use when creating or rebuilding the policy.")
    p_storage.add_argument("--rebuild", action="store_true", help="Rebuild storage-policy.json from the selected style, preserving no custom bucket overrides.")
    p_storage.add_argument("--init-dirs", action="store_true", help="Create storage directories declared by the policy.")
    p_storage.add_argument("--include-optional", action="store_true", help="Also create optional buckets such as src/code.")
    p_storage.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output storage policy format.")
    p_storage.add_argument("--write", action="store_true", help="Write a storage policy report under .research-loop/storage-reports.")
    p_storage.set_defaults(func=command_storage)

    p_passport = sub.add_parser("passport", help="Update high-level research passport fields.")
    p_passport.add_argument("--stage", help=f"Set current stage. Allowed: {', '.join(STAGES)}")
    p_passport.add_argument("--title", help="Project title.")
    p_passport.add_argument("--domain", help="Research domain or field.")
    p_passport.add_argument("--summary", help="Project summary.")
    p_passport.add_argument("--question", help="Set and record the active research question.")
    p_passport.add_argument("--target", action="append", help="Output target, e.g. paper, figure, patent, report.")
    p_passport.set_defaults(func=command_passport)

    p_profile = sub.add_parser("profile", help="Update project profile settings used by routing and validation.")
    p_profile.add_argument("--target-venue", help="Target journal, conference, funder, venue, or outlet.")
    p_profile.add_argument("--citation-style", help="Citation style, e.g. Nature, APA, IEEE, Chicago.")
    p_profile.add_argument("--preferred-language", help="Preferred output language.")
    p_profile.add_argument("--data-sensitivity", help="normal, sensitive, or restricted.")
    p_profile.add_argument("--verification-strictness", help="quick, standard, or strict.")
    p_profile.add_argument("--route-mode", help="quick, standard, or strict.")
    p_profile.set_defaults(func=command_profile)

    p_question = sub.add_parser("question", help="Record a research or open question.")
    p_question.add_argument("--text", required=True, help="Question text.")
    p_question.add_argument("--kind", choices=["research", "open"], default="open", help="Question kind.")
    p_question.add_argument("--status", default="open", help="open, active, answered, or dropped.")
    p_question.add_argument("--stage", help=f"Set current stage. Allowed: {', '.join(STAGES)}")
    p_question.add_argument("--note", help="Optional note.")
    p_question.set_defaults(func=command_question)

    p_material = sub.add_parser("material", help="Record a research material or artifact.")
    p_material.add_argument("--kind", required=True, help="Material kind, e.g. paper, dataset, code, figure, draft.")
    p_material.add_argument("--title", help="Material title.")
    p_material.add_argument("--path", help="Local path, relative to the project root or absolute.")
    p_material.add_argument("--source", help="External source URL, DOI, dataset id, or repository.")
    p_material.add_argument("--status", default="available", help="available, missing, external, or derived.")
    p_material.add_argument("--note", help="Optional note.")
    p_material.set_defaults(func=command_material)

    p_claim = sub.add_parser("claim", help="Record a key research claim.")
    p_claim.add_argument("--text", required=True, help="Claim text.")
    p_claim.add_argument("--status", default="proposed", help="proposed, supported, contested, unverified, or retracted.")
    p_claim.add_argument("--stage", help=f"Set current stage. Allowed: {', '.join(STAGES)}")
    p_claim.add_argument("--evidence-id", action="append", help="Existing evidence id supporting or contesting this claim.")
    p_claim.add_argument("--note", help="Optional note.")
    p_claim.set_defaults(func=command_claim)

    p_evidence = sub.add_parser("evidence", help="Record evidence for a claim or project fact.")
    p_evidence.add_argument("--kind", required=True, help="Evidence kind, e.g. citation, experiment, dataset, analysis.")
    p_evidence.add_argument("--source", required=True, help="Evidence source, e.g. DOI, file path, command run, URL.")
    p_evidence.add_argument("--locator", help="Precise locator, e.g. page, section, table, run id.")
    p_evidence.add_argument("--claim-id", help="Claim id this evidence supports or contests.")
    p_evidence.add_argument("--status", default="unverified", help="verified, partial, unverified, or failed.")
    p_evidence.add_argument("--note", help="Optional note.")
    p_evidence.set_defaults(func=command_evidence)

    p_decision = sub.add_parser("decision", help="Record a research decision and rationale.")
    p_decision.add_argument("--decision", required=True, help="Decision text.")
    p_decision.add_argument("--rationale", help="Rationale.")
    p_decision.add_argument("--alternatives", help="Semicolon-separated alternatives considered.")
    p_decision.add_argument("--status", default="active", help="active, superseded, rejected, or deferred.")
    p_decision.add_argument("--stage", help=f"Set current stage. Allowed: {', '.join(STAGES)}")
    p_decision.set_defaults(func=command_decision)

    p_risk = sub.add_parser("risk", help="Record a research risk or integrity concern.")
    p_risk.add_argument("--text", required=True, help="Risk text.")
    p_risk.add_argument("--severity", default="medium", help="low, medium, high, or blocking.")
    p_risk.add_argument("--status", default="open", help="open, mitigated, accepted, or closed.")
    p_risk.add_argument("--mitigation", help="Mitigation plan.")
    p_risk.set_defaults(func=command_risk)

    p_next = sub.add_parser("next", help="Record a next action.")
    p_next.add_argument("--text", required=True, help="Action text.")
    p_next.add_argument("--stage", help=f"Set current stage. Allowed: {', '.join(STAGES)}")
    p_next.add_argument("--status", default="todo", help="todo, in-progress, done, or blocked.")
    p_next.add_argument("--owner", help="Owner or role.")
    p_next.set_defaults(func=command_next)

    p_update = sub.add_parser("update", help="Update or close an existing research loop record.")
    p_update.add_argument("--kind", required=True, choices=["claim", "risk", "next", "question", "material", "evidence", "decision"], help="Record kind to update.")
    p_update.add_argument("--id", required=True, help="Record id to update.")
    p_update.add_argument("--status", help="New status.")
    p_update.add_argument("--text", help="New or revised text.")
    p_update.add_argument("--note", help="Update note.")
    p_update.add_argument("--severity", help="Risk severity.")
    p_update.add_argument("--mitigation", help="Risk mitigation.")
    p_update.add_argument("--stage", help=f"Stage. Allowed: {', '.join(STAGES)}")
    p_update.add_argument("--title", help="Material title.")
    p_update.add_argument("--source", help="Source URL, DOI, path, or identifier.")
    p_update.add_argument("--path", help="Material path.")
    p_update.add_argument("--locator", help="Evidence locator.")
    p_update.add_argument("--evidence-id", action="append", help="Claim evidence id; can be repeated.")
    p_update.set_defaults(func=command_update)

    p_normalize = sub.add_parser("normalize", help="Convert rough natural-language input into a project-grounded downstream prompt.")
    p_normalize.add_argument("--stage", help=f"Set current stage before normalization. Allowed: {', '.join(STAGES)}")
    p_normalize.add_argument("--input", required=True, help="Raw user request or messy natural-language task.")
    p_normalize.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output normalized prompt format.")
    p_normalize.add_argument("--write", action="store_true", help="Write the normalized prompt under .research-loop/reports.")
    p_normalize.set_defaults(func=command_normalize)

    p_route = sub.add_parser("route", help="Recommend domain skills and gates for the current research stage.")
    p_route.add_argument("--stage", help=f"Set current stage before routing. Allowed: {', '.join(STAGES)}")
    p_route.add_argument("--intent", help="Optional user intent or immediate task.")
    p_route.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output route plan format.")
    p_route.add_argument("--write", action="store_true", help="Write the route plan under .research-loop/reports.")
    p_route.set_defaults(func=command_route)

    p_deep_loop = sub.add_parser("deep-loop", help="Evaluate a subchain gate, run review routing semantics, and produce the next deep-loop directive.")
    p_deep_loop.add_argument("--stage", help=f"Set current stage before evaluating the gate. Allowed: {', '.join(STAGES)}")
    p_deep_loop.add_argument("--intent", help="Current user goal or task intent used for route graph construction.")
    p_deep_loop.add_argument("--loop-id", help="Optional stable loop id. Defaults to a timestamped id.")
    p_deep_loop.add_argument("--current-subchain", choices=sorted(DEEP_LOOP_SUBCHAIN_BY_ID), help="Current subchain id, e.g. P2 or P7. Defaults to the route-selected first subchain.")
    p_deep_loop.add_argument("--next-subchain", action="append", choices=sorted(DEEP_LOOP_SUBCHAIN_BY_ID), help="Force a next subchain when the gate passes. Repeat for alternatives.")
    p_deep_loop.add_argument("--gate-result", choices=["auto", "pass", "fail", "block", "human"], default="auto", help="Observed gate result. auto derives from route blockers, supplied issues, and quality score.")
    p_deep_loop.add_argument("--quality-score", type=float, help="Optional gate quality score. Use 0-1 or 0-100.")
    p_deep_loop.add_argument("--pass-threshold", type=float, help="Optional pass threshold. Use 0-1 or 0-100; defaults from depth/profile.")
    p_deep_loop.add_argument("--gate-issue", action="append", help="Gate issue, failed criterion, or blocker observed in this round. Repeat for multiple issues.")
    p_deep_loop.add_argument("--result-summary", help="Short summary of what this subchain round produced.")
    p_deep_loop.add_argument("--artifact", action="append", help="Artifact path or id produced by the current round. Repeat for multiple artifacts.")
    p_deep_loop.add_argument("--harness-report", action="append", help="Structured JSON harness/test report to parse as gate evidence. Repeat for multiple reports.")
    p_deep_loop.add_argument("--round-index", type=int, help="Explicit round index for this subchain. Defaults from previous deep-loop records.")
    p_deep_loop.add_argument("--max-rounds", type=int, help="Maximum retry rounds for this subchain before escalation. Defaults from depth.")
    p_deep_loop.add_argument("--skip-research-council", action="store_true", help="Disable the supplemental research-council review for this gate. Default is enabled.")
    p_deep_loop.add_argument("--skip-adversarial-gate", action="store_true", help="Disable the supplemental adversarial gate review for this gate. Default is enabled.")
    p_deep_loop.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output deep-loop directive format.")
    p_deep_loop.add_argument("--write", action="store_true", help="Write the deep-loop directive under .research-loop/deep-loops and record a next action.")
    p_deep_loop.set_defaults(func=command_deep_loop)

    p_capabilities = sub.add_parser("capabilities", help="Print the research loop capability matrix and missing tool gaps.")
    p_capabilities.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output capability matrix format.")
    p_capabilities.set_defaults(func=command_capabilities)

    p_source_hub = sub.add_parser("source-hub", help="Query public scholarly metadata providers through the research source hub.")
    p_source_hub.add_argument("--query", required=True, help="Search query, DOI, title, or arXiv id.")
    p_source_hub.add_argument("--provider", choices=["auto", "crossref", "openalex", "arxiv"], default="auto", help="Metadata provider to query.")
    p_source_hub.add_argument("--rows", type=int, default=3, help="Results per provider, 1-10.")
    p_source_hub.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output source-hub format.")
    p_source_hub.add_argument("--write", action="store_true", help="Write source-hub results under .research-loop/reports.")
    p_source_hub.add_argument("--record-materials", action="store_true", help="Record returned metadata as source-metadata materials.")
    p_source_hub.set_defaults(func=command_source_hub)

    p_content_ingest = sub.add_parser("content-ingest", help="Fetch or import explicit articles, datasets, and files into research-loop packages.")
    p_content_ingest.add_argument("--source", action="append", required=True, help="URL or local file path. Repeat for multiple sources.")
    p_content_ingest.add_argument("--mode", choices=["auto", "article", "data", "file"], default="auto", help="Force a content family or infer automatically.")
    p_content_ingest.add_argument("--max-bytes", type=int, default=10485760, help="Maximum bytes per source. Defaults to 10 MiB.")
    p_content_ingest.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output content-ingest report format.")
    p_content_ingest.add_argument("--write", action="store_true", help="Write the content-ingest report under .research-loop/reports.")
    p_content_ingest.add_argument("--record-materials", action="store_true", help="Record imported articles/datasets/files as project materials.")
    p_content_ingest.add_argument("--wiki-root", help="Optional llm-wiki root where source pages and inbox hubs should be written.")
    p_content_ingest.add_argument("--write-wiki", action="store_true", help="Write llm-wiki-compatible source pages for imported items.")
    p_content_ingest.set_defaults(func=command_content_ingest)

    p_problem_loop = sub.add_parser("problem-loop", help="Analyze project blockers through an isolated lab, expert panel, tests, and promotion gate.")
    p_problem_loop.add_argument("--problem", required=True, help="Problem, blocker, failure, or obstacle to diagnose.")
    p_problem_loop.add_argument("--case-id", help="Optional stable case id. Defaults to timestamp plus problem digest.")
    p_problem_loop.add_argument("--repro-command", action="append", help="Reproduction command expected to fail before repair. A non-zero exit code counts as reproduced evidence, not a gate failure.")
    p_problem_loop.add_argument("--test-command", action="append", help="Validation command expected to pass from the project root, with logs captured in the isolated lab.")
    p_problem_loop.add_argument("--promote-threshold", type=float, default=0.75, help="Minimum gate score needed before promotion is allowed.")
    p_problem_loop.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output problem-loop report format.")
    p_problem_loop.add_argument("--write", action="store_true", help="Write a problem-loop report under .research-loop/problem-reports.")
    p_problem_loop.set_defaults(func=command_problem_loop)

    p_problem_promote = sub.add_parser("problem-promote", help="Promote an approved isolated problem-loop case into the main research loop.")
    p_problem_promote.add_argument("--case-id", required=True, help="Problem-loop case id.")
    p_problem_promote.add_argument("--force", action="store_true", help="Promote even when the gate is not approved; records that the promotion was forced.")
    p_problem_promote.add_argument("--note", help="Optional promotion note or human approval rationale.")
    p_problem_promote.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output promotion format.")
    p_problem_promote.set_defaults(func=command_problem_promote)

    p_zotero = sub.add_parser("zotero-bridge", help="Export recorded source metadata into Zotero-compatible plans, BibTeX, CSL-JSON, attachments, dedupe, and wiki pages.")
    p_zotero.add_argument("--collection", default="Project Literature", help="Target Zotero collection name.")
    p_zotero.add_argument("--format", choices=["plan", "csl-json", "bibtex", "all"], default="plan", help="Export payload to print/write.")
    p_zotero.add_argument("--wiki-root", help="Optional llm-wiki root where sources/ and topics/ pages should be written.")
    p_zotero.add_argument("--write", action="store_true", help="Write Zotero bridge artifacts under .research-loop/zotero and .research-loop/reports.")
    p_zotero.add_argument("--write-wiki", action="store_true", help="Write llm-wiki-compatible paper pages and a Zotero library hub.")
    p_zotero.add_argument("--include-attachments", action="store_true", help="Plan local or remote PDF attachments for exported items.")
    p_zotero.add_argument("--no-dedupe", action="store_true", help="Disable DOI/title deduplication.")
    p_zotero.set_defaults(func=command_zotero_bridge)

    p_auto_loop = sub.add_parser("auto-loop", help="Run validation/test/repair rounds until gates pass or a safety limit is reached.")
    p_auto_loop.add_argument("--goal", required=True, help="Completion goal for this unattended loop.")
    p_auto_loop.add_argument("--test-command", action="append", help="Shell test command. Repeat for multiple gates.")
    p_auto_loop.add_argument("--repair-command", action="append", help="Shell repair command to run after a failed gate. Repeat for multiple repairs.")
    p_auto_loop.add_argument("--max-rounds", type=int, default=5, help="Maximum loop rounds unless --allow-unbounded is set.")
    p_auto_loop.add_argument("--max-minutes", type=float, default=0.0, help="Optional wall-clock limit in minutes. 0 means no time limit.")
    p_auto_loop.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output report format.")
    p_auto_loop.add_argument("--skip-validate", action="store_true", help="Skip research-loop structural validation as a test gate.")
    p_auto_loop.add_argument("--allow-unbounded", action="store_true", help="Allow an unbounded round count. Requires a repair command or max-minutes.")
    p_auto_loop.add_argument("--skip-deep-loop", action="store_true", help="Disable per-round deep-loop gate dispatch.")
    p_auto_loop.add_argument("--deep-loop-intent", help="Optional intent prompt used by deep-loop. Defaults to --goal.")
    p_auto_loop.add_argument("--current-subchain", choices=sorted(DEEP_LOOP_SUBCHAIN_BY_ID), help="Current P1-P10 subchain for deep-loop dispatch.")
    p_auto_loop.add_argument("--next-subchain", action="append", choices=sorted(DEEP_LOOP_SUBCHAIN_BY_ID), help="Force a next P1-P10 subchain when the deep-loop gate passes.")
    p_auto_loop.add_argument("--auto-route-next", action="store_true", default=True, help="Automatically consume route_next by starting the next subchain inside this auto-loop. Enabled by default.")
    p_auto_loop.add_argument("--no-auto-route-next", action="store_false", dest="auto_route_next", help="Disable automatic route_next consumption and stop after writing the handoff.")
    p_auto_loop.add_argument("--route-depth-budget", type=int, default=3, help="Maximum automatic route_next transitions when auto-routing is enabled.")
    p_auto_loop.add_argument("--allow-unbounded-routes", action="store_true", help="Allow unlimited automatic route_next transitions. Use with explicit time, round, or external supervision limits for long unattended runs.")
    p_auto_loop.add_argument("--route-agent", choices=sorted(ROUTE_AGENT_CHOICES), default="codex", help="Built-in route_next executor to run at the start of auto-routed subchains. Defaults to codex for unattended continuation.")
    p_auto_loop.add_argument(
        "--route-agent-command",
        action="append",
        help="Shell command template to execute at the start of an auto-routed subchain. Variables: {cwd}, {subchain}, {goal}, {prompt}, {prompt_file}, {round}. Repeat for multiple commands.",
    )
    p_auto_loop.add_argument("--route-codex-path", help="Explicit Codex CLI executable path for --route-agent codex. Defaults to auto-discovery.")
    p_auto_loop.add_argument("--route-codex-sandbox", choices=["read-only", "workspace-write", "danger-full-access"], default="workspace-write", help="Sandbox mode passed to `codex exec` for auto-routed subchains.")
    p_auto_loop.add_argument("--route-codex-approval", choices=["untrusted", "on-request", "never"], default="never", help="Approval policy passed to `codex exec` for auto-routed subchains.")
    p_auto_loop.add_argument("--route-codex-skip-git-check", action="store_true", default=True, help="Pass --skip-git-repo-check to `codex exec` (default).")
    p_auto_loop.add_argument("--route-codex-require-git", action="store_false", dest="route_codex_skip_git_check", help="Do not pass --skip-git-repo-check to `codex exec`.")
    p_auto_loop.add_argument("--route-codex-ephemeral", action="store_true", help="Pass --ephemeral to `codex exec`.")
    p_auto_loop.add_argument("--route-codex-json", action="store_true", help="Pass --json to `codex exec` and capture JSONL in executor logs.")
    p_auto_loop.add_argument("--route-codex-output", help="Pass --output-last-message to `codex exec` with this file path.")
    p_auto_loop.add_argument("--route-agent-idle-timeout", type=float, default=DEFAULT_ROUTE_AGENT_IDLE_TIMEOUT_SECONDS, help="Kill a route executor after this many seconds without stdout/stderr activity. 0 disables idle timeout.")
    p_auto_loop.add_argument("--route-agent-wall-timeout", type=float, default=DEFAULT_ROUTE_AGENT_WALL_TIMEOUT_SECONDS, help="Kill a route executor after this many wall-clock seconds. 0 disables wall timeout.")
    p_auto_loop.add_argument("--route-agent-poll-seconds", type=float, default=DEFAULT_ROUTE_AGENT_POLL_SECONDS, help="Polling interval for route executor liveness checks.")
    p_auto_loop.add_argument("--deep-loop-quality-score", type=float, help="Optional per-round quality score for deep-loop gates, 0-1 or 0-100.")
    p_auto_loop.add_argument("--deep-loop-pass-threshold", type=float, help="Optional deep-loop pass threshold, 0-1 or 0-100.")
    p_auto_loop.add_argument("--deep-loop-max-rounds", type=int, help="Override deep-loop retry budget before escalation.")
    p_auto_loop.add_argument("--harness-report", action="append", help="Structured JSON harness/test report to pass into each deep-loop gate as evidence.")
    p_auto_loop.add_argument("--skip-problem-escalation", action="store_true", help="Record escalate_problem_loop without automatically creating a problem-loop case.")
    p_auto_loop.add_argument("--problem-promote-threshold", type=float, default=0.75, help="Promotion threshold used when auto-loop escalates into problem-loop.")
    p_auto_loop.set_defaults(func=command_auto_loop)

    p_auto_loop_resume = sub.add_parser("auto-loop-resume", help="Resume an interrupted or budget-stopped auto-loop from a previous auto-loop report.")
    p_auto_loop_resume.add_argument("--report", help="Path to a previous *-auto-loop.json report.")
    p_auto_loop_resume.add_argument("--latest", action="store_true", help="Resume from the newest *-auto-loop.json under .research-loop/reports.")
    p_auto_loop_resume.add_argument("--extra-rounds", type=int, default=5, help="Additional max rounds for the resumed run.")
    p_auto_loop_resume.add_argument("--extra-route-depth", type=int, default=3, help="Additional automatic route_next transitions for the resumed run.")
    p_auto_loop_resume.add_argument("--max-minutes", type=float, default=0.0, help="Optional wall-clock limit for the resumed run.")
    p_auto_loop_resume.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output report format.")
    p_auto_loop_resume.add_argument("--test-command", action="append", help="Override test commands from the source report.")
    p_auto_loop_resume.add_argument("--repair-command", action="append", help="Override repair commands from the source report.")
    p_auto_loop_resume.add_argument("--skip-validate", action="store_true", help="Skip structural validation in the resumed run.")
    p_auto_loop_resume.add_argument("--allow-unbounded", action="store_true", help="Allow an unbounded resumed round count. Requires a repair command or max-minutes.")
    p_auto_loop_resume.add_argument("--allow-unbounded-routes", action="store_true", help="Allow unlimited automatic route_next transitions in the resumed run.")
    p_auto_loop_resume.add_argument("--no-auto-route-next", action="store_true", help="Disable automatic continuation after the resumed starting route.")
    p_auto_loop_resume.add_argument("--route-agent", choices=sorted(ROUTE_AGENT_CHOICES), help="Built-in route_next executor for the resumed run.")
    p_auto_loop_resume.add_argument("--route-agent-command", action="append", help="Override or provide route-agent command templates for the resumed run.")
    p_auto_loop_resume.add_argument("--route-codex-path", help="Explicit Codex CLI executable path for the resumed run.")
    p_auto_loop_resume.add_argument("--route-codex-sandbox", choices=["read-only", "workspace-write", "danger-full-access"], default="workspace-write", help="Sandbox mode passed to `codex exec`.")
    p_auto_loop_resume.add_argument("--route-codex-approval", choices=["untrusted", "on-request", "never"], default="never", help="Approval policy passed to `codex exec`.")
    p_auto_loop_resume.add_argument("--route-codex-require-git", action="store_true", help="Do not pass --skip-git-repo-check to `codex exec`.")
    p_auto_loop_resume.add_argument("--route-codex-ephemeral", action="store_true", help="Pass --ephemeral to `codex exec`.")
    p_auto_loop_resume.add_argument("--route-codex-json", action="store_true", help="Pass --json to `codex exec`.")
    p_auto_loop_resume.add_argument("--route-codex-output", help="Pass --output-last-message to `codex exec` with this file path.")
    p_auto_loop_resume.add_argument("--route-agent-idle-timeout", type=float, help="Override route executor idle timeout for the resumed run. 0 disables idle timeout.")
    p_auto_loop_resume.add_argument("--route-agent-wall-timeout", type=float, help="Override route executor wall timeout for the resumed run. 0 disables wall timeout.")
    p_auto_loop_resume.add_argument("--route-agent-poll-seconds", type=float, help="Override route executor liveness polling interval.")
    p_auto_loop_resume.add_argument("--deep-loop-max-rounds", type=int, help="Override deep-loop retry budget in the resumed run.")
    p_auto_loop_resume.add_argument("--harness-report", action="append", help="Structured JSON harness/test report to pass into resumed deep-loop gates as evidence.")
    p_auto_loop_resume.add_argument("--skip-problem-escalation", action="store_true", help="Do not automatically create problem-loop cases in the resumed run.")
    p_auto_loop_resume.add_argument("--problem-promote-threshold", type=float, default=0.75, help="Promotion threshold used when resumed auto-loop escalates into problem-loop.")
    p_auto_loop_resume.set_defaults(func=command_auto_loop_resume)

    p_auto_loop_watchdog = sub.add_parser("auto-loop-watchdog", help="Supervise auto-loop and auto-loop-resume so unattended runs keep advancing across resumable stops.")
    p_auto_loop_watchdog.add_argument("--goal", required=True, help="Completion goal for this supervised unattended loop.")
    p_auto_loop_watchdog.add_argument("--test-command", action="append", help="Shell test command. Repeat for multiple gates.")
    p_auto_loop_watchdog.add_argument("--repair-command", action="append", help="Shell repair command to run after a failed gate. Repeat for multiple repairs.")
    p_auto_loop_watchdog.add_argument("--max-rounds", type=int, default=5, help="Maximum loop rounds for the initial auto-loop.")
    p_auto_loop_watchdog.add_argument("--max-minutes", type=float, default=0.0, help="Optional wall-clock limit passed to child auto-loop commands.")
    p_auto_loop_watchdog.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output watchdog report format.")
    p_auto_loop_watchdog.add_argument("--skip-validate", action="store_true", help="Skip research-loop structural validation as a test gate.")
    p_auto_loop_watchdog.add_argument("--allow-unbounded", action="store_true", help="Allow unbounded child round counts with guardrails.")
    p_auto_loop_watchdog.add_argument("--skip-deep-loop", action="store_true", help="Disable per-round deep-loop gate dispatch.")
    p_auto_loop_watchdog.add_argument("--deep-loop-intent", help="Optional intent prompt used by deep-loop. Defaults to --goal.")
    p_auto_loop_watchdog.add_argument("--current-subchain", choices=sorted(DEEP_LOOP_SUBCHAIN_BY_ID), help="Current P1-P10 subchain for deep-loop dispatch.")
    p_auto_loop_watchdog.add_argument("--next-subchain", action="append", choices=sorted(DEEP_LOOP_SUBCHAIN_BY_ID), help="Force a next P1-P10 subchain when the deep-loop gate passes.")
    p_auto_loop_watchdog.add_argument("--auto-route-next", action="store_true", default=True, help="Automatically consume route_next decisions. Enabled by default.")
    p_auto_loop_watchdog.add_argument("--no-auto-route-next", action="store_false", dest="auto_route_next", help="Disable automatic route_next consumption.")
    p_auto_loop_watchdog.add_argument("--route-depth-budget", type=int, default=3, help="Maximum automatic route_next transitions for the initial auto-loop.")
    p_auto_loop_watchdog.add_argument("--allow-unbounded-routes", action="store_true", help="Allow unlimited automatic route_next transitions inside child loops.")
    p_auto_loop_watchdog.add_argument("--route-agent", choices=sorted(ROUTE_AGENT_CHOICES), default="codex", help="Built-in route_next executor for child loops.")
    p_auto_loop_watchdog.add_argument(
        "--route-agent-command",
        action="append",
        help="Shell command template to execute at the start of an auto-routed subchain. Variables: {cwd}, {subchain}, {goal}, {prompt}, {prompt_file}, {round}. Repeat for multiple commands.",
    )
    p_auto_loop_watchdog.add_argument("--route-codex-path", help="Explicit Codex CLI executable path for --route-agent codex.")
    p_auto_loop_watchdog.add_argument("--route-codex-sandbox", choices=["read-only", "workspace-write", "danger-full-access"], default="workspace-write", help="Sandbox mode passed to `codex exec`.")
    p_auto_loop_watchdog.add_argument("--route-codex-approval", choices=["untrusted", "on-request", "never"], default="never", help="Approval policy passed to `codex exec`.")
    p_auto_loop_watchdog.add_argument("--route-codex-require-git", action="store_true", help="Do not pass --skip-git-repo-check to `codex exec`.")
    p_auto_loop_watchdog.add_argument("--route-codex-ephemeral", action="store_true", help="Pass --ephemeral to `codex exec`.")
    p_auto_loop_watchdog.add_argument("--route-codex-json", action="store_true", help="Pass --json to `codex exec`.")
    p_auto_loop_watchdog.add_argument("--route-codex-output", help="Pass --output-last-message to `codex exec` with this file path.")
    p_auto_loop_watchdog.add_argument("--route-agent-idle-timeout", type=float, default=DEFAULT_ROUTE_AGENT_IDLE_TIMEOUT_SECONDS, help="Kill a route executor after this many seconds without stdout/stderr activity. 0 disables idle timeout.")
    p_auto_loop_watchdog.add_argument("--route-agent-wall-timeout", type=float, default=DEFAULT_ROUTE_AGENT_WALL_TIMEOUT_SECONDS, help="Kill a route executor after this many wall-clock seconds. 0 disables wall timeout.")
    p_auto_loop_watchdog.add_argument("--route-agent-poll-seconds", type=float, default=DEFAULT_ROUTE_AGENT_POLL_SECONDS, help="Polling interval for route executor liveness checks.")
    p_auto_loop_watchdog.add_argument("--deep-loop-quality-score", type=float, help="Optional per-round quality score for deep-loop gates, 0-1 or 0-100.")
    p_auto_loop_watchdog.add_argument("--deep-loop-pass-threshold", type=float, help="Optional deep-loop pass threshold, 0-1 or 0-100.")
    p_auto_loop_watchdog.add_argument("--deep-loop-max-rounds", type=int, help="Override deep-loop retry budget before escalation.")
    p_auto_loop_watchdog.add_argument("--harness-report", action="append", help="Structured JSON harness/test report to pass into child deep-loop gates as evidence.")
    p_auto_loop_watchdog.add_argument("--skip-problem-escalation", action="store_true", help="Record escalation without automatically creating a problem-loop case.")
    p_auto_loop_watchdog.add_argument("--problem-promote-threshold", type=float, default=0.75, help="Promotion threshold used when auto-loop escalates into problem-loop.")
    p_auto_loop_watchdog.add_argument("--max-resumes", type=int, default=3, help="Maximum automatic auto-loop-resume attempts after resumable child stops.")
    p_auto_loop_watchdog.add_argument("--allow-unbounded-resumes", action="store_true", help="Ignore --max-resumes and keep resuming while child reports contain unattended-safe continuation work. Use with max-minutes or another external limit.")
    p_auto_loop_watchdog.add_argument("--resume-extra-rounds", type=int, default=5, help="Additional max rounds for each auto-loop-resume attempt.")
    p_auto_loop_watchdog.add_argument("--resume-extra-route-depth", type=int, default=3, help="Additional route_next transitions for each auto-loop-resume attempt.")
    p_auto_loop_watchdog.add_argument("--resume-max-minutes", type=float, help="Optional max_minutes override for resumed child loops.")
    p_auto_loop_watchdog.add_argument("--child-idle-timeout", type=float, default=DEFAULT_WATCHDOG_CHILD_IDLE_TIMEOUT_SECONDS, help="Kill the child auto-loop process after this many silent seconds. 0 disables child idle timeout.")
    p_auto_loop_watchdog.add_argument("--child-wall-timeout", type=float, default=DEFAULT_WATCHDOG_CHILD_WALL_TIMEOUT_SECONDS, help="Kill the child auto-loop process after this many wall-clock seconds. 0 disables child wall timeout.")
    p_auto_loop_watchdog.add_argument("--poll-seconds", type=float, default=DEFAULT_WATCHDOG_POLL_SECONDS, help="Polling interval for child auto-loop supervision.")
    p_auto_loop_watchdog.add_argument("--external-supervisor", choices=sorted(EXTERNAL_SUPERVISOR_CHOICES), default="none", help="Optional fail-open external supervisor layer for watchdog decisions.")
    p_auto_loop_watchdog.add_argument("--external-supervisor-model", default=DEFAULT_EXTERNAL_SUPERVISOR_MODEL, help="Model used by --external-supervisor deepseek.")
    p_auto_loop_watchdog.add_argument("--external-supervisor-base-url", default=DEFAULT_EXTERNAL_SUPERVISOR_BASE_URL, help="OpenAI-compatible base URL used by --external-supervisor deepseek.")
    p_auto_loop_watchdog.add_argument("--external-supervisor-timeout", type=float, default=DEFAULT_EXTERNAL_SUPERVISOR_TIMEOUT_SECONDS, help="Seconds to wait for external supervisor before falling back to the local watchdog decision.")
    p_auto_loop_watchdog.add_argument("--external-supervisor-max-chars", type=int, default=DEFAULT_EXTERNAL_SUPERVISOR_MAX_CHARS, help="Maximum child report excerpt characters sent to the external supervisor.")
    p_auto_loop_watchdog.add_argument("--external-supervisor-reasoning-effort", choices=["high", "max"], default="high", help="Reasoning effort for DeepSeek thinking mode.")
    p_auto_loop_watchdog.set_defaults(func=command_auto_loop_watchdog)

    p_claim_evidence = sub.add_parser("claim-evidence", help="Verify claim-to-evidence structure over evidence ids, sources, locators, and statuses.")
    p_claim_evidence.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output claim-evidence report format.")
    p_claim_evidence.add_argument("--write", action="store_true", help="Write claim-evidence report under .research-loop/reports.")
    p_claim_evidence.add_argument("--fail-on-issue", action="store_true", help="Exit 1 when any claim-evidence issue is found.")
    p_claim_evidence.add_argument("--require-source-material", action="store_true", help="Warn when evidence source is not registered as a project material. Automatically enabled when verification_strictness=strict.")
    p_claim_evidence.set_defaults(func=command_claim_evidence)

    p_resume = sub.add_parser("resume", help="Print or write a resume brief for a future thread.")
    p_resume.add_argument("--write", action="store_true", help="Write the resume brief under .research-loop/reports.")
    p_resume.add_argument("--excerpt-chars", type=int, default=2400, help="Max chars from latest handoff/checkpoint.")
    p_resume.set_defaults(func=command_resume)

    p_validate = sub.add_parser("validate", help="Validate project-loop structural integrity.")
    p_validate.add_argument("--fail-on-issue", action="store_true", help="Exit 1 when any issue is found.")
    p_validate.add_argument("--skip-claim-evidence", action="store_true", help="Skip claim-evidence verification during structural validation.")
    p_validate.add_argument("--require-source-material", action="store_true", help="Require evidence sources to match registered project materials. Automatically enabled when verification_strictness=strict.")
    p_validate.set_defaults(func=command_validate)

    p_checkpoint = sub.add_parser("checkpoint", help="Create a manual checkpoint.")
    p_checkpoint.add_argument("--name", help="Checkpoint name.")
    p_checkpoint.add_argument("--stage", help=f"Set current stage. Allowed: {', '.join(STAGES)}")
    p_checkpoint.add_argument("--note", help="Checkpoint note.")
    p_checkpoint.add_argument("--research-question", help="Update the active research question.")
    p_checkpoint.add_argument("--summary", help="Update the project summary.")
    p_checkpoint.set_defaults(func=command_checkpoint)

    p_handoff = sub.add_parser("handoff", help="Create a handoff file for a future thread.")
    p_handoff.add_argument("--name", help="Handoff name.")
    p_handoff.add_argument("--note", help="Additional handoff note.")
    p_handoff.set_defaults(func=command_handoff)

    p_run = sub.add_parser("run", help="Run a command with snapshots and logs.")
    p_run.add_argument("--name", help="Run name.")
    p_run.add_argument("command", nargs=argparse.REMAINDER, help="Command after --")
    p_run.set_defaults(func=command_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    lock_path = None
    lock_handle = None
    try:
        if command_needs_workspace_lock(args):
            cwd = resolve_workspace(getattr(args, "cwd", None))
            lock_path = loop_root(cwd) / "workspace-command.lock"
            lock_handle = acquire_path_lock(lock_path)
        return int(args.func(args))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if lock_path is not None and lock_handle is not None:
            release_path_lock(lock_path, lock_handle)


if __name__ == "__main__":
    raise SystemExit(main())
