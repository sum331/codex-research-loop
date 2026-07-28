#!/usr/bin/env python3
"""Minimal stdio MCP server for codex-research-loop.

The server intentionally shells out to research_loop.py. This keeps the MCP
surface small and lets the CLI remain the single source of behavior.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve().parent / "research_loop.py"
SERVER_NAME = "codex-research-loop"
SERVER_VERSION = "0.9.6"


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


TOOLS: list[dict[str, Any]] = [
    {
        "name": "research_loop_status",
        "description": "Show current project-local research loop status.",
        "inputSchema": schema({"cwd": {"type": "string", "description": "Active project directory."}}, ["cwd"]),
    },
    {
        "name": "research_storage_policy",
        "description": "Show, create, rebuild, audit, or materialize the project-facing research storage policy.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "style": {"type": "string", "description": "adaptive, canonical, minimal, or loop-local."},
                "rebuild": {"type": "boolean", "description": "Rebuild storage-policy.json from the selected style."},
                "init_dirs": {"type": "boolean", "description": "Create directories declared by the policy."},
                "include_optional": {"type": "boolean", "description": "Also create optional buckets such as src/code."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write a storage policy report."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_route",
        "description": "Build a multi-path research task graph and recommend routed skills, gates, and missing tools.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "intent": {"type": "string", "description": "Current user task or intent."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write route plan to reports."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_deep_loop",
        "description": "Evaluate a subchain gate, create review-for-transition or review-for-retry directives, and route the next deep-loop step.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "intent": {"type": "string", "description": "Current user goal or task intent."},
                "loop_id": {"type": "string", "description": "Optional stable loop id."},
                "current_subchain": {"type": "string", "description": "Current subchain id, e.g. P2 or P7."},
                "next_subchains": {"type": "array", "items": {"type": "string"}, "description": "Forced next subchain ids when the gate passes."},
                "gate_result": {"type": "string", "description": "auto, pass, fail, block, or human."},
                "quality_score": {"type": "number", "description": "Optional gate quality score, 0-1 or 0-100."},
                "pass_threshold": {"type": "number", "description": "Optional pass threshold, 0-1 or 0-100."},
                "gate_issues": {"type": "array", "items": {"type": "string"}, "description": "Gate issues, failed criteria, or blockers."},
                "result_summary": {"type": "string", "description": "Short summary of current round output."},
                "artifacts": {"type": "array", "items": {"type": "string"}, "description": "Artifact paths or ids produced by the current round."},
                "harness_reports": {"type": "array", "items": {"type": "string"}, "description": "Structured JSON harness/test reports to parse as gate evidence."},
                "round_index": {"type": "integer", "description": "Explicit round index for this subchain."},
                "max_rounds": {"type": "integer", "description": "Maximum retry rounds before escalation."},
                "skip_research_council": {"type": "boolean", "description": "Disable supplemental research-council review for this gate. Default is enabled."},
                "skip_adversarial_gate": {"type": "boolean", "description": "Disable supplemental adversarial gate review for this gate. Default is enabled."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write the directive and record a next action."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_observe",
        "description": "Record an OPHIS-style observation from metrics, logs, artifacts, reviews, data, or failures.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "text": {"type": "string", "description": "Observation text."},
                "kind": {"type": "string", "description": "Observation kind, e.g. metric, log, evidence_gap, artifact, review, data, failure."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "subchain": {"type": "string", "description": "P1-P10 subchain that owns this observation."},
                "source": {"type": "string", "description": "Source of the observation."},
                "artifacts": {"type": "array", "items": {"type": "string"}, "description": "Artifact paths or ids supporting the observation."},
                "signal_strength": {"type": "string", "description": "low, medium, or high."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for later phenomenon mining and gate routing."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Append to the observation ledger."},
            },
            ["cwd", "text"],
        ),
    },
    {
        "name": "research_loop_hypothesis",
        "description": "Record a falsifiable mechanism hypothesis with predictions, falsifiers, confidence, and required reads.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "mechanism": {"type": "string", "description": "Mechanism hypothesis text."},
                "phenomenon_id": {"type": "string", "description": "Phenomenon id this hypothesis explains."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "subchain": {"type": "string", "description": "P1-P10 subchain that owns this hypothesis."},
                "predictions": {"type": "array", "items": {"type": "string"}, "description": "Predictions if the mechanism is true."},
                "falsifiers": {"type": "array", "items": {"type": "string"}, "description": "Conditions that would falsify the hypothesis."},
                "confidence": {"type": "string", "description": "low, medium, or high."},
                "required_reads": {"type": "array", "items": {"type": "string"}, "description": "Required sources, artifacts, or reports."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Append to the hypothesis ledger."},
            },
            ["cwd", "mechanism"],
        ),
    },
    {
        "name": "research_loop_intervention",
        "description": "Record a minimal intervention bound to a mechanism hypothesis.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "plan": {"type": "string", "description": "Minimal intervention plan."},
                "hypothesis_id": {"type": "string", "description": "Hypothesis id this intervention tests."},
                "kind": {"type": "string", "description": "Intervention kind."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "subchain": {"type": "string", "description": "P1-P10 subchain that owns this intervention."},
                "expected_effect": {"type": "string", "description": "Expected measurable or review-visible effect."},
                "validation": {"type": "string", "description": "Validation check or harness surface."},
                "rollback": {"type": "string", "description": "Rollback or containment plan."},
                "unattended_safe": {"type": "boolean", "description": "Whether unattended auto-loop may execute follow-up work."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Append to the intervention ledger."},
            },
            ["cwd", "plan"],
        ),
    },
    {
        "name": "research_loop_ophi_cycle",
        "description": "Run one OPHIS mechanistic cycle: observation, problem, hypothesis, intervention, effect gate, and mechanism candidate.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "observation": {"type": "string", "description": "Observation from the current research loop or project artifact."},
                "problem": {"type": "string", "description": "Problem or phenomenon summary induced by the observation."},
                "hypothesis": {"type": "string", "description": "Falsifiable mechanism hypothesis."},
                "intervention": {"type": "string", "description": "Minimal intervention plan."},
                "expected_effect": {"type": "string", "description": "Expected effect if the hypothesis is useful."},
                "validation": {"type": "string", "description": "Validation check that determines whether the intervention worked."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "subchain": {"type": "string", "description": "P1-P10 subchain that owns this cycle."},
                "kind": {"type": "string", "description": "Observation kind."},
                "phenomenon_kind": {"type": "string", "description": "Phenomenon kind."},
                "source": {"type": "string", "description": "Source of the observation."},
                "artifacts": {"type": "array", "items": {"type": "string"}, "description": "Artifact paths or ids supporting the cycle."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for later mechanism retrieval and gate routing."},
                "signal_strength": {"type": "string", "description": "low, medium, or high."},
                "confidence": {"type": "string", "description": "low, medium, or high."},
                "intervention_kind": {"type": "string", "description": "Intervention kind."},
                "rollback": {"type": "string", "description": "Rollback or containment plan."},
                "unattended_safe": {"type": "boolean", "description": "Whether unattended auto-loop may act on generated next action."},
                "mechanism_status": {"type": "string", "description": "candidate, supported, rejected, or needs_replication."},
                "negative_result": {"type": "boolean", "description": "Mark the generated mechanism candidate as a negative result."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Persist all generated OPHIS records."},
            },
            ["cwd", "observation", "problem", "hypothesis", "intervention", "expected_effect", "validation"],
        ),
    },
    {
        "name": "research_loop_mechanism",
        "description": "Record a reusable mechanism or negative result in the mechanism library.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "mechanism": {"type": "string", "description": "Mechanism statement to preserve for reuse."},
                "hypothesis_id": {"type": "string", "description": "Source hypothesis id."},
                "intervention_id": {"type": "string", "description": "Source intervention id."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "subchain": {"type": "string", "description": "P1-P10 subchain where this mechanism applies."},
                "status": {"type": "string", "description": "candidate, supported, rejected, or needs_replication."},
                "scope": {"type": "string", "description": "Scope where this mechanism may be reused."},
                "effect_summary": {"type": "string", "description": "Observed or expected effect summary."},
                "reuse_conditions": {"type": "array", "items": {"type": "string"}, "description": "Conditions required before reusing this mechanism."},
                "negative_result": {"type": "boolean", "description": "Also append this mechanism to negative-results.jsonl."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Append to the mechanism library."},
            },
            ["cwd", "mechanism"],
        ),
    },
    {
        "name": "research_loop_capabilities",
        "description": "Show the research-loop capability matrix, available skills/apps, subchains, and missing tool gaps.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "format": {"type": "string", "description": "markdown or json."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_normalize",
        "description": "Convert messy natural-language input into a project-grounded downstream prompt before routing.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "input": {"type": "string", "description": "Raw user request or rough task."},
                "stage": {"type": "string", "description": "Optional stage override."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write normalized prompt to reports."},
            },
            ["cwd", "input"],
        ),
    },
    {
        "name": "research_source_hub",
        "description": "Query public scholarly metadata providers through Crossref, OpenAlex, and arXiv.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "query": {"type": "string", "description": "Search query, DOI, title, or arXiv id."},
                "provider": {"type": "string", "description": "auto, crossref, openalex, or arxiv."},
                "rows": {"type": "integer", "description": "Results per provider, 1-10."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write source-hub report to reports."},
                "record_materials": {"type": "boolean", "description": "Record returned metadata as source-metadata materials."},
            },
            ["cwd", "query"],
        ),
    },
    {
        "name": "research_content_ingest",
        "description": "Fetch or import explicit URLs and local files into article-processing packages, standardized data packages, material records, and optional llm-wiki pages.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "sources": {"type": "array", "items": {"type": "string"}, "description": "URLs or local file paths to ingest."},
                "mode": {"type": "string", "description": "auto, article, data, or file."},
                "max_bytes": {"type": "integer", "description": "Maximum bytes per source."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write content-ingest report to reports."},
                "record_materials": {"type": "boolean", "description": "Record imported items as project materials."},
                "wiki_root": {"type": "string", "description": "Optional llm-wiki root."},
                "write_wiki": {"type": "boolean", "description": "Write llm-wiki-compatible source pages and inbox hubs."},
            },
            ["cwd", "sources"],
        ),
    },
    {
        "name": "research_problem_loop",
        "description": "Analyze a blocker through an isolated scratch lab, generated expert panel, captured tests, adjustment plan, and promotion gate without mutating core files.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "problem": {"type": "string", "description": "Problem, blocker, failure, or obstacle to diagnose."},
                "case_id": {"type": "string", "description": "Optional stable case id."},
                "repro_commands": {"type": "array", "items": {"type": "string"}, "description": "Reproduction commands expected to fail before repair."},
                "test_commands": {"type": "array", "items": {"type": "string"}, "description": "Validation commands expected to pass."},
                "promote_threshold": {"type": "number", "description": "Minimum gate score needed before promotion is allowed."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write a problem-loop report."},
            },
            ["cwd", "problem"],
        ),
    },
    {
        "name": "research_problem_promote",
        "description": "Promote an approved problem-loop case into the main research loop by recording a decision and next action.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "case_id": {"type": "string", "description": "Problem-loop case id."},
                "force": {"type": "boolean", "description": "Promote even if the gate is not approved."},
                "note": {"type": "string", "description": "Human approval or promotion rationale."},
                "format": {"type": "string", "description": "markdown or json."},
            },
            ["cwd", "case_id"],
        ),
    },
    {
        "name": "research_zotero_bridge",
        "description": "Export recorded source metadata into Zotero-compatible collection plans, BibTeX, CSL-JSON, attachment plans, dedupe reports, and llm-wiki pages.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "collection": {"type": "string", "description": "Target Zotero collection name."},
                "format": {"type": "string", "description": "plan, csl-json, bibtex, or all."},
                "wiki_root": {"type": "string", "description": "Optional llm-wiki root."},
                "write": {"type": "boolean", "description": "Write bridge artifacts."},
                "write_wiki": {"type": "boolean", "description": "Write llm-wiki-compatible pages."},
                "include_attachments": {"type": "boolean", "description": "Include PDF attachment planning."},
                "no_dedupe": {"type": "boolean", "description": "Disable DOI/title dedupe."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_auto_loop",
        "description": "Run supervised validation/test/repair rounds. This compatibility entrypoint now uses auto-loop-watchdog by default so unattended work can resume across route stops.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "goal": {"type": "string", "description": "Completion goal for this unattended loop."},
                "test_commands": {"type": "array", "items": {"type": "string"}, "description": "Shell test commands."},
                "repair_commands": {"type": "array", "items": {"type": "string"}, "description": "Shell repair commands run after failed gates."},
                "max_rounds": {"type": "integer", "description": "Maximum loop rounds."},
                "max_minutes": {"type": "number", "description": "Optional wall-clock limit in minutes."},
                "format": {"type": "string", "description": "markdown or json."},
                "skip_validate": {"type": "boolean", "description": "Skip structural validation gate."},
                "allow_unbounded": {"type": "boolean", "description": "Allow unbounded round count with guardrails."},
                "skip_deep_loop": {"type": "boolean", "description": "Disable per-round deep-loop gate dispatch."},
                "deep_loop_intent": {"type": "string", "description": "Optional intent prompt used by deep-loop. Defaults to goal."},
                "current_subchain": {"type": "string", "description": "Current P1-P10 subchain for deep-loop dispatch."},
                "next_subchains": {"type": "array", "items": {"type": "string"}, "description": "Forced next P1-P10 subchains when the deep-loop gate passes."},
                "auto_route_next": {"type": "boolean", "description": "Explicitly enable automatic route_next consumption. Enabled by the CLI by default."},
                "no_auto_route_next": {"type": "boolean", "description": "Disable automatic route_next consumption and stop after handoff."},
                "route_depth_budget": {"type": "integer", "description": "Maximum automatic route_next transitions when bounded routing is used."},
                "allow_unbounded_routes": {"type": "boolean", "description": "Allow unlimited automatic route_next transitions with external safety limits."},
                "route_agent": {"type": "string", "description": "Built-in route_next executor, such as codex or none."},
                "route_agent_commands": {"type": "array", "items": {"type": "string"}, "description": "Shell command templates to run at the start of auto-routed subchains."},
                "route_codex_path": {"type": "string", "description": "Explicit Codex CLI executable path."},
                "route_codex_sandbox": {"type": "string", "description": "Sandbox mode passed to codex exec."},
                "route_codex_approval": {"type": "string", "description": "Approval mode passed to codex exec."},
                "route_codex_skip_git_check": {"type": "boolean", "description": "Pass --skip-git-repo-check to codex exec."},
                "route_codex_require_git": {"type": "boolean", "description": "Do not pass --skip-git-repo-check to codex exec."},
                "route_codex_ephemeral": {"type": "boolean", "description": "Pass --ephemeral to codex exec."},
                "route_codex_json": {"type": "boolean", "description": "Pass --json to codex exec."},
                "route_codex_output": {"type": "string", "description": "Path for --output-last-message from codex exec."},
                "route_agent_idle_timeout": {"type": "number", "description": "Kill a route executor after this many silent seconds. 0 disables idle timeout."},
                "route_agent_wall_timeout": {"type": "number", "description": "Kill a route executor after this many wall-clock seconds. 0 disables wall timeout."},
                "route_agent_poll_seconds": {"type": "number", "description": "Polling interval for route executor liveness checks."},
                "deep_loop_quality_score": {"type": "number", "description": "Optional deep-loop quality score, 0-1 or 0-100."},
                "deep_loop_pass_threshold": {"type": "number", "description": "Optional deep-loop pass threshold, 0-1 or 0-100."},
                "deep_loop_max_rounds": {"type": "integer", "description": "Override deep-loop retry budget before escalation."},
                "harness_reports": {"type": "array", "items": {"type": "string"}, "description": "Structured JSON harness/test reports passed into deep-loop gates as evidence."},
                "skip_problem_escalation": {"type": "boolean", "description": "Record escalation without automatically creating a problem-loop case."},
                "problem_promote_threshold": {"type": "number", "description": "Promotion threshold used for automatic problem-loop cases."},
                "max_resumes": {"type": "integer", "description": "Maximum automatic auto-loop-resume attempts when using the default watchdog entrypoint."},
                "allow_unbounded_resumes": {"type": "boolean", "description": "Ignore max_resumes and keep resuming while child reports contain unattended-safe continuation work."},
                "resume_extra_rounds": {"type": "integer", "description": "Additional max rounds for each watchdog resume attempt."},
                "resume_extra_route_depth": {"type": "integer", "description": "Additional route_next transitions for each watchdog resume attempt."},
                "resume_max_minutes": {"type": "number", "description": "Optional max_minutes override for resumed child loops."},
                "child_idle_timeout": {"type": "number", "description": "Kill child auto-loop after this many silent seconds. 0 disables child idle timeout."},
                "child_wall_timeout": {"type": "number", "description": "Kill child auto-loop after this many wall-clock seconds. 0 disables child wall timeout."},
                "poll_seconds": {"type": "number", "description": "Polling interval for child auto-loop supervision."},
                "external_supervisor": {"type": "string", "description": "Optional fail-open external supervisor provider, such as deepseek."},
                "external_supervisor_model": {"type": "string", "description": "Model used by the external supervisor."},
                "external_supervisor_base_url": {"type": "string", "description": "OpenAI-compatible base URL for the external supervisor."},
                "external_supervisor_timeout": {"type": "number", "description": "Seconds to wait before falling back to the local watchdog decision."},
                "external_supervisor_max_chars": {"type": "integer", "description": "Maximum child report excerpt characters sent to the external supervisor."},
                "external_supervisor_reasoning_effort": {"type": "string", "description": "DeepSeek thinking effort, high or max."},
                "legacy_auto_loop": {"type": "boolean", "description": "Use the old bare auto-loop command instead of the default watchdog-supervised entrypoint."},
            },
            ["cwd", "goal"],
        ),
    },
    {
        "name": "research_loop_auto_loop_resume",
        "description": "Resume an interrupted, handoff-required, or budget-stopped auto-loop from a previous auto-loop report.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "report": {"type": "string", "description": "Path to a previous *-auto-loop.json report."},
                "latest": {"type": "boolean", "description": "Resume from the newest auto-loop report."},
                "extra_rounds": {"type": "integer", "description": "Additional max rounds for the resumed run."},
                "extra_route_depth": {"type": "integer", "description": "Additional route_next transitions for the resumed run."},
                "max_minutes": {"type": "number", "description": "Optional wall-clock limit for the resumed run."},
                "format": {"type": "string", "description": "markdown or json."},
                "test_commands": {"type": "array", "items": {"type": "string"}, "description": "Override test commands from the source report."},
                "repair_commands": {"type": "array", "items": {"type": "string"}, "description": "Override repair commands from the source report."},
                "skip_validate": {"type": "boolean", "description": "Skip structural validation in the resumed run."},
                "allow_unbounded": {"type": "boolean", "description": "Allow unbounded resumed rounds with guardrails."},
                "allow_unbounded_routes": {"type": "boolean", "description": "Allow unlimited route_next transitions in the resumed run."},
                "no_auto_route_next": {"type": "boolean", "description": "Disable automatic continuation after the resumed starting route."},
                "route_agent": {"type": "string", "description": "Built-in route executor, such as codex or none."},
                "route_agent_commands": {"type": "array", "items": {"type": "string"}, "description": "Route-agent command templates for the resumed run."},
                "route_codex_path": {"type": "string", "description": "Explicit Codex CLI executable path."},
                "route_codex_sandbox": {"type": "string", "description": "Sandbox mode passed to codex exec."},
                "route_codex_approval": {"type": "string", "description": "Approval mode passed to codex exec."},
                "route_codex_require_git": {"type": "boolean", "description": "Do not pass --skip-git-repo-check to codex exec."},
                "route_codex_ephemeral": {"type": "boolean", "description": "Pass --ephemeral to codex exec."},
                "route_codex_json": {"type": "boolean", "description": "Pass --json to codex exec."},
                "route_codex_output": {"type": "string", "description": "Path for --output-last-message from codex exec."},
                "route_agent_idle_timeout": {"type": "number", "description": "Override route executor idle timeout for the resumed run."},
                "route_agent_wall_timeout": {"type": "number", "description": "Override route executor wall timeout for the resumed run."},
                "route_agent_poll_seconds": {"type": "number", "description": "Override route executor liveness polling interval."},
                "deep_loop_max_rounds": {"type": "integer", "description": "Override deep-loop retry budget in the resumed run."},
                "harness_reports": {"type": "array", "items": {"type": "string"}, "description": "Structured JSON harness/test reports passed into resumed deep-loop gates as evidence."},
                "skip_problem_escalation": {"type": "boolean", "description": "Do not automatically create problem-loop cases in the resumed run."},
                "problem_promote_threshold": {"type": "number", "description": "Promotion threshold used for automatic problem-loop cases."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_auto_loop_watchdog",
        "description": "Supervise auto-loop and auto-loop-resume so unattended runs keep advancing across resumable stops.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "goal": {"type": "string", "description": "Completion goal for this supervised unattended loop."},
                "test_commands": {"type": "array", "items": {"type": "string"}, "description": "Shell test commands."},
                "repair_commands": {"type": "array", "items": {"type": "string"}, "description": "Shell repair commands run after failed gates."},
                "max_rounds": {"type": "integer", "description": "Maximum rounds for the initial auto-loop."},
                "max_minutes": {"type": "number", "description": "Optional wall-clock limit passed to child loops."},
                "format": {"type": "string", "description": "markdown or json."},
                "skip_validate": {"type": "boolean", "description": "Skip structural validation gate."},
                "allow_unbounded": {"type": "boolean", "description": "Allow unbounded child round counts with guardrails."},
                "skip_deep_loop": {"type": "boolean", "description": "Disable per-round deep-loop gate dispatch."},
                "deep_loop_intent": {"type": "string", "description": "Optional intent prompt used by deep-loop. Defaults to goal."},
                "current_subchain": {"type": "string", "description": "Current P1-P10 subchain for deep-loop dispatch."},
                "next_subchains": {"type": "array", "items": {"type": "string"}, "description": "Forced next P1-P10 subchains when the deep-loop gate passes."},
                "auto_route_next": {"type": "boolean", "description": "Explicitly enable automatic route_next consumption. Enabled by default."},
                "no_auto_route_next": {"type": "boolean", "description": "Disable automatic route_next consumption."},
                "route_depth_budget": {"type": "integer", "description": "Maximum route_next transitions for the initial auto-loop."},
                "allow_unbounded_routes": {"type": "boolean", "description": "Allow unlimited route_next transitions in child loops."},
                "route_agent": {"type": "string", "description": "Built-in route executor, such as codex or none."},
                "route_agent_commands": {"type": "array", "items": {"type": "string"}, "description": "Route-agent command templates for child loops."},
                "route_codex_path": {"type": "string", "description": "Explicit Codex CLI executable path."},
                "route_codex_sandbox": {"type": "string", "description": "Sandbox mode passed to codex exec."},
                "route_codex_approval": {"type": "string", "description": "Approval mode passed to codex exec."},
                "route_codex_require_git": {"type": "boolean", "description": "Do not pass --skip-git-repo-check to codex exec."},
                "route_codex_ephemeral": {"type": "boolean", "description": "Pass --ephemeral to codex exec."},
                "route_codex_json": {"type": "boolean", "description": "Pass --json to codex exec."},
                "route_codex_output": {"type": "string", "description": "Path for --output-last-message from codex exec."},
                "route_agent_idle_timeout": {"type": "number", "description": "Kill a route executor after this many silent seconds. 0 disables idle timeout."},
                "route_agent_wall_timeout": {"type": "number", "description": "Kill a route executor after this many wall-clock seconds. 0 disables wall timeout."},
                "route_agent_poll_seconds": {"type": "number", "description": "Polling interval for route executor liveness checks."},
                "deep_loop_quality_score": {"type": "number", "description": "Optional deep-loop quality score, 0-1 or 0-100."},
                "deep_loop_pass_threshold": {"type": "number", "description": "Optional deep-loop pass threshold, 0-1 or 0-100."},
                "deep_loop_max_rounds": {"type": "integer", "description": "Override deep-loop retry budget before escalation."},
                "harness_reports": {"type": "array", "items": {"type": "string"}, "description": "Structured JSON harness/test reports passed into child deep-loop gates as evidence."},
                "skip_problem_escalation": {"type": "boolean", "description": "Record escalation without automatically creating a problem-loop case."},
                "problem_promote_threshold": {"type": "number", "description": "Promotion threshold used for automatic problem-loop cases."},
                "max_resumes": {"type": "integer", "description": "Maximum automatic auto-loop-resume attempts."},
                "allow_unbounded_resumes": {"type": "boolean", "description": "Ignore max_resumes and keep resuming while child reports contain unattended-safe continuation work."},
                "resume_extra_rounds": {"type": "integer", "description": "Additional max rounds for each resume attempt."},
                "resume_extra_route_depth": {"type": "integer", "description": "Additional route_next transitions for each resume attempt."},
                "resume_max_minutes": {"type": "number", "description": "Optional max_minutes override for resumed child loops."},
                "child_idle_timeout": {"type": "number", "description": "Kill child auto-loop after this many silent seconds. 0 disables child idle timeout."},
                "child_wall_timeout": {"type": "number", "description": "Kill child auto-loop after this many wall-clock seconds. 0 disables child wall timeout."},
                "poll_seconds": {"type": "number", "description": "Polling interval for child auto-loop supervision."},
                "external_supervisor": {"type": "string", "description": "Optional fail-open external supervisor provider, such as deepseek."},
                "external_supervisor_model": {"type": "string", "description": "Model used by the external supervisor."},
                "external_supervisor_base_url": {"type": "string", "description": "OpenAI-compatible base URL for the external supervisor."},
                "external_supervisor_timeout": {"type": "number", "description": "Seconds to wait before falling back to the local watchdog decision."},
                "external_supervisor_max_chars": {"type": "integer", "description": "Maximum child report excerpt characters sent to the external supervisor."},
                "external_supervisor_reasoning_effort": {"type": "string", "description": "DeepSeek thinking effort, high or max."},
            },
            ["cwd", "goal"],
        ),
    },
    {
        "name": "research_claim_evidence_verify",
        "description": "Verify claim-to-evidence structure over evidence ids, sources, locators, statuses, and verdicts.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string", "description": "Active project directory."},
                "format": {"type": "string", "description": "markdown or json."},
                "write": {"type": "boolean", "description": "Write claim-evidence report to reports."},
                "fail_on_issue": {"type": "boolean", "description": "Return an error when any issue is found."},
                "require_source_material": {"type": "boolean", "description": "Warn when evidence sources are not registered project materials."},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_passport",
        "description": "Update high-level project passport fields.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "stage": {"type": "string"},
                "title": {"type": "string"},
                "domain": {"type": "string"},
                "summary": {"type": "string"},
                "question": {"type": "string"},
                "targets": {"type": "array", "items": {"type": "string"}},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_profile",
        "description": "Update project profile settings used by routing and validation.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "target_venue": {"type": "string"},
                "citation_style": {"type": "string"},
                "preferred_language": {"type": "string"},
                "data_sensitivity": {"type": "string"},
                "verification_strictness": {"type": "string"},
                "route_mode": {"type": "string"},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_question",
        "description": "Record a research or open question.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "text": {"type": "string"},
                "kind": {"type": "string"},
                "status": {"type": "string"},
                "stage": {"type": "string"},
                "note": {"type": "string"},
            },
            ["cwd", "text"],
        ),
    },
    {
        "name": "research_loop_material",
        "description": "Record a research material, file, source, dataset, paper, draft, or figure.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "kind": {"type": "string"},
                "title": {"type": "string"},
                "path": {"type": "string"},
                "source": {"type": "string"},
                "status": {"type": "string"},
                "note": {"type": "string"},
            },
            ["cwd", "kind"],
        ),
    },
    {
        "name": "research_loop_claim",
        "description": "Record a key research claim.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "text": {"type": "string"},
                "status": {"type": "string"},
                "stage": {"type": "string"},
                "evidence_ids": {"type": "array", "items": {"type": "string"}},
                "note": {"type": "string"},
            },
            ["cwd", "text"],
        ),
    },
    {
        "name": "research_loop_evidence",
        "description": "Record evidence for a claim or project fact.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "kind": {"type": "string"},
                "source": {"type": "string"},
                "locator": {"type": "string"},
                "claim_id": {"type": "string"},
                "status": {"type": "string"},
                "note": {"type": "string"},
            },
            ["cwd", "kind", "source"],
        ),
    },
    {
        "name": "research_loop_decision",
        "description": "Record a research decision and rationale.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "decision": {"type": "string"},
                "rationale": {"type": "string"},
                "alternatives": {"type": "string"},
                "status": {"type": "string"},
                "stage": {"type": "string"},
            },
            ["cwd", "decision"],
        ),
    },
    {
        "name": "research_loop_risk",
        "description": "Record a research risk or integrity concern.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "text": {"type": "string"},
                "severity": {"type": "string"},
                "status": {"type": "string"},
                "mitigation": {"type": "string"},
            },
            ["cwd", "text"],
        ),
    },
    {
        "name": "research_loop_next",
        "description": "Record a next action.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "text": {"type": "string"},
                "stage": {"type": "string"},
                "status": {"type": "string"},
                "owner": {"type": "string"},
            },
            ["cwd", "text"],
        ),
    },
    {
        "name": "research_loop_update",
        "description": "Update or close an existing loop record by id.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "kind": {"type": "string"},
                "id": {"type": "string"},
                "status": {"type": "string"},
                "text": {"type": "string"},
                "note": {"type": "string"},
                "severity": {"type": "string"},
                "mitigation": {"type": "string"},
                "stage": {"type": "string"},
                "title": {"type": "string"},
                "source": {"type": "string"},
                "path": {"type": "string"},
                "locator": {"type": "string"},
                "evidence_ids": {"type": "array", "items": {"type": "string"}},
            },
            ["cwd", "kind", "id"],
        ),
    },
    {
        "name": "research_loop_checkpoint",
        "description": "Create a manual research loop checkpoint.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "name": {"type": "string"},
                "stage": {"type": "string"},
                "note": {"type": "string"},
                "research_question": {"type": "string"},
                "summary": {"type": "string"},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_handoff",
        "description": "Create a handoff file for a future Codex thread.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "name": {"type": "string"},
                "note": {"type": "string"},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_validate",
        "description": "Validate project-loop structural integrity.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "fail_on_issue": {"type": "boolean"},
                "skip_claim_evidence": {"type": "boolean"},
                "require_source_material": {"type": "boolean"},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_resume",
        "description": "Print or write a resume brief for a future Codex thread.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "write": {"type": "boolean"},
                "excerpt_chars": {"type": "integer"},
            },
            ["cwd"],
        ),
    },
    {
        "name": "research_loop_run",
        "description": "Run a shell command with research-loop snapshots and logs.",
        "inputSchema": schema(
            {
                "cwd": {"type": "string"},
                "command": {"type": "string"},
                "name": {"type": "string"},
            },
            ["cwd", "command"],
        ),
    },
]


def as_bool(value: Any) -> bool:
    return bool(value) if value is not None else False


def add_option(command: list[str], flag: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str) and value == "":
        return
    command.extend([flag, str(value)])


def run_cli(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    text = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, text.strip()


def tool_to_cli(name: str, args: dict[str, Any]) -> list[str]:
    cwd = args.get("cwd")
    command = ["--cwd", str(cwd)]
    if name == "research_loop_status":
        return [*command, "status"]
    if name == "research_storage_policy":
        command.append("storage")
        add_option(command, "--style", args.get("style"))
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("rebuild")):
            command.append("--rebuild")
        if as_bool(args.get("init_dirs")):
            command.append("--init-dirs")
        if as_bool(args.get("include_optional")):
            command.append("--include-optional")
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_route":
        command.append("route")
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--intent", args.get("intent"))
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_deep_loop":
        command.append("deep-loop")
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--intent", args.get("intent"))
        add_option(command, "--loop-id", args.get("loop_id"))
        add_option(command, "--current-subchain", args.get("current_subchain"))
        for next_subchain in args.get("next_subchains") or []:
            add_option(command, "--next-subchain", next_subchain)
        add_option(command, "--gate-result", args.get("gate_result"))
        add_option(command, "--quality-score", args.get("quality_score"))
        add_option(command, "--pass-threshold", args.get("pass_threshold"))
        for gate_issue in args.get("gate_issues") or []:
            add_option(command, "--gate-issue", gate_issue)
        add_option(command, "--result-summary", args.get("result_summary"))
        for artifact in args.get("artifacts") or []:
            add_option(command, "--artifact", artifact)
        for report in args.get("harness_reports") or []:
            add_option(command, "--harness-report", report)
        add_option(command, "--round-index", args.get("round_index"))
        add_option(command, "--max-rounds", args.get("max_rounds"))
        if as_bool(args.get("skip_research_council")):
            command.append("--skip-research-council")
        if as_bool(args.get("skip_adversarial_gate")):
            command.append("--skip-adversarial-gate")
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_observe":
        command.append("observe")
        add_option(command, "--text", args.get("text"))
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--subchain", args.get("subchain"))
        add_option(command, "--source", args.get("source"))
        for artifact in args.get("artifacts") or []:
            add_option(command, "--artifact", artifact)
        add_option(command, "--signal-strength", args.get("signal_strength"))
        for tag in args.get("tags") or []:
            add_option(command, "--tag", tag)
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_hypothesis":
        command.append("hypothesis")
        add_option(command, "--mechanism", args.get("mechanism"))
        add_option(command, "--phenomenon-id", args.get("phenomenon_id"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--subchain", args.get("subchain"))
        for prediction in args.get("predictions") or []:
            add_option(command, "--prediction", prediction)
        for falsifier in args.get("falsifiers") or []:
            add_option(command, "--falsifier", falsifier)
        add_option(command, "--confidence", args.get("confidence"))
        for required_read in args.get("required_reads") or []:
            add_option(command, "--required-read", required_read)
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_intervention":
        command.append("intervention")
        add_option(command, "--plan", args.get("plan"))
        add_option(command, "--hypothesis-id", args.get("hypothesis_id"))
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--subchain", args.get("subchain"))
        add_option(command, "--expected-effect", args.get("expected_effect"))
        add_option(command, "--validation", args.get("validation"))
        add_option(command, "--rollback", args.get("rollback"))
        if args.get("unattended_safe") is False:
            command.append("--no-unattended-safe")
        elif as_bool(args.get("unattended_safe")):
            command.append("--unattended-safe")
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_ophi_cycle":
        command.append("ophi-cycle")
        add_option(command, "--observation", args.get("observation"))
        add_option(command, "--problem", args.get("problem"))
        add_option(command, "--hypothesis", args.get("hypothesis"))
        add_option(command, "--intervention", args.get("intervention"))
        add_option(command, "--expected-effect", args.get("expected_effect"))
        add_option(command, "--validation", args.get("validation"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--subchain", args.get("subchain"))
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--phenomenon-kind", args.get("phenomenon_kind"))
        add_option(command, "--source", args.get("source"))
        for artifact in args.get("artifacts") or []:
            add_option(command, "--artifact", artifact)
        for tag in args.get("tags") or []:
            add_option(command, "--tag", tag)
        add_option(command, "--signal-strength", args.get("signal_strength"))
        add_option(command, "--confidence", args.get("confidence"))
        add_option(command, "--intervention-kind", args.get("intervention_kind"))
        add_option(command, "--rollback", args.get("rollback"))
        if args.get("unattended_safe") is False:
            command.append("--no-unattended-safe")
        elif as_bool(args.get("unattended_safe")):
            command.append("--unattended-safe")
        add_option(command, "--mechanism-status", args.get("mechanism_status"))
        if as_bool(args.get("negative_result")):
            command.append("--negative-result")
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_mechanism":
        command.append("mechanism")
        add_option(command, "--mechanism", args.get("mechanism"))
        add_option(command, "--hypothesis-id", args.get("hypothesis_id"))
        add_option(command, "--intervention-id", args.get("intervention_id"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--subchain", args.get("subchain"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--scope", args.get("scope"))
        add_option(command, "--effect-summary", args.get("effect_summary"))
        for reuse_condition in args.get("reuse_conditions") or []:
            add_option(command, "--reuse-condition", reuse_condition)
        if as_bool(args.get("negative_result")):
            command.append("--negative-result")
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_loop_capabilities":
        command.append("capabilities")
        add_option(command, "--format", args.get("format"))
        return command
    if name == "research_loop_normalize":
        command.append("normalize")
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--input", args.get("input"))
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_source_hub":
        command.append("source-hub")
        add_option(command, "--query", args.get("query"))
        add_option(command, "--provider", args.get("provider"))
        add_option(command, "--rows", args.get("rows"))
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        if as_bool(args.get("record_materials")):
            command.append("--record-materials")
        return command
    if name == "research_content_ingest":
        command.append("content-ingest")
        for source in args.get("sources") or []:
            add_option(command, "--source", source)
        add_option(command, "--mode", args.get("mode"))
        add_option(command, "--max-bytes", args.get("max_bytes"))
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        if as_bool(args.get("record_materials")):
            command.append("--record-materials")
        add_option(command, "--wiki-root", args.get("wiki_root"))
        if as_bool(args.get("write_wiki")):
            command.append("--write-wiki")
        return command
    if name == "research_problem_loop":
        command.append("problem-loop")
        add_option(command, "--problem", args.get("problem"))
        add_option(command, "--case-id", args.get("case_id"))
        for repro_command in args.get("repro_commands") or []:
            add_option(command, "--repro-command", repro_command)
        for test_command in args.get("test_commands") or []:
            add_option(command, "--test-command", test_command)
        add_option(command, "--promote-threshold", args.get("promote_threshold"))
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        return command
    if name == "research_problem_promote":
        command.append("problem-promote")
        add_option(command, "--case-id", args.get("case_id"))
        if as_bool(args.get("force")):
            command.append("--force")
        add_option(command, "--note", args.get("note"))
        add_option(command, "--format", args.get("format"))
        return command
    if name == "research_zotero_bridge":
        command.append("zotero-bridge")
        add_option(command, "--collection", args.get("collection"))
        add_option(command, "--format", args.get("format"))
        add_option(command, "--wiki-root", args.get("wiki_root"))
        if as_bool(args.get("write")):
            command.append("--write")
        if as_bool(args.get("write_wiki")):
            command.append("--write-wiki")
        if as_bool(args.get("include_attachments")):
            command.append("--include-attachments")
        if as_bool(args.get("no_dedupe")):
            command.append("--no-dedupe")
        return command
    if name == "research_loop_auto_loop":
        legacy_auto_loop = as_bool(args.get("legacy_auto_loop"))
        command.append("auto-loop" if legacy_auto_loop else "auto-loop-watchdog")
        add_option(command, "--goal", args.get("goal"))
        for test_command in args.get("test_commands") or []:
            add_option(command, "--test-command", test_command)
        for repair_command in args.get("repair_commands") or []:
            add_option(command, "--repair-command", repair_command)
        add_option(command, "--max-rounds", args.get("max_rounds"))
        add_option(command, "--max-minutes", args.get("max_minutes"))
        add_option(command, "--format", args.get("format"))
        add_option(command, "--deep-loop-intent", args.get("deep_loop_intent"))
        add_option(command, "--current-subchain", args.get("current_subchain"))
        for next_subchain in args.get("next_subchains") or []:
            add_option(command, "--next-subchain", next_subchain)
        if args.get("auto_route_next") is False or as_bool(args.get("no_auto_route_next")):
            command.append("--no-auto-route-next")
        elif as_bool(args.get("auto_route_next")):
            command.append("--auto-route-next")
        add_option(command, "--route-depth-budget", args.get("route_depth_budget"))
        if as_bool(args.get("allow_unbounded_routes")):
            command.append("--allow-unbounded-routes")
        add_option(command, "--route-agent", args.get("route_agent"))
        for route_command in args.get("route_agent_commands") or []:
            add_option(command, "--route-agent-command", route_command)
        add_option(command, "--route-codex-path", args.get("route_codex_path"))
        add_option(command, "--route-codex-sandbox", args.get("route_codex_sandbox"))
        add_option(command, "--route-codex-approval", args.get("route_codex_approval"))
        if as_bool(args.get("route_codex_skip_git_check")):
            command.append("--route-codex-skip-git-check")
        if as_bool(args.get("route_codex_require_git")):
            command.append("--route-codex-require-git")
        if as_bool(args.get("route_codex_ephemeral")):
            command.append("--route-codex-ephemeral")
        if as_bool(args.get("route_codex_json")):
            command.append("--route-codex-json")
        add_option(command, "--route-codex-output", args.get("route_codex_output"))
        add_option(command, "--route-agent-idle-timeout", args.get("route_agent_idle_timeout"))
        add_option(command, "--route-agent-wall-timeout", args.get("route_agent_wall_timeout"))
        add_option(command, "--route-agent-poll-seconds", args.get("route_agent_poll_seconds"))
        add_option(command, "--deep-loop-quality-score", args.get("deep_loop_quality_score"))
        add_option(command, "--deep-loop-pass-threshold", args.get("deep_loop_pass_threshold"))
        add_option(command, "--deep-loop-max-rounds", args.get("deep_loop_max_rounds"))
        for report in args.get("harness_reports") or []:
            add_option(command, "--harness-report", report)
        add_option(command, "--problem-promote-threshold", args.get("problem_promote_threshold"))
        if as_bool(args.get("skip_validate")):
            command.append("--skip-validate")
        if as_bool(args.get("allow_unbounded")):
            command.append("--allow-unbounded")
        if as_bool(args.get("skip_deep_loop")):
            command.append("--skip-deep-loop")
        if as_bool(args.get("skip_problem_escalation")):
            command.append("--skip-problem-escalation")
        if not legacy_auto_loop:
            add_option(command, "--max-resumes", args.get("max_resumes"))
            if as_bool(args.get("allow_unbounded_resumes")):
                command.append("--allow-unbounded-resumes")
            add_option(command, "--resume-extra-rounds", args.get("resume_extra_rounds"))
            add_option(command, "--resume-extra-route-depth", args.get("resume_extra_route_depth"))
            add_option(command, "--resume-max-minutes", args.get("resume_max_minutes"))
            add_option(command, "--child-idle-timeout", args.get("child_idle_timeout"))
            add_option(command, "--child-wall-timeout", args.get("child_wall_timeout"))
            add_option(command, "--poll-seconds", args.get("poll_seconds"))
            add_option(command, "--external-supervisor", args.get("external_supervisor"))
            add_option(command, "--external-supervisor-model", args.get("external_supervisor_model"))
            add_option(command, "--external-supervisor-base-url", args.get("external_supervisor_base_url"))
            add_option(command, "--external-supervisor-timeout", args.get("external_supervisor_timeout"))
            add_option(command, "--external-supervisor-max-chars", args.get("external_supervisor_max_chars"))
            add_option(command, "--external-supervisor-reasoning-effort", args.get("external_supervisor_reasoning_effort"))
        return command
    if name == "research_loop_auto_loop_resume":
        command.append("auto-loop-resume")
        add_option(command, "--report", args.get("report"))
        if as_bool(args.get("latest")):
            command.append("--latest")
        add_option(command, "--extra-rounds", args.get("extra_rounds"))
        add_option(command, "--extra-route-depth", args.get("extra_route_depth"))
        add_option(command, "--max-minutes", args.get("max_minutes"))
        add_option(command, "--format", args.get("format"))
        for test_command in args.get("test_commands") or []:
            add_option(command, "--test-command", test_command)
        for repair_command in args.get("repair_commands") or []:
            add_option(command, "--repair-command", repair_command)
        if as_bool(args.get("skip_validate")):
            command.append("--skip-validate")
        if as_bool(args.get("allow_unbounded")):
            command.append("--allow-unbounded")
        if as_bool(args.get("allow_unbounded_routes")):
            command.append("--allow-unbounded-routes")
        if as_bool(args.get("no_auto_route_next")):
            command.append("--no-auto-route-next")
        add_option(command, "--route-agent", args.get("route_agent"))
        for route_command in args.get("route_agent_commands") or []:
            add_option(command, "--route-agent-command", route_command)
        add_option(command, "--route-codex-path", args.get("route_codex_path"))
        add_option(command, "--route-codex-sandbox", args.get("route_codex_sandbox"))
        add_option(command, "--route-codex-approval", args.get("route_codex_approval"))
        if as_bool(args.get("route_codex_require_git")):
            command.append("--route-codex-require-git")
        if as_bool(args.get("route_codex_ephemeral")):
            command.append("--route-codex-ephemeral")
        if as_bool(args.get("route_codex_json")):
            command.append("--route-codex-json")
        add_option(command, "--route-codex-output", args.get("route_codex_output"))
        add_option(command, "--route-agent-idle-timeout", args.get("route_agent_idle_timeout"))
        add_option(command, "--route-agent-wall-timeout", args.get("route_agent_wall_timeout"))
        add_option(command, "--route-agent-poll-seconds", args.get("route_agent_poll_seconds"))
        add_option(command, "--deep-loop-max-rounds", args.get("deep_loop_max_rounds"))
        for report in args.get("harness_reports") or []:
            add_option(command, "--harness-report", report)
        if as_bool(args.get("skip_problem_escalation")):
            command.append("--skip-problem-escalation")
        add_option(command, "--problem-promote-threshold", args.get("problem_promote_threshold"))
        return command
    if name == "research_loop_auto_loop_watchdog":
        command.append("auto-loop-watchdog")
        add_option(command, "--goal", args.get("goal"))
        for test_command in args.get("test_commands") or []:
            add_option(command, "--test-command", test_command)
        for repair_command in args.get("repair_commands") or []:
            add_option(command, "--repair-command", repair_command)
        add_option(command, "--max-rounds", args.get("max_rounds"))
        add_option(command, "--max-minutes", args.get("max_minutes"))
        add_option(command, "--format", args.get("format"))
        add_option(command, "--deep-loop-intent", args.get("deep_loop_intent"))
        add_option(command, "--current-subchain", args.get("current_subchain"))
        for next_subchain in args.get("next_subchains") or []:
            add_option(command, "--next-subchain", next_subchain)
        if args.get("auto_route_next") is False or as_bool(args.get("no_auto_route_next")):
            command.append("--no-auto-route-next")
        elif as_bool(args.get("auto_route_next")):
            command.append("--auto-route-next")
        add_option(command, "--route-depth-budget", args.get("route_depth_budget"))
        if as_bool(args.get("allow_unbounded_routes")):
            command.append("--allow-unbounded-routes")
        add_option(command, "--route-agent", args.get("route_agent"))
        for route_command in args.get("route_agent_commands") or []:
            add_option(command, "--route-agent-command", route_command)
        add_option(command, "--route-codex-path", args.get("route_codex_path"))
        add_option(command, "--route-codex-sandbox", args.get("route_codex_sandbox"))
        add_option(command, "--route-codex-approval", args.get("route_codex_approval"))
        if as_bool(args.get("route_codex_require_git")):
            command.append("--route-codex-require-git")
        if as_bool(args.get("route_codex_ephemeral")):
            command.append("--route-codex-ephemeral")
        if as_bool(args.get("route_codex_json")):
            command.append("--route-codex-json")
        add_option(command, "--route-codex-output", args.get("route_codex_output"))
        add_option(command, "--route-agent-idle-timeout", args.get("route_agent_idle_timeout"))
        add_option(command, "--route-agent-wall-timeout", args.get("route_agent_wall_timeout"))
        add_option(command, "--route-agent-poll-seconds", args.get("route_agent_poll_seconds"))
        add_option(command, "--deep-loop-quality-score", args.get("deep_loop_quality_score"))
        add_option(command, "--deep-loop-pass-threshold", args.get("deep_loop_pass_threshold"))
        add_option(command, "--deep-loop-max-rounds", args.get("deep_loop_max_rounds"))
        for report in args.get("harness_reports") or []:
            add_option(command, "--harness-report", report)
        add_option(command, "--problem-promote-threshold", args.get("problem_promote_threshold"))
        add_option(command, "--max-resumes", args.get("max_resumes"))
        if as_bool(args.get("allow_unbounded_resumes")):
            command.append("--allow-unbounded-resumes")
        add_option(command, "--resume-extra-rounds", args.get("resume_extra_rounds"))
        add_option(command, "--resume-extra-route-depth", args.get("resume_extra_route_depth"))
        add_option(command, "--resume-max-minutes", args.get("resume_max_minutes"))
        add_option(command, "--child-idle-timeout", args.get("child_idle_timeout"))
        add_option(command, "--child-wall-timeout", args.get("child_wall_timeout"))
        add_option(command, "--poll-seconds", args.get("poll_seconds"))
        add_option(command, "--external-supervisor", args.get("external_supervisor"))
        add_option(command, "--external-supervisor-model", args.get("external_supervisor_model"))
        add_option(command, "--external-supervisor-base-url", args.get("external_supervisor_base_url"))
        add_option(command, "--external-supervisor-timeout", args.get("external_supervisor_timeout"))
        add_option(command, "--external-supervisor-max-chars", args.get("external_supervisor_max_chars"))
        add_option(command, "--external-supervisor-reasoning-effort", args.get("external_supervisor_reasoning_effort"))
        if as_bool(args.get("skip_validate")):
            command.append("--skip-validate")
        if as_bool(args.get("allow_unbounded")):
            command.append("--allow-unbounded")
        if as_bool(args.get("skip_deep_loop")):
            command.append("--skip-deep-loop")
        if as_bool(args.get("skip_problem_escalation")):
            command.append("--skip-problem-escalation")
        return command
    if name == "research_claim_evidence_verify":
        command.append("claim-evidence")
        add_option(command, "--format", args.get("format"))
        if as_bool(args.get("write")):
            command.append("--write")
        if as_bool(args.get("fail_on_issue")):
            command.append("--fail-on-issue")
        if as_bool(args.get("require_source_material")):
            command.append("--require-source-material")
        return command
    if name == "research_loop_passport":
        command.append("passport")
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--title", args.get("title"))
        add_option(command, "--domain", args.get("domain"))
        add_option(command, "--summary", args.get("summary"))
        add_option(command, "--question", args.get("question"))
        for target in args.get("targets") or []:
            add_option(command, "--target", target)
        return command
    if name == "research_loop_profile":
        command.append("profile")
        add_option(command, "--target-venue", args.get("target_venue"))
        add_option(command, "--citation-style", args.get("citation_style"))
        add_option(command, "--preferred-language", args.get("preferred_language"))
        add_option(command, "--data-sensitivity", args.get("data_sensitivity"))
        add_option(command, "--verification-strictness", args.get("verification_strictness"))
        add_option(command, "--route-mode", args.get("route_mode"))
        return command
    if name == "research_loop_question":
        command.append("question")
        add_option(command, "--text", args.get("text"))
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--note", args.get("note"))
        return command
    if name == "research_loop_material":
        command.append("material")
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--title", args.get("title"))
        add_option(command, "--path", args.get("path"))
        add_option(command, "--source", args.get("source"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--note", args.get("note"))
        return command
    if name == "research_loop_claim":
        command.append("claim")
        add_option(command, "--text", args.get("text"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--stage", args.get("stage"))
        for evidence_id in args.get("evidence_ids") or []:
            add_option(command, "--evidence-id", evidence_id)
        add_option(command, "--note", args.get("note"))
        return command
    if name == "research_loop_evidence":
        command.append("evidence")
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--source", args.get("source"))
        add_option(command, "--locator", args.get("locator"))
        add_option(command, "--claim-id", args.get("claim_id"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--note", args.get("note"))
        return command
    if name == "research_loop_decision":
        command.append("decision")
        add_option(command, "--decision", args.get("decision"))
        add_option(command, "--rationale", args.get("rationale"))
        add_option(command, "--alternatives", args.get("alternatives"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--stage", args.get("stage"))
        return command
    if name == "research_loop_risk":
        command.append("risk")
        add_option(command, "--text", args.get("text"))
        add_option(command, "--severity", args.get("severity"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--mitigation", args.get("mitigation"))
        return command
    if name == "research_loop_next":
        command.append("next")
        add_option(command, "--text", args.get("text"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--owner", args.get("owner"))
        return command
    if name == "research_loop_update":
        command.append("update")
        add_option(command, "--kind", args.get("kind"))
        add_option(command, "--id", args.get("id"))
        add_option(command, "--status", args.get("status"))
        add_option(command, "--text", args.get("text"))
        add_option(command, "--note", args.get("note"))
        add_option(command, "--severity", args.get("severity"))
        add_option(command, "--mitigation", args.get("mitigation"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--title", args.get("title"))
        add_option(command, "--source", args.get("source"))
        add_option(command, "--path", args.get("path"))
        add_option(command, "--locator", args.get("locator"))
        for evidence_id in args.get("evidence_ids") or []:
            add_option(command, "--evidence-id", evidence_id)
        return command
    if name == "research_loop_checkpoint":
        command.append("checkpoint")
        add_option(command, "--name", args.get("name"))
        add_option(command, "--stage", args.get("stage"))
        add_option(command, "--note", args.get("note"))
        add_option(command, "--research-question", args.get("research_question"))
        add_option(command, "--summary", args.get("summary"))
        return command
    if name == "research_loop_handoff":
        command.append("handoff")
        add_option(command, "--name", args.get("name"))
        add_option(command, "--note", args.get("note"))
        return command
    if name == "research_loop_validate":
        command.append("validate")
        if as_bool(args.get("fail_on_issue")):
            command.append("--fail-on-issue")
        if as_bool(args.get("skip_claim_evidence")):
            command.append("--skip-claim-evidence")
        if as_bool(args.get("require_source_material")):
            command.append("--require-source-material")
        return command
    if name == "research_loop_resume":
        command.append("resume")
        if as_bool(args.get("write")):
            command.append("--write")
        add_option(command, "--excerpt-chars", args.get("excerpt_chars"))
        return command
    if name == "research_loop_run":
        command.append("run")
        add_option(command, "--name", args.get("name"))
        command.append("--")
        command.append(str(args.get("command")))
        return command
    raise ValueError(f"Unknown tool: {name}")


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        cli = tool_to_cli(name, args)
        code, text = run_cli(cli)
        return {
            "content": [{"type": "text", "text": text or "(no output)"}],
            "isError": code != 0,
        }
    except Exception as exc:
        return {
            "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}],
            "isError": True,
        }


def response(message_id: Any, result: Any = None, error: Any = None) -> dict[str, Any]:
    payload = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return payload


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    message_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if method == "initialize":
        return response(
            message_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
    if method == "tools/list":
        return response(message_id, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        return response(message_id, call_tool(str(name), arguments))
    if method == "ping":
        return response(message_id, {})
    if method and method.startswith("notifications/"):
        return None
    if message_id is None:
        return None
    return response(message_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            reply = handle(message)
            if reply is not None:
                print(json.dumps(reply, ensure_ascii=True), flush=True)
        except Exception as exc:
            error = response(None, error={"code": -32603, "message": f"{type(exc).__name__}: {exc}"})
            print(json.dumps(error, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
