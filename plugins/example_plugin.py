#!/usr/bin/env python3
"""
Example Plugin for ParrotSec AI Assistant v3.0
"""

from typing import Dict, Any

class ExamplePlugin:
    """Example plugin demonstrating the plugin interface"""

    @property
    def name(self) -> str:
        return "example"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "Your Name"

    @property
    def description(self) -> str:
        return "Example plugin demonstrating the plugin system"

    def execute(self, ai_assistant, **kwargs) -> Any:
        """Execute plugin"""
        print("Example plugin executed!")
        print(f"Current target: {ai_assistant.current_target}")
        return {"status": "success", "message": "Example plugin ran successfully"}

    def register_commands(self) -> Dict:
        """Register custom commands"""
        return {
            'example': self.run_example,
            'example_target': self.show_target
        }

    def run_example(self, args: str):
        """Run example command"""
        print(f"Running example with args: {args}")

    def show_target(self, args: str):
        """Show current target"""
        print(f"Current target: {self.ai.current_target}")

# Export plugin class
PluginClass = ExamplePlugin
