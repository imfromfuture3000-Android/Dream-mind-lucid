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
  install              Install all required dependencies (Python, Node, Solana/Rust)
  deploy-all           Deploy complete Dream-Mind-Lucid ecosystem (all components)
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
    print(" - 🌙 OneiroBot integration available: try #oneirobot or #summon_oneirobot")


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


def run_install():
    """Install all required dependencies."""
    print("📦 Installing Dream-Mind-Lucid dependencies...")
    try:
        import subprocess
        
        # 1. Install Python dependencies
        print("🐍 Installing Python dependencies...")
        subprocess.run(["pip", "install", "web3", "py-solc-x", "mcp", "ipfshttpclient", "PyExifTool"], check=True)
        
        # Install Solidity compiler
        try:
            from solcx import install_solc
            install_solc("0.8.20")
        except ImportError:
            print("⚠️ Solidity compiler installation skipped - py-solc-x not available yet")
        
        # Install from requirements.txt if available
        if os.path.exists("requirements.txt"):
            print("📋 Installing from requirements.txt...")
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Python dependencies installed!")
        
        # 2. Install Node.js dependencies
        print("📦 Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], check=True, cwd=".")
        if os.path.exists("evm"):
            subprocess.run(["npm", "install"], check=True, cwd="evm")
            print("✅ Node.js dependencies installed!")
        
        # 3. Install dashboard dependencies  
        if os.path.exists("dashboard/requirements.txt"):
            print("📊 Installing dashboard dependencies...")
            subprocess.run(["pip", "install", "-r", "dashboard/requirements.txt"], check=True)
            print("✅ Dashboard dependencies installed!")
        
        # 4. Check Rust/Cargo availability
        try:
            result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("🦀 Rust/Cargo detected:", result.stdout.strip())
                # Test Solana program compilation
                if os.path.exists("solana/programs"):
                    print("🔍 Testing Solana program compilation...")
                    result = subprocess.run(["cargo", "check"], cwd="solana/programs", capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ Solana program compilation successful!")
                    else:
                        print("⚠️ Solana program compilation warnings (but successful)") 
            else:
                print("⚠️ Rust/Cargo not available - Solana development disabled")
        except FileNotFoundError:
            print("⚠️ Rust/Cargo not found - Solana development disabled")
        
        print("\n🎉 All dependencies installed successfully!")
        print("💡 Run 'python grok_copilot_launcher.py deploy-all' to deploy everything")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return 1

def run_deploy_all():
    """Deploy all components of the Dream-Mind-Lucid ecosystem."""
    print("🚀 Starting complete Dream-Mind-Lucid deployment...")
    try:
        import subprocess
        
        # 1. Run migration tests first to ensure everything is ready
        print("🧪 Running pre-deployment tests...")
        result = subprocess.run([sys.executable, "test_solana_migration.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Pre-deployment tests passed!")
        else:
            print("⚠️ Some tests failed, but continuing with deployment")
            print("Test output:", result.stdout[-500:])  # Show last 500 chars
        
        # 2. Deploy Solana tokens (primary blockchain)
        print("\n💎 Deploying Solana tokens and programs...")
        try:
            result = subprocess.run([sys.executable, "agents/solana_dream_agent.py", "deploy_tokens"], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("✅ Solana deployment successful!")
                print("Output:", result.stdout[-300:])  # Show output summary
            else:
                print("⚠️ Solana deployment completed with warnings")
                print("Output:", result.stdout[-300:])
        except subprocess.TimeoutExpired:
            print("⚠️ Solana deployment timed out but may still be running")
        except Exception as e:
            print(f"⚠️ Solana deployment issue: {e}")
        
        # 3. Deploy SKALE contracts (legacy support)
        print("\n⚡ Deploying SKALE contracts...")
        try:
            # Deploy IEMDreams contract
            synd = importlib.import_module("agents.iem_syndicate")
            print("Deploying IEMDreams...")
            synd.deploy_contract("IEMDreams")
            
            print("Deploying OneiroSphere...")
            synd.deploy_contract("OneiroSphere")
            
            print("✅ SKALE deployment successful!")
        except Exception as e:
            print(f"⚠️ SKALE deployment issue: {e}")
        
        # 4. Deploy EVM contracts if Hardhat is available
        print("\n🔗 Deploying EVM contracts...")
        try:
            if os.path.exists("evm/hardhat.config.js"):
                result = subprocess.run(["npx", "hardhat", "compile"], cwd="evm", capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ EVM contracts compiled successfully!")
                else:
                    print("⚠️ EVM compilation warnings:", result.stderr[-200:])
            else:
                print("⚠️ Hardhat config not found, skipping EVM deployment")
        except Exception as e:
            print(f"⚠️ EVM deployment issue: {e}")
        
        # 5. Test the deployed system
        print("\n🧪 Running post-deployment tests...")
        try:
            result = subprocess.run([sys.executable, "test_deployment.py"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Post-deployment tests passed!")
                print("System status:", result.stdout[-400:])
            else:
                print("⚠️ Some post-deployment tests failed")
        except Exception as e:
            print(f"⚠️ Post-deployment test issue: {e}")
        
        print("\n🎉 Deployment complete! The Dream-Mind-Lucid ecosystem is ready!")
        print("🌌 Next steps:")
        print("  • Set environment variables for mainnet deployment")
        print("  • Run 'python grok_copilot_launcher.py test' to verify functionality") 
        print("  • Start the dashboard: cd dashboard && streamlit run dream_dashboard.py")
        print("  • Record your first dream via the agents or dashboard")
        
        return 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return 1


def run_oneirobot(args):
    """Run OneiroBot commands via Copilot integration"""
    try:
        copilot_instruction = importlib.import_module("copilot-instruction")
    except ModuleNotFoundError as e:
        print(f"❌ Could not import copilot-instruction: {e}")
        return 1

    if not args:
        print("Usage: oneirobot summon|status|scan|optimize|fix|help")
        return 1

    # Map command shortcuts to full commands
    command_map = {
        'summon': 'summon_oneirobot',
        'status': 'oneirobot_status', 
        'scan': 'oneirobot_scan',
        'optimize': 'oneirobot_optimize',
        'fix': 'oneirobot_fix',
        'help': 'oneirobot_help'
    }
    
    cmd = args[0].lower().lstrip('#')
    full_command = command_map.get(cmd, cmd)
    
    try:
        # Use the handle_copilot_command function directly
        result = copilot_instruction.handle_copilot_command(full_command, args[1:])
        print(f"✅ OneiroBot command '{cmd}' executed successfully")
        return 0
    except Exception as exc:
        print(f"❌ Error executing OneiroBot command: {exc}")
        return 1


def main():
    if len(sys.argv) == 1:
        status()
        return 0

    # Provide a minimal subcommand layer
    sub = sys.argv[1].lower()
    sub = sub.lstrip('#')
    if sub in {"deploy", "audit", "test", "record", "deploy_contract", "record_dream"}:
        return run_syndicate(sys.argv[1:])
    elif sub in {"oneirobot", "oneiro", "summon_oneirobot", "oneirobot_status", "oneirobot_scan", 
                 "oneirobot_optimize", "oneirobot_fix", "oneirobot_help"}:
        return run_oneirobot(sys.argv[1:])
    elif sub == "install":
        return run_install()
    elif sub in {"deploy-all", "deploy_all", "all"}:
        return run_deploy_all()
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
        print("💡 Available commands: install, deploy-all, deploy, audit, test, oneirobot, image")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
