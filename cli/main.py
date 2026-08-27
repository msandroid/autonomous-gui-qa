"""
Main CLI Entrypoint for Autonomous GUI QA.
"""

import argparse
import sys
import os
from autonomous_gui_qa.engine.vlm import VLMEngine
from autonomous_gui_qa.engine.agent import AutonomousGUIAgent
from autonomous_gui_qa.engine.oracle import VisualOracle
from autonomous_gui_qa.drivers.ios_simulator import IOSSimulatorDriver
from autonomous_gui_qa.drivers.android_device import AndroidDeviceDriver
from autonomous_gui_qa.reporting.reporter import QAReporter
from autonomous_gui_qa.scenarios.runner import ScenarioRunner

def main():
    parser = argparse.ArgumentParser(description="Autonomous Mobile GUI Exploration & VLM Visual QA")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: explore
    p_explore = subparsers.add_parser("explore", help="Autonomous exploration or goal pursuit")
    p_explore.add_argument("--platform", choices=["ios", "android"], default="ios")
    p_explore.add_argument("--bundle-id", required=False, help="App bundle ID / package name")
    p_explore.add_argument("--goal", required=True, help="Natural language goal for the agent")
    p_explore.add_argument("--max-steps", type=int, default=10)
    p_explore.add_argument("--provider", choices=["gemini", "claude", "openai"], default="gemini")
    p_explore.add_argument("--output-dir", default="reports")

    # Command: scenario
    p_scen = subparsers.add_parser("scenario", help="Run declarative YAML scenario")
    p_scen.add_argument("--file", required=True, help="Path to scenario YAML file")
    p_scen.add_argument("--platform", choices=["ios", "android"], default="ios")
    p_scen.add_argument("--provider", choices=["gemini", "claude", "openai"], default="gemini")
    p_scen.add_argument("--output-dir", default="reports")

    # Command: inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect a single screenshot file")
    p_insp.add_argument("--image", required=True, help="Path to screenshot image")
    p_insp.add_argument("--provider", choices=["gemini", "claude", "openai"], default="gemini")
    p_insp.add_argument("--output-dir", default="reports")

    args = parser.parse_args()

    vlm = VLMEngine(provider=args.provider)
    reporter = QAReporter(output_dir=args.output_dir)

    if args.command == "explore":
        driver = IOSSimulatorDriver(bundle_id=args.bundle_id) if args.platform == "ios" else AndroidDeviceDriver()
        agent = AutonomousGUIAgent(driver=driver, vlm_engine=vlm)
        traj = agent.run_goal(args.goal, max_steps=args.max_steps)
        print(f"\n✅ Autonomous run complete. Trajectory recorded: {len(traj)} steps.")

    elif args.command == "scenario":
        driver = IOSSimulatorDriver() if args.platform == "ios" else AndroidDeviceDriver()
        oracle = VisualOracle(vlm)
        runner = ScenarioRunner(driver, oracle)
        results = runner.run_scenario(args.file)
        rep = reporter.generate_report(results, suite_name=f"Scenario: {os.path.basename(args.file)}")
        print(f"\n📊 Report generated: {rep[html]}")
        print(f"📄 Summary generated: {rep[markdown]}")

    elif args.command == "inspect":
        oracle = VisualOracle(vlm)
        res = oracle.audit_screen(args.image)
        rep = reporter.generate_report([{
            "step_name": "inspect",
            "screen_name": os.path.basename(args.image),
            "image_path": args.image,
            "is_passed": res.is_passed,
            "confidence": res.confidence,
            "summary": res.summary,
            "defects": [d.dict() for d in res.defects]
        }], suite_name="Single Screen Inspection")
        print(f"\n📊 Report generated: {rep[html]}")

if __name__ == "__main__":
    main()
