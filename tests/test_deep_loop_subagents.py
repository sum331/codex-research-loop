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

    def test_every_subchain_has_head_agent_contract(self):
        self.assertEqual(set(research_loop.SUBCHAIN_AGENT_SPECS), set(research_loop.DEEP_LOOP_SUBCHAIN_BY_ID))
        for subchain_id, spec in research_loop.SUBCHAIN_AGENT_SPECS.items():
            self.assertTrue(spec["agent_id"].startswith(subchain_id.lower()))
            self.assertEqual(spec["subchain_id"], subchain_id)
            self.assertTrue(spec["mission"])
            self.assertTrue(spec["entry_read"])
            self.assertTrue(spec["quality_vector"])
            self.assertTrue(spec["handoff_contract"])

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
