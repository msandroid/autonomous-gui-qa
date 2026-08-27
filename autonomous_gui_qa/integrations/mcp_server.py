"""
Standard Model Context Protocol (MCP) Server for Mobile GUI QA & Visual Oracle.
Communicates via JSON-RPC over stdio, compatible with Claude, Cursor, Antigravity, and Windsurf.
"""

import sys
import json
import os
from typing import Dict, Any, List, Optional
from ..engine.vlm import VLMEngine
from ..engine.oracle import VisualOracle
from ..engine.agent import AutonomousGUIAgent
from ..drivers.ios_simulator import IOSSimulatorDriver
from ..drivers.android_device import AndroidDeviceDriver
from ..reporting.reporter import QAReporter
from ..scenarios.runner import ScenarioRunner

TOOLS_METADATA = [
    {
        "name": "run_autonomous_exploration",
        "description": "Runs an autonomous Mobile GUI Agent to achieve a natural language goal on iOS/Android.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Goal for the agent (e.g. Change target language to Spanish)"},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"},
                "bundle_id": {"type": "string", "description": "App bundle ID (e.g. Translate.Blue)"},
                "max_steps": {"type": "integer", "default": 10}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "run_scenario",
        "description": "Executes a declarative YAML test scenario and generates a visual QA report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scenario_file": {"type": "string", "description": "Path to the scenario YAML file"},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"},
                "output_dir": {"type": "string", "default": "reports"}
            },
            "required": ["scenario_file"]
        }
    },
    {
        "name": "mobile_screenshot",
        "description": "Takes a screenshot of the connected iOS Simulator or Android device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "default": "screenshot.png"},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"}
            }
        }
    },
    {
        "name": "vlm_visual_audit",
        "description": "Audits a mobile screenshot using VLM for text truncation, layout clipping, contrast, and UX defects.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Absolute path to screenshot image"},
                "context_prompt": {"type": "string", "description": "Optional context about expected state"}
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "mobile_tap",
        "description": "Taps on the mobile screen at normalized coordinates (0-1000).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate (0-1000)"},
                "y": {"type": "integer", "description": "Y coordinate (0-1000)"},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"}
            },
            "required": ["x", "y"]
        }
    },
    {
        "name": "mobile_type",
        "description": "Types text into the active mobile focus/input field.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text string to type"},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "mobile_swipe",
        "description": "Performs a directional swipe on the mobile device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["UP", "DOWN", "LEFT", "RIGHT"]},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"}
            },
            "required": ["direction"]
        }
    },
    {
        "name": "mobile_set_appearance",
        "description": "Switches the mobile OS appearance between light and dark mode.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["light", "dark"]},
                "platform": {"type": "string", "enum": ["ios", "android"], "default": "ios"}
            },
            "required": ["mode"]
        }
    }
]

class MCPServer:
    """Stdio JSON-RPC MCP Server implementation."""

    def __init__(self):
        self.vlm = VLMEngine()
        self.oracle = VisualOracle(self.vlm)

    def get_driver(self, platform: str, bundle_id: Optional[str] = None):
        if platform == "ios":
            return IOSSimulatorDriver(bundle_id=bundle_id)
        return AndroidDeviceDriver()

    def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        platform = arguments.get("platform", "ios")

        if name == "run_autonomous_exploration":
            driver = self.get_driver(platform, arguments.get("bundle_id"))
            agent = AutonomousGUIAgent(driver=driver, vlm_engine=self.vlm)
            traj = agent.run_goal(arguments["goal"], max_steps=arguments.get("max_steps", 10))
            return {"content": [{"type": "text", "text": f"Exploration completed ({len(traj)} steps recorded)."}]}

        elif name == "run_scenario":
            driver = self.get_driver(platform)
            runner = ScenarioRunner(driver, self.oracle)
            results = runner.run_scenario(arguments["scenario_file"])
            reporter = QAReporter(output_dir=arguments.get("output_dir", "reports"))
            rep = reporter.generate_report(results, suite_name=f"Scenario {arguments[scenario_file]}")
            return {"content": [{"type": "text", "text": f"Scenario complete. Report: {rep[html]}"}]}

        elif name == "mobile_screenshot":
            driver = self.get_driver(platform)
            path = driver.take_screenshot(arguments.get("filename", "screenshot.png"))
            return {"content": [{"type": "text", "text": f"Screenshot saved to: {path}"}]}

        elif name == "vlm_visual_audit":
            res = self.oracle.audit_screen(arguments["image_path"], arguments.get("context_prompt", ""))
            return {"content": [{"type": "text", "text": json.dumps(res.dict(), indent=2)}]}

        elif name == "mobile_tap":
            driver = self.get_driver(platform)
            driver.tap(arguments["x"], arguments["y"])
            return {"content": [{"type": "text", "text": f"Tapped at ({arguments[x]}, {arguments[y]})"}]}

        elif name == "mobile_type":
            driver = self.get_driver(platform)
            driver.type_text(arguments["text"])
            return {"content": [{"type": "text", "text": f"Typed text: {arguments[text]}"}]}

        elif name == "mobile_swipe":
            driver = self.get_driver(platform)
            driver.swipe(arguments["direction"])
            return {"content": [{"type": "text", "text": f"Swiped {arguments[direction]}"}]}

        elif name == "mobile_set_appearance":
            driver = self.get_driver(platform)
            driver.set_appearance(arguments["mode"])
            return {"content": [{"type": "text", "text": f"Appearance set to {arguments[mode]}"}]}

        raise ValueError(f"Unknown tool: {name}")

    def run(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                req_id = req.get("id")
                method = req.get("method")

                if method == "initialize":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "autonomous-gui-qa", "version": "0.1.0"}
                        }
                    }
                elif method == "tools/list":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"tools": TOOLS_METADATA}
                    }
                elif method == "tools/call":
                    params = req.get("params", {})
                    tool_result = self.handle_call_tool(params.get("name"), params.get("arguments", {}))
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": tool_result
                    }
                else:
                    res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_res = {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32603, "message": str(e)}}
                sys.stdout.write(json.dumps(err_res) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    server = MCPServer()
    server.run()
