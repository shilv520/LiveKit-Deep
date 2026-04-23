"""
Wrapper to run voice agent with UTF-8 encoding fix for Windows
"""
import sys
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Now import and run the main module
import importlib.util
spec = importlib.util.spec_from_file_location('voice_agent', '02_voice_agent.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Run the CLI
if mod.LIVEKIT_AVAILABLE:
    from livekit.agents import cli
    cli.run_app(mod.server)
else:
    print("[ERROR] Please install LiveKit dependencies first")