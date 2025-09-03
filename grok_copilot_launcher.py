#!/usr/bin/env python3
"""
Grok Copilot Launcher (wrapper)
--------------------------------
Lightweight wrapper so you can run:  python grok_copilot_launcher.py
Safely defers heavy imports (ipfs, exiftool, biconomy, MCP) until actually needed.
Use as a friendlier entrypoint around existing tooling in:
  - grok_copilot_image_launcher.py
  - agents/iem_syndicate.py

Commands:
  (no args)            Show status
  deploy <Contract>    Deploy contract via iem_syndicate (IEMDreams | OneiroSphere)
  audit <Contract>     Audit deployed contract
  test                 Run dream recording test

Environment (optional):
  DEPLOYER_KEY, SKALE_RPC, SKALE_CHAIN_ID, FORWARDER_ADDRESS, INFURA_PROJECT_ID
"""
import sys
import importlib
import shutil
import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

def status():
    print("🌌 Grok Copilot Launcher Ready")
    print(" - Python:", sys.version.split()[0])
    print(" - Working Dir:", REPO_ROOT)
    # Lightweight dependency presence checks
    mods = ["web3", "solcx", "ipfshttpclient", "PyExifTool", "mcp"]
    available = []
    for m in mods:
        try:
            importlib.import_module(m if m != "PyExifTool" else "exiftool")
            available.append((m, True))
        except Exception:
            available.append((m, False))
    print(" - Modules:")
    for name, ok in available:
        print(f"    {name:14} {'✅' if ok else '⚠️ missing'}")
    if not any(ok for _, ok in available):
        print("   Tip: pip install -r requirements.txt")
    print(" - Launcher bridging to iem_syndicate & grok_copilot_image_launcher")


def run_syndicate(args):
    try:
        synd = importlib.import_module("agents.iem_syndicate")
    except ModuleNotFoundError as e:
        print(f"❌ Could not import iem_syndicate: {e}")
        return 1

    if not args:
        print("Usage: deploy|audit|test ... (see file header)")
        return 1

    # Re-dispatch to the underlying functions without re-parsing argv globally
    cmd = args[0].lower().lstrip('#')  # allow hashtag style commands
    if cmd == 'deploy_contract':
        cmd = 'deploy'
    if cmd == 'record_dream':
        cmd = 'record'
    try:
        if cmd == "deploy":
            if len(args) < 2:
                print("❌ Specify contract (IEMDreams|OneiroSphere)")
                return 1
            synd.deploy_contract(args[1])
        elif cmd == "audit":
            target = args[1] if len(args) > 1 else "OneiroSphere"
            synd.audit_contract(target)
        elif cmd == "test":
            synd.test_dream_recording()
        else:
            print(f"❌ Unknown command: {cmd}")
            return 1
    except Exception as exc:
        print(f"❌ Error executing syndicate command: {exc}")
        return 1
    return 0


def main():
    if len(sys.argv) == 1:
        status()
        return 0

    # Provide a minimal subcommand layer
    sub = sys.argv[1].lower()
    sub = sub.lstrip('#')
    if sub in {"deploy", "audit", "test", "record", "deploy_contract", "record_dream"}:
        return run_syndicate(sys.argv[1:])
    elif sub == "image":
        # Lazy run of the heavier image launcher
        try:
            mod = importlib.import_module("grok_copilot_image_launcher")
            print("📸 Image launcher module imported. (No auto-run main provided)")
        except Exception as e:
            print(f"❌ Failed to import image launcher: {e}")
            return 1
        return 0
    else:
        print(f"❌ Unknown subcommand: {sub}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
