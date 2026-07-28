from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


research_loop = load_module("research_loop_under_test", ROOT / "scripts" / "research_loop.py")
mcp_server = load_module("mcp_server_under_test", ROOT / "scripts" / "mcp_server.py")


def deep_args(**overrides):
    values = {
        "intent": "analyze experiment outputs and prepare figures",
        "current_subchain": "P6",
        "next_subchain": ["P7"],
        "gate_result": "pass",
        "quality_score": None,
        "pass_threshold": None,
        "max_rounds": None,
        "round_index": 1,
        "gate_issue": [],
        "result_summary": "",
        "artifact": [],
        "harness_report": [],
        "loop_id": "test-loop",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def minimal_state(stage: str = "ANALYSIS"):
    return {
        "project_id": "test-project",
        "current_stage": stage,
        "latest_handoff": None,
        "latest_checkpoint": None,
        "counters": {},
    }


def minimal_passport():
    return {
        "project_title": "Synthetic Project",
        "domain": "astronomy",
        "research_question": "Which signal is supported by the data?",
        "materials": [],
        "key_claims": [],
        "risks": [],
        "next_actions": [],
        "profile": {"verification_strictness": "standard", "route_mode": "standard"},
    }


class DeepLoopSubagentTests(unittest.TestCase):
    def test_plugin_manifest_prompts_external_api_pairing(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        prompts = "\n".join(manifest["interface"].get("defaultPrompt") or [])

        self.assertIn("DeepSeek", prompts)
        self.assertIn("external supervisor", prompts)
        self.assertIn("DEEPSEEK_API_KEY", prompts)

    def test_portable_bundle_contains_skills_dispatch_plugin_and_installer(self):
        portable = ROOT / "portable"
        manifest_path = portable / "manifests" / "codex-portable-manifest.json"
        channels_path = portable / "manifests" / "plugin-install-channels.json"
        dispatch_path = portable / "dispatch" / "codex_capability_dispatch_inventory_20260702.md"
        installer_path = portable / "scripts" / "install-codex-portable.ps1"
        router_path = portable / "plugins" / "prompt-submit-skill-router" / "scripts" / "user_prompt_submit_router.py"

        self.assertTrue(manifest_path.exists())
        self.assertTrue(channels_path.exists())
        self.assertTrue(dispatch_path.exists())
        self.assertTrue(installer_path.exists())
        self.assertTrue(router_path.exists())
        self.assertTrue((portable / "skills" / "research-loop" / "SKILL.md").exists())
        self.assertTrue((portable / "skills" / "skill-plugin-router" / "SKILL.md").exists())
        self.assertTrue((portable / "skills" / "local-task-hooks" / "SKILL.md").exists())
        self.assertTrue((portable / "hooks" / "local-task-hooks" / "codex_lifecycle_hook.py").exists())
        self.assertIn("CODEX_RESEARCH_LOOP_HOME", installer_path.read_text(encoding="utf-8"))

        portable_skill = (portable / "skills" / "research-loop" / "SKILL.md").read_text(encoding="utf-8")
        source_skill = (ROOT / "skills" / "research-loop" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("$env:CODEX_RESEARCH_LOOP_HOME", portable_skill)
        self.assertIn("$env:CODEX_RESEARCH_LOOP_HOME", source_skill)
        self.assertNotIn("C:\\Users\\ASUS\\plugins\\codex-research-loop", portable_skill)
        self.assertNotIn("C:\\Users\\ASUS\\plugins\\codex-research-loop", source_skill)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        self.assertIn("research-loop", manifest["packaged_skills"])
        self.assertIn("skill-plugin-router", manifest["packaged_skills"])
        self.assertIn("prompt-submit-skill-router", manifest["packaged_plugins"])
        self.assertIn("codex_capability_dispatch_inventory_20260702.md", manifest["dispatch_tables"])
        self.assertFalse(manifest["includes_secrets"])

        channels = json.loads(channels_path.read_text(encoding="utf-8"))
        self.assertIn("codex-research-loop", [item["name"] for item in channels["local_plugins"]])
        self.assertIn("github@openai-curated-remote", [item["id"] for item in channels["managed_plugins"]])
        self.assertIn("documents@openai-primary-runtime", [item["id"] for item in channels["runtime_plugins"]])
        self.assertTrue(channels["auto_install"]["fail_open"])

    def test_prompt_router_dispatches_research_loop_requests(self):
        portable = ROOT / "portable"
        dispatch_path = portable / "dispatch" / "codex_capability_dispatch_inventory_20260702.md"
        router_path = portable / "plugins" / "prompt-submit-skill-router" / "scripts" / "user_prompt_submit_router.py"
        registry = dispatch_path.read_text(encoding="utf-8")
        self.assertIn("skill:research-loop", registry)
        self.assertIn("capability-registry-id: skill:research-loop", registry)

        env = os.environ.copy()
        env["CODEX_CAPABILITY_REGISTRY"] = str(dispatch_path)
        result = subprocess.run(
            [sys.executable, str(router_path)],
            input=json.dumps({"prompt": "继续完善 research loop deep-loop 专家委员会和对抗 gate"}),
            text=True,
            capture_output=True,
            encoding="utf-8",
            env=env,
            check=True,
        )

        self.assertIn("skill:research-loop", result.stdout)

    def test_normalize_adds_standard_harness_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            research_loop.init_project(cwd)
            state = research_loop.load_state(cwd)
            passport = research_loop.load_passport(cwd, state)

            payload = research_loop.normalize_task_input(cwd, state, passport, "continue the current research task")

        self.assertEqual(payload["execution_profile"]["id"], "standard_loop")
        self.assertIn("route plan", payload["harness_protocol"]["validation_surfaces"])
        self.assertIn("grader", payload["harness_protocol"]["case_contract"]["fields"])
        self.assertIn("failures_by_tag", payload["harness_protocol"]["feedback_summary"]["preferred_metrics"])
        self.assertIn("Execution profile: standard_loop", payload["downstream_prompt"])
        self.assertIn("If using reproducible cases", payload["downstream_prompt"])
        self.assertTrue(any("inspect generated artifacts or logs directly" in item for item in payload["harness_protocol"]["guardrails"]))

    def test_capability_matrix_exposes_council_and_adversarial_gate(self):
        payload = research_loop.capability_matrix_payload()
        available_ids = {item["id"] for item in payload["available_capabilities"]}

        self.assertIn("tool:research-council-reviewer", available_ids)
        self.assertIn("tool:adversarial-gate-reviewer", available_ids)

    def test_capability_matrix_exposes_ophi_mechanistic_tools(self):
        payload = research_loop.capability_matrix_payload()
        available_ids = {item["id"] for item in payload["available_capabilities"]}

        self.assertIn("tool:mechanistic-observer", available_ids)
        self.assertIn("tool:phenomenon-miner", available_ids)
        self.assertIn("tool:hypothesis-portfolio", available_ids)
        self.assertIn("tool:intervention-planner", available_ids)
        self.assertIn("tool:mechanism-library", available_ids)

    def test_ophi_cycle_records_mechanistic_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    str(cwd),
                    "ophi-cycle",
                    "--observation",
                    "Metric improves on smoke data but collapses on held-out cases.",
                    "--problem",
                    "The current analysis may be overfitting a narrow validation slice.",
                    "--hypothesis",
                    "The gate is optimizing artifact readiness without enough variance checks.",
                    "--intervention",
                    "Add a variance-focused harness gate before writing-stage promotion.",
                    "--expected-effect",
                    "Late-stage routes should retry analysis instead of promoting unstable results.",
                    "--validation",
                    "Compare pass/fail decisions before and after the variance gate on two reports.",
                    "--stage",
                    "ANALYSIS",
                    "--subchain",
                    "P6",
                    "--artifact",
                    "reports/harness.json",
                    "--tag",
                    "variance",
                    "--write",
                    "--format",
                    "json",
                ],
                text=True,
                capture_output=True,
                encoding="utf-8",
                check=True,
            )

            payload = json.loads(proc.stdout)
            root = cwd / ".research-loop"

            self.assertEqual(payload["schema_version"], research_loop.SCHEMA_VERSION)
            self.assertEqual(payload["observation"]["type"], "observation")
            self.assertEqual(payload["phenomenon"]["type"], "phenomenon")
            self.assertEqual(payload["hypothesis"]["type"], "hypothesis")
            self.assertEqual(payload["intervention"]["type"], "intervention")
            self.assertEqual(payload["mechanism_candidate"]["type"], "mechanism")
            self.assertEqual(payload["effect_gate"]["status"], "pending_validation")
            self.assertIn("mechanism_candidate", payload["next_actions"][0]["text"])

            self.assertTrue((root / "observations" / "observation-ledger.jsonl").exists())
            self.assertTrue((root / "phenomena" / "phenomenon-ledger.jsonl").exists())
            self.assertTrue((root / "hypotheses" / "hypothesis-ledger.jsonl").exists())
            self.assertTrue((root / "interventions" / "intervention-ledger.jsonl").exists())
            self.assertTrue((root / "effect-gates" / "effect-gate-ledger.jsonl").exists())
            self.assertTrue((root / "mechanisms" / "mechanism-library.jsonl").exists())

            mechanisms = research_loop.read_jsonl(root / "mechanisms" / "mechanism-library.jsonl")
            self.assertEqual(mechanisms[-1]["hypothesis_id"], payload["hypothesis"]["id"])
            self.assertEqual(mechanisms[-1]["status"], "candidate")

    def test_mcp_maps_ophi_tools(self):
        observe = mcp_server.tool_to_cli(
            "research_loop_observe",
            {
                "cwd": "C:\\project",
                "text": "Observed a recurring evidence gap.",
                "kind": "evidence_gap",
                "stage": "LITERATURE",
                "subchain": "P2",
                "tags": ["citation"],
                "write": True,
            },
        )
        cycle = mcp_server.tool_to_cli(
            "research_loop_ophi_cycle",
            {
                "cwd": "C:\\project",
                "observation": "Observed unstable figure gate.",
                "problem": "Figure readiness hides uncertainty.",
                "hypothesis": "The analysis gate is too shallow.",
                "intervention": "Add a variance audit.",
                "expected_effect": "Gate routes back to P6.",
                "validation": "Replay two harness reports.",
                "subchain": "P6",
                "format": "json",
                "write": True,
            },
        )
        mechanism = mcp_server.tool_to_cli(
            "research_loop_mechanism",
            {
                "cwd": "C:\\project",
                "mechanism": "Variance gates prevent premature writing promotion.",
                "status": "supported",
                "scope": "analysis-stage gates",
                "negative_result": True,
                "write": True,
            },
        )

        self.assertEqual(observe[:3], ["--cwd", "C:\\project", "observe"])
        self.assertIn("--text", observe)
        self.assertIn("--tag", observe)
        self.assertIn("--write", observe)
        self.assertEqual(cycle[:3], ["--cwd", "C:\\project", "ophi-cycle"])
        self.assertIn("--expected-effect", cycle)
        self.assertIn("--validation", cycle)
        self.assertIn("--write", cycle)
        self.assertEqual(mechanism[:3], ["--cwd", "C:\\project", "mechanism"])
        self.assertIn("--negative-result", mechanism)

    def test_route_adds_research_experiment_harness_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            research_loop.init_project(cwd)
            state = research_loop.load_state(cwd)
            passport = research_loop.load_passport(cwd, state)

            graph = research_loop.build_route_graph(cwd, state, passport, "run analysis and compare metrics against the baseline")

        self.assertEqual(graph["execution_profile"]["id"], "research_experiment_loop")
        self.assertIn("metric and target-transform lock", graph["harness_protocol"]["validation_surfaces"])
        self.assertIn("deep-loop consumes pass/fail", "; ".join(graph["harness_protocol"]["integration_points"]))
        self.assertTrue(any("Lock metric definitions" in item for item in graph["harness_protocol"]["guardrails"]))

    def test_deep_loop_continuation_inherits_harness_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = research_loop.build_deep_loop_payload(
                deep_args(
                    intent="write manuscript with citations and formula preservation",
                    current_subchain="P7",
                    next_subchain=["P8"],
                    result_summary="Draft and citation pass completed.",
                    artifact=["manuscripts/draft.md"],
                ),
                Path(tmp),
                minimal_state("WRITING"),
                minimal_passport(),
            )

        harness = payload["continuation_contract"]["harness_protocol"]
        self.assertEqual(harness["execution_profile"], "manuscript_artifact_loop")
        self.assertIn("formula/text preservation audit", harness["validation_surfaces"])
        self.assertIn("weighted_score", harness["feedback_summary"]["preferred_metrics"])
        self.assertIn("Harness protocol", payload["continuation_contract"]["next_work_prompt"])

    def test_harness_report_failure_drives_retry_gate_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "harness-report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "selected_candidate": "candidate-a",
                        "evaluations": [
                            {
                                "candidate": {"name": "candidate-a"},
                                "summary": {
                                    "case_count": 3,
                                    "pass_count": 2,
                                    "pass_rate": 2 / 3,
                                    "weighted_score": 0.72,
                                    "failures_by_tag": {"formula": 1},
                                    "avg_latency_ms": 12.5,
                                },
                                "results": [
                                    {"case_id": "display-math-count", "passed": True, "score": 1.0, "tags": ["formula"]},
                                    {"case_id": "inline-math-missing", "passed": False, "score": 0.0, "tags": ["formula"], "error": "missing inline math"},
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = research_loop.build_deep_loop_payload(
                deep_args(
                    intent="write manuscript with citations and formula preservation",
                    current_subchain="P7",
                    next_subchain=["P8"],
                    gate_result="auto",
                    harness_report=[str(report_path)],
                    result_summary="",
                    artifact=[],
                    round_index=1,
                    max_rounds=3,
                ),
                Path(tmp),
                minimal_state("WRITING"),
                minimal_passport(),
            )

        self.assertEqual(payload["gate_input"]["effective_gate_result"], "fail")
        self.assertEqual(payload["gate"]["decision"], "retry_same_route")
        self.assertEqual(payload["harness_evidence"]["failures_by_tag"], {"formula": 1})
        self.assertIn("Harness evidence did not pass", "\n".join(payload["gate_input"]["manual_issues"]))
        self.assertIn(str(report_path), payload["gate_input"]["artifacts"])

    def test_harness_report_pass_routes_next_with_evidence_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "harness-pass.json"
            report_path.write_text(
                json.dumps(
                    {
                        "summary": {
                            "case_count": 4,
                            "pass_count": 4,
                            "pass_rate": 1.0,
                            "weighted_score": 0.96,
                            "failures_by_tag": {},
                            "avg_latency_or_runtime": 1.2,
                        }
                    }
                ),
                encoding="utf-8",
            )

            payload = research_loop.build_deep_loop_payload(
                deep_args(
                    intent="run analysis and compare metrics against the baseline",
                    current_subchain="P5",
                    next_subchain=["P6"],
                    gate_result="auto",
                    harness_report=[str(report_path)],
                    result_summary="",
                    artifact=[],
                ),
                Path(tmp),
                minimal_state("EXECUTION"),
                minimal_passport(),
            )

        self.assertEqual(payload["gate_input"]["effective_gate_result"], "pass")
        self.assertEqual(payload["gate"]["decision"], "route_next")
        self.assertAlmostEqual(payload["gate"]["quality_score"], 0.96)
        self.assertIn(str(report_path), payload["continuation_contract"]["artifact_refs"])

    def test_every_subchain_has_head_agent_contract(self):
        self.assertEqual(set(research_loop.SUBCHAIN_AGENT_SPECS), set(research_loop.DEEP_LOOP_SUBCHAIN_BY_ID))
        for subchain_id, spec in research_loop.SUBCHAIN_AGENT_SPECS.items():
            self.assertTrue(spec["agent_id"].startswith(subchain_id.lower()))
            self.assertEqual(spec["subchain_id"], subchain_id)
            self.assertTrue(spec["mission"])
            self.assertTrue(spec["entry_read"])
            self.assertTrue(spec["quality_vector"])
            self.assertTrue(spec["handoff_contract"])

    def test_deep_loop_builds_research_council_with_rich_expert_cards(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="assess whether the proposed astronomy claim is novel and supported",
                current_subchain="P3",
                next_subchain=["P7"],
                gate_result="auto",
                gate_issue=["novelty is unclear", "one core claim is unsupported by source evidence"],
                result_summary="A preliminary claim map exists, but counterevidence is not resolved.",
            ),
            ROOT,
            minimal_state("SYNTHESIS"),
            minimal_passport(),
        )

        council = payload["research_council"]
        self.assertGreaterEqual(len(council["experts"]), 6)
        expert_ids = {expert["expert_id"] for expert in council["experts"]}
        self.assertIn("domain_pi", expert_ids)
        self.assertIn("skeptical_reviewer", expert_ids)
        self.assertIn("novelty_assessor", expert_ids)
        for expert in council["experts"]:
            self.assertTrue(expert["role"])
            self.assertTrue(expert["domain_scope"])
            self.assertTrue(expert["required_reads"])
            self.assertTrue(expert["diagnostic_frame"])
            self.assertTrue(expert["red_flags"])
            self.assertTrue(expert["output_contract"])
        self.assertTrue(council["independent_review_contracts"])
        self.assertTrue(council["cross_critique_contract"])
        self.assertTrue(council["synthesis_contract"])

    def test_adversarial_gate_flags_premature_convergence_for_late_review(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="finalize a research report after review",
                current_subchain="P8",
                next_subchain=["P9"],
                gate_result="pass",
                result_summary="Review looks acceptable.",
                artifact=[],
            ),
            ROOT,
            minimal_state("REVIEW"),
            minimal_passport(),
        )

        adversarial = payload["adversarial_gate"]
        self.assertIn(adversarial["premature_convergence_risk"], {"medium", "high"})
        self.assertTrue(adversarial["killer_tests"])
        self.assertTrue(adversarial["missing_counterfactuals"])

    def test_arbiter_marks_unsupported_evidence_as_evidence_gap_route(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="prepare the report draft for review",
                current_subchain="P7",
                next_subchain=["P8"],
                gate_result="pass",
                gate_issue=["unsupported claim remains", "missing source locator for a key citation"],
                result_summary="Draft is formatted, but citation support is incomplete.",
                artifact=["reports/draft.md"],
            ),
            ROOT,
            minimal_state("WRITING"),
            minimal_passport(),
        )

        arbiter = payload["arbiter"]
        self.assertEqual(arbiter["semantic_reason"], "evidence_gap_route")
        self.assertIn(payload["gate"]["decision"], {"retry_same_route", "escalate_problem_loop"})
        self.assertTrue({"P2", "P10"} & set(arbiter["route_recommendation"]["target_subchains"]))
        self.assertIn("evidence_gap_route", payload["continuation_contract"]["arbiter_findings"]["semantic_reason"])

    def test_deep_loop_markdown_includes_council_adversarial_and_arbiter_sections(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="review a thin claim synthesis",
                current_subchain="P3",
                next_subchain=["P7"],
                gate_result="pass",
                gate_issue=["alternative explanations are missing"],
                result_summary="Claims were drafted without a counterargument matrix.",
            ),
            ROOT,
            minimal_state("SYNTHESIS"),
            minimal_passport(),
        )

        markdown = "\n".join(research_loop.deep_loop_markdown(payload))
        self.assertIn("## Research Council", markdown)
        self.assertIn("## Adversarial Gate", markdown)
        self.assertIn("## Arbiter", markdown)
        self.assertIn("skeptical_reviewer", markdown)

    def test_p6_pass_without_analysis_artifact_escalates_to_problem_loop(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(current_subchain="P6", next_subchain=["P7"], result_summary="", artifact=[]),
            ROOT,
            minimal_state("ANALYSIS"),
            minimal_passport(),
        )

        self.assertEqual(payload["subchain_agent"]["agent_id"], "p6_analysis_figure_head_agent")
        self.assertEqual(payload["gate_vector"]["artifact_readiness"]["level"], "high")
        self.assertEqual(payload["gate"]["decision"], "escalate_problem_loop")
        self.assertEqual(payload["continuation_contract"]["target_subchains"], ["P10"])

    def test_p5_pass_with_run_log_routes_next_without_expert_escalation(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="execute reproducibility command",
                current_subchain="P5",
                next_subchain=["P6"],
                result_summary="Command completed and run log was captured.",
                artifact=[".research-loop/runs/round-01/test.log"],
            ),
            ROOT,
            minimal_state("EXECUTION"),
            minimal_passport(),
        )

        self.assertEqual(payload["subchain_agent"]["agent_id"], "p5_execution_head_agent")
        self.assertEqual(payload["gate"]["decision"], "route_next")
        self.assertEqual(payload["continuation_contract"]["target_subchains"], ["P6"])

    def test_route_next_prompt_embeds_target_head_agent_contract(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="execute reproducibility command",
                current_subchain="P5",
                next_subchain=["P6"],
                result_summary="Command completed and run log was captured.",
                artifact=[".research-loop/runs/round-01/test.log"],
            ),
            ROOT,
            minimal_state("EXECUTION"),
            minimal_passport(),
        )

        prompt = payload["continuation_contract"]["next_work_prompt"]
        self.assertIn("Subchain Head Agent Contract", prompt)
        self.assertIn("p6_analysis_figure_head_agent", prompt)
        self.assertIn("Required outputs", prompt)
        self.assertIn("analysis report", prompt)
        self.assertIn("Harness protocol", prompt)
        self.assertIn("wrapped command run log", prompt)

    def test_retry_same_route_prompt_keeps_original_task_and_harness(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(
                intent="run analysis and compare metrics against the baseline",
                current_subchain="P5",
                next_subchain=["P6"],
                gate_result="fail",
                gate_issue=["metric report is missing"],
                result_summary="Validation did not produce a metric report.",
                round_index=1,
                max_rounds=3,
            ),
            ROOT,
            minimal_state("EXECUTION"),
            minimal_passport(),
        )

        prompt = payload["continuation_contract"]["next_work_prompt"]
        self.assertEqual(payload["gate"]["decision"], "retry_same_route")
        self.assertIn("Project Task And Harness", prompt)
        self.assertIn("Harness protocol", prompt)
        self.assertIn("failures_by_tag", prompt)
        self.assertIn("metric and target-transform lock", prompt)

    def test_problem_escalation_prompt_embeds_p10_head_agent_contract(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(current_subchain="P6", next_subchain=["P7"], result_summary="", artifact=[]),
            ROOT,
            minimal_state("ANALYSIS"),
            minimal_passport(),
        )

        prompt = payload["continuation_contract"]["next_work_prompt"]
        self.assertIn("Subchain Head Agent Contract", prompt)
        self.assertIn("p10_problem_expert_head_agent", prompt)
        self.assertIn("isolated lab diagnosis", prompt)
        self.assertIn("Original Project Task And Harness", prompt)
        self.assertIn("Harness protocol", prompt)

    def test_auto_loop_problem_escalation_problem_includes_gate_vector_context(self):
        payload = research_loop.build_deep_loop_payload(
            deep_args(current_subchain="P6", next_subchain=["P7"], result_summary="", artifact=[]),
            ROOT,
            minimal_state("ANALYSIS"),
            minimal_passport(),
        )

        problem = research_loop.auto_loop_problem_statement("analyze outputs", payload, [])

        self.assertIn("Gate vector blocking dimensions", problem)
        self.assertIn("artifact_readiness", problem)
        self.assertIn("Continuation contract", problem)
        self.assertIn("p10_problem_expert_head_agent", problem)
        self.assertIn("Harness protocol", problem)
        self.assertIn("execution_profile", problem)
        self.assertIn("feedback_metrics", problem)

    def test_mcp_auto_loop_maps_unattended_route_options(self):
        command = mcp_server.tool_to_cli(
            "research_loop_auto_loop",
            {
                "cwd": "D:\\Project",
                "goal": "complete the project",
                "auto_route_next": True,
                "allow_unbounded_routes": True,
                "route_depth_budget": 8,
                "route_agent": "none",
                "route_agent_commands": ["cmd /c echo {subchain}"],
                "harness_reports": ["reports\\harness.json"],
                "route_codex_sandbox": "workspace-write",
                "route_codex_approval": "never",
                "allow_unbounded_resumes": True,
            },
        )

        self.assertIn("auto-loop-watchdog", command)
        self.assertNotIn("auto-loop", command)
        self.assertIn("--auto-route-next", command)
        self.assertIn("--allow-unbounded-routes", command)
        self.assertIn("--allow-unbounded-resumes", command)
        self.assertEqual(command[command.index("--route-depth-budget") + 1], "8")
        self.assertEqual(command[command.index("--route-agent") + 1], "none")
        self.assertIn("--route-agent-command", command)
        self.assertIn("--harness-report", command)
        self.assertEqual(command[command.index("--harness-report") + 1], "reports\\harness.json")

    def test_mcp_deep_loop_maps_harness_reports(self):
        command = mcp_server.tool_to_cli(
            "research_loop_deep_loop",
            {
                "cwd": "D:\\Project",
                "intent": "run analysis",
                "current_subchain": "P5",
                "next_subchains": ["P6"],
                "gate_result": "auto",
                "harness_reports": ["reports\\summary.json", "reports\\cases.json"],
                "format": "json",
            },
        )

        self.assertIn("deep-loop", command)
        report_positions = [index for index, value in enumerate(command) if value == "--harness-report"]
        self.assertEqual(len(report_positions), 2)
        self.assertEqual(command[report_positions[0] + 1], "reports\\summary.json")
        self.assertEqual(command[report_positions[1] + 1], "reports\\cases.json")

    def test_mcp_deep_loop_maps_council_and_adversarial_skip_flags(self):
        command = mcp_server.tool_to_cli(
            "research_loop_deep_loop",
            {
                "cwd": "D:\\Project",
                "intent": "debug legacy gate behavior",
                "current_subchain": "P3",
                "skip_research_council": True,
                "skip_adversarial_gate": True,
            },
        )

        self.assertIn("--skip-research-council", command)
        self.assertIn("--skip-adversarial-gate", command)

    def test_mcp_auto_loop_legacy_mode_keeps_bare_auto_loop(self):
        command = mcp_server.tool_to_cli(
            "research_loop_auto_loop",
            {
                "cwd": "D:\\Project",
                "goal": "legacy compatibility smoke",
                "test_commands": ["python -m pytest -q"],
                "legacy_auto_loop": True,
            },
        )

        self.assertIn("auto-loop", command)
        self.assertNotIn("auto-loop-watchdog", command)

    def test_mcp_auto_loop_resume_maps_latest_and_route_options(self):
        command = mcp_server.tool_to_cli(
            "research_loop_auto_loop_resume",
            {
                "cwd": "D:\\Project",
                "latest": True,
                "extra_rounds": 7,
                "extra_route_depth": 4,
                "route_agent": "none",
                "route_agent_commands": ["cmd /c echo resume"],
                "format": "json",
            },
        )

        self.assertIn("auto-loop-resume", command)
        self.assertIn("--latest", command)
        self.assertEqual(command[command.index("--extra-rounds") + 1], "7")
        self.assertEqual(command[command.index("--extra-route-depth") + 1], "4")
        self.assertEqual(command[command.index("--route-agent") + 1], "none")
        self.assertIn("--route-agent-command", command)

    def test_mcp_auto_loop_watchdog_maps_resume_options(self):
        command = mcp_server.tool_to_cli(
            "research_loop_auto_loop_watchdog",
            {
                "cwd": "D:\\Project",
                "goal": "finish unattended run",
                "test_commands": ["python -m pytest -q"],
                "current_subchain": "P5",
                "next_subchains": ["P6"],
                "route_agent": "none",
                "route_agent_commands": ["cmd /c echo route"],
                "route_agent_idle_timeout": 120,
                "max_resumes": 3,
                "allow_unbounded_resumes": True,
                "resume_extra_rounds": 5,
                "resume_extra_route_depth": 2,
                "poll_seconds": 0.2,
                "format": "json",
            },
        )

        self.assertIn("auto-loop-watchdog", command)
        self.assertEqual(command[command.index("--goal") + 1], "finish unattended run")
        self.assertEqual(command[command.index("--route-agent-idle-timeout") + 1], "120")
        self.assertEqual(command[command.index("--max-resumes") + 1], "3")
        self.assertIn("--allow-unbounded-resumes", command)
        self.assertEqual(command[command.index("--resume-extra-rounds") + 1], "5")
        self.assertEqual(command[command.index("--resume-extra-route-depth") + 1], "2")

    def test_mcp_auto_loop_watchdog_maps_external_supervisor_options(self):
        command = mcp_server.tool_to_cli(
            "research_loop_auto_loop_watchdog",
            {
                "cwd": "D:\\Project",
                "goal": "finish unattended run",
                "external_supervisor": "deepseek",
                "external_supervisor_model": "deepseek-v4-pro",
                "external_supervisor_timeout": 7,
                "external_supervisor_base_url": "https://api.deepseek.com",
            },
        )

        self.assertIn("--external-supervisor", command)
        self.assertEqual(command[command.index("--external-supervisor") + 1], "deepseek")
        self.assertEqual(command[command.index("--external-supervisor-model") + 1], "deepseek-v4-pro")
        self.assertEqual(command[command.index("--external-supervisor-timeout") + 1], "7")
        self.assertEqual(command[command.index("--external-supervisor-base-url") + 1], "https://api.deepseek.com")

    def test_watchdog_treats_unattended_continuation_contract_as_resumable(self):
        payload = {
            "status": "problem-loop-escalated",
            "rounds": [
                {
                    "round": 1,
                    "subchain": "P5",
                    "deep_loop": {
                        "decision": "route_next",
                        "target_subchains": ["P6"],
                        "continuation_contract": {
                            "decision": "route_next",
                            "target_subchains": ["P6"],
                            "next_work_prompt": "Run P6 analysis.",
                            "unattended_safe": True,
                            "requires_human": False,
                        },
                    },
                }
            ],
        }

        self.assertTrue(research_loop.watchdog_child_is_resumable("problem-loop-escalated", payload))

    def test_external_supervisor_skips_without_api_key_and_preserves_local_decision(self):
        child_payload = {
            "status": "route-depth-budget-exhausted",
            "goal": "resume safely",
            "rounds": [
                {
                    "round": 1,
                    "subchain": "P5",
                    "goal": "resume safely",
                    "status": "route-depth-budget-exhausted",
                    "auto_route": {
                        "decision": "route_next",
                        "to_subchain": "P6",
                        "next_goal": "continue into analysis",
                    },
                }
            ],
        }
        args = argparse.Namespace(
            external_supervisor="deepseek",
            external_supervisor_model="deepseek-v4-flash",
            external_supervisor_base_url="https://api.deepseek.com",
            external_supervisor_timeout=1,
            external_supervisor_max_chars=4000,
            external_supervisor_reasoning_effort="high",
        )

        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(research_loop, "read_windows_user_environment_variable", return_value=""):
                review = research_loop.external_supervisor_review(
                    args,
                    Path(tmp),
                    attempt_index=1,
                    goal="resume safely",
                    source_status="route-depth-budget-exhausted",
                    child_payload=child_payload,
                    local_resumable=True,
                )

        self.assertEqual(review["status"], "skipped")
        self.assertEqual(review["provider"], "deepseek")
        self.assertTrue(review["fail_open"])
        self.assertTrue(review["local_resumable"])
        self.assertEqual(review["effective_resumable"], True)
        self.assertNotIn("api_key", json.dumps(review).lower())

    def test_external_supervisor_api_failure_is_fail_open_and_sanitized(self):
        child_payload = {
            "status": "route-agent-timeout",
            "goal": "resume safely",
            "rounds": [
                {
                    "round": 1,
                    "subchain": "P5",
                    "goal": "resume safely",
                    "status": "route-agent-timeout",
                    "auto_route": {
                        "decision": "route_next",
                        "to_subchain": "P6",
                        "next_goal": "continue into analysis",
                    },
                }
            ],
        }
        args = argparse.Namespace(
            external_supervisor="deepseek",
            external_supervisor_model="deepseek-v4-flash",
            external_supervisor_base_url="https://api.deepseek.com",
            external_supervisor_timeout=1,
            external_supervisor_max_chars=4000,
            external_supervisor_reasoning_effort="high",
        )

        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"DEEPSEEK_API_KEY": "dummy-token"}, clear=True):
            with mock.patch.object(research_loop.urllib.request, "urlopen", side_effect=research_loop.urllib.error.URLError("boom")):
                review = research_loop.external_supervisor_review(
                    args,
                    Path(tmp),
                    attempt_index=1,
                    goal="resume safely",
                    source_status="route-agent-timeout",
                    child_payload=child_payload,
                    local_resumable=True,
                )

        serialized = json.dumps(review)
        self.assertEqual(review["status"], "failed")
        self.assertTrue(review["fail_open"])
        self.assertTrue(review["effective_resumable"])
        self.assertNotIn("dummy-token", serialized)

    def test_external_supervisor_reads_windows_user_env_fallback_without_leaking_token(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                decision = {
                    "recommendation": "route_next",
                    "confidence": 0.91,
                    "unattended_safe": True,
                    "requires_human": False,
                    "reasons": ["local continuation is executable"],
                    "risk_flags": [],
                    "next_prompt_patch": "",
                }
                payload = {"choices": [{"message": {"content": json.dumps(decision)}}]}
                return json.dumps(payload).encode("utf-8")

        child_payload = {
            "status": "route-depth-budget-exhausted",
            "goal": "resume safely",
            "rounds": [
                {
                    "round": 1,
                    "subchain": "P5",
                    "goal": "resume safely",
                    "status": "route-depth-budget-exhausted",
                    "auto_route": {
                        "decision": "route_next",
                        "to_subchain": "P6",
                        "next_goal": "continue into analysis",
                    },
                }
            ],
        }
        args = argparse.Namespace(
            external_supervisor="deepseek",
            external_supervisor_model="deepseek-v4-flash",
            external_supervisor_base_url="https://api.deepseek.com",
            external_supervisor_timeout=1,
            external_supervisor_max_chars=4000,
            external_supervisor_reasoning_effort="high",
        )

        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(research_loop, "read_windows_user_environment_variable", return_value="dummy-token", create=True):
                with mock.patch.object(research_loop.urllib.request, "urlopen", return_value=FakeResponse()) as urlopen:
                    review = research_loop.external_supervisor_review(
                        args,
                        Path(tmp),
                        attempt_index=1,
                        goal="resume safely",
                        source_status="route-depth-budget-exhausted",
                        child_payload=child_payload,
                        local_resumable=True,
                    )

        serialized = json.dumps(review)
        self.assertEqual(review["status"], "ok")
        self.assertTrue(urlopen.called)
        self.assertTrue(review["effective_resumable"])
        self.assertNotIn("dummy-token", serialized)

    def test_watchdog_unbounded_resumes_ignore_resume_count_cap(self):
        args = argparse.Namespace(max_resumes=1, allow_unbounded_resumes=True)

        self.assertTrue(research_loop.watchdog_resume_allowed(args, resume_count=99))

    def test_run_auto_command_kills_idle_executor_and_records_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = Path(tmp) / "round"
            result = research_loop.run_auto_command(
                Path(tmp),
                round_dir,
                "route-executor",
                f'"{sys.executable}" -c "import time; time.sleep(5)"',
                1,
                idle_timeout_seconds=0.25,
                poll_interval_seconds=0.05,
            )

            self.assertTrue(result["timed_out"])
            self.assertEqual(result["timeout_reason"], "idle")
            self.assertNotEqual(result["exit_code"], 0)
            self.assertLess(result["elapsed_seconds"], 3)
            self.assertTrue(Path(result["stdout_log"]).exists())

    def test_auto_loop_no_auto_route_reports_handoff_required_not_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop",
                    "--goal",
                    "handoff smoke",
                    "--skip-validate",
                    "--test-command",
                    "cmd /c exit /b 0",
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--no-auto-route-next",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "route-next-handoff-required")
            self.assertNotEqual(payload["status"], "passed")
            self.assertIn("P6", payload["final_message"])

    def test_auto_loop_failed_route_agent_is_reported_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop",
                    "--goal",
                    "route executor smoke",
                    "--skip-validate",
                    "--test-command",
                    "cmd /c exit /b 0",
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--route-agent",
                    "none",
                    "--route-agent-command",
                    "cmd /c exit /b 7",
                    "--route-depth-budget",
                    "1",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "route-agent-failed")
            self.assertEqual(payload["rounds"][0]["status"], "route-next-auto-started")
            self.assertEqual(payload["rounds"][1]["subchain"], "P6")
            self.assertEqual(payload["rounds"][1]["status"], "route-agent-failed")
            self.assertEqual(payload["rounds"][1]["executors"][0]["exit_code"], 7)
            self.assertIn("P6", payload["final_message"])

    def test_auto_loop_timed_out_route_agent_is_reported_as_resumable_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop",
                    "--goal",
                    "route executor timeout smoke",
                    "--skip-validate",
                    "--test-command",
                    "cmd /c exit /b 0",
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--route-agent",
                    "none",
                    "--route-agent-command",
                    f'"{sys.executable}" -c "import time; time.sleep(5)"',
                    "--route-agent-idle-timeout",
                    "0.25",
                    "--route-agent-poll-seconds",
                    "0.05",
                    "--route-depth-budget",
                    "1",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "route-agent-timeout")
            self.assertEqual(payload["rounds"][1]["status"], "route-agent-timeout")
            self.assertTrue(payload["rounds"][1]["executors"][0]["timed_out"])
            self.assertEqual(payload["rounds"][1]["executors"][0]["timeout_reason"], "idle")

    def test_auto_loop_retry_same_route_runs_agent_before_next_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "retry-marker.txt"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop",
                    "--goal",
                    "retry same route smoke",
                    "--skip-validate",
                    "--test-command",
                    f'cmd /c if exist "{marker}" (exit /b 0) else (exit /b 1)',
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--route-agent",
                    "none",
                    "--route-agent-command",
                    f'cmd /c echo retry > "{marker}"',
                    "--route-depth-budget",
                    "0",
                    "--max-rounds",
                    "3",
                    "--deep-loop-max-rounds",
                    "3",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["rounds"][0]["deep_loop"]["decision"], "retry_same_route")
            self.assertEqual(payload["rounds"][0]["status"], "retry-same-route-auto-started")
            self.assertEqual(payload["rounds"][1]["subchain"], "P5")
            self.assertEqual(payload["rounds"][1]["executors"][0]["exit_code"], 0)
            self.assertEqual(payload["rounds"][1]["tests"][0]["exit_code"], 0)
            self.assertTrue(marker.exists())

    def test_auto_loop_approved_problem_loop_continues_into_p10(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop",
                    "--goal",
                    "problem continuation smoke",
                    "--skip-validate",
                    "--test-command",
                    "cmd /c exit /b 0",
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--route-agent",
                    "none",
                    "--route-agent-command",
                    "cmd /c exit /b 0",
                    "--route-depth-budget",
                    "1",
                    "--max-rounds",
                    "4",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["rounds"][0]["status"], "route-next-auto-started")
            self.assertEqual(payload["rounds"][1]["deep_loop"]["decision"], "escalate_problem_loop")
            self.assertEqual(payload["rounds"][1]["problem_loop"]["gate_status"], "approved")
            self.assertEqual(payload["rounds"][1]["status"], "problem-loop-auto-started")
            self.assertEqual(payload["rounds"][2]["subchain"], "P10")
            self.assertEqual(payload["rounds"][2]["executors"][0]["exit_code"], 0)

    def test_auto_loop_resume_restarts_budget_exhausted_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop",
                    "--goal",
                    "resume route budget smoke",
                    "--skip-validate",
                    "--test-command",
                    "cmd /c exit /b 0",
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--route-agent",
                    "none",
                    "--route-depth-budget",
                    "0",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )
            first_payload = json.loads(first.stdout)
            self.assertEqual(first_payload["status"], "route-depth-budget-exhausted")

            marker = Path(tmp) / "resume-marker.txt"
            resumed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop-resume",
                    "--latest",
                    "--extra-rounds",
                    "2",
                    "--extra-route-depth",
                    "0",
                    "--route-agent",
                    "none",
                    "--route-agent-command",
                    f'cmd /c echo resumed > "{marker}"',
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(resumed.returncode, 0)
            payload = json.loads(resumed.stdout)
            self.assertEqual(payload["rounds"][0]["subchain"], "P6")
            self.assertEqual(payload["rounds"][0]["executors"][0]["exit_code"], 0)
            self.assertTrue(marker.exists())
            self.assertEqual(payload["resume"]["source_status"], "route-depth-budget-exhausted")

    def test_auto_loop_watchdog_resumes_resumable_auto_loop_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "watchdog-marker.txt"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "research_loop.py"),
                    "--cwd",
                    tmp,
                    "auto-loop-watchdog",
                    "--goal",
                    "watchdog resume smoke",
                    "--skip-validate",
                    "--test-command",
                    "cmd /c exit /b 0",
                    "--current-subchain",
                    "P5",
                    "--next-subchain",
                    "P6",
                    "--route-agent",
                    "none",
                    "--route-agent-command",
                    f'cmd /c echo watched > "{marker}"',
                    "--route-depth-budget",
                    "0",
                    "--resume-extra-rounds",
                    "2",
                    "--resume-extra-route-depth",
                    "0",
                    "--max-resumes",
                    "1",
                    "--poll-seconds",
                    "0.05",
                    "--format",
                    "json",
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )

            payload = json.loads(proc.stdout)
            self.assertGreaterEqual(payload["attempt_count"], 2)
            self.assertEqual(payload["resume_count"], 1)
            self.assertEqual(payload["attempts"][0]["kind"], "auto-loop")
            self.assertEqual(payload["attempts"][0]["source_status"], "route-depth-budget-exhausted")
            self.assertEqual(payload["attempts"][1]["kind"], "auto-loop-resume")
            self.assertTrue(marker.exists())

    def test_persisted_deep_loop_decision_records_gate_vector_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            research_loop.init_project(cwd)
            state = research_loop.load_state(cwd)
            passport = research_loop.load_passport(cwd, state)
            payload = research_loop.build_deep_loop_payload(
                deep_args(current_subchain="P6", next_subchain=["P7"], result_summary="", artifact=[]),
                cwd,
                state,
                passport,
            )

            research_loop.persist_deep_loop_payload(cwd, state, passport, payload, source="test")
            decisions = research_loop.read_jsonl(research_loop.decisions_path(cwd))
            record = [item for item in decisions if item.get("type") == "deep_loop_gate"][-1]

            self.assertIn("gate_vector_summary", record)
            self.assertEqual(record["gate_vector_summary"]["artifact_readiness"], "high")
            self.assertIn("artifact_readiness", record["blocking_dimensions"])


if __name__ == "__main__":
    unittest.main()
