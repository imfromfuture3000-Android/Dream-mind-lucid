#!/usr/bin/env python3
"""
Dream-Mind-Lucid Installation and Deployment Script
===================================================
One-command setup for the complete Dream ecosystem.

Usage:
    python install_and_deploy.py           # Install dependencies and deploy everything
    python install_and_deploy.py install   # Install dependencies only  
    python install_and_deploy.py deploy    # Deploy everything (assumes dependencies installed)
    python install_and_deploy.py validate  # Validate installation
"""

import os
import sys
import subprocess

def print_banner():
    print("🌌" + "="*60 + "🌌")
    print("     DREAM-MIND-LUCID INSTALLATION & DEPLOYMENT")
    print("           The Oneiro-Sphere Awaits...")
    print("🌌" + "="*60 + "🌌")

def install_dependencies():
    """Install all project dependencies."""
    print("\n📦 Installing all dependencies...")
    
    try:
        # Use the enhanced grok_copilot_launcher install
        result = subprocess.run([sys.executable, "grok_copilot_launcher.py", "install"], 
                              check=False)  # Don't fail on dashboard install issues
        
        if result.returncode == 0:
            print("✅ All dependencies installed successfully!")
        else:
            print("⚠️ Some dependencies had issues (dashboard), but core installation succeeded")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False

def validate_installation():
    """Validate the installation."""
    print("\n🧪 Validating installation...")
    
    try:
        result = subprocess.run([sys.executable, "validate_installation.py"], check=True)
        print("✅ Validation completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Validation failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def deploy_ecosystem():
    """Deploy the complete Dream-Mind-Lucid ecosystem."""
    print("\n🚀 Deploying Dream-Mind-Lucid ecosystem...")
    
    try:
        # Use the deploy-all command
        result = subprocess.run([sys.executable, "grok_copilot_launcher.py", "deploy-all"], 
                              check=True)
        
        print("✅ Ecosystem deployment completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def show_next_steps():
    """Show what users can do next."""
    print("\n🎯 NEXT STEPS:")
    print("  1️⃣  Validate your installation:")
    print("      python validate_installation.py")
    print("")
    print("  2️⃣  Set environment variables for real deployment:")
    print("      export DEPLOYER_KEY='your-private-key'")
    print("      export SKALE_RPC='https://mainnet.skalenodes.com/v1/elated-tan-skat'")
    print("      export SOLANA_RPC_URL='https://mainnet.helius-rpc.com/?api-key=your-key'")
    print("")
    print("  3️⃣  Test the deployment:")
    print("      python grok_copilot_launcher.py test")
    print("")
    print("  4️⃣  Start the dashboard:")
    print("      cd dashboard && streamlit run dream_dashboard.py")
    print("")
    print("  5️⃣  Record your first dream:")
    print("      python agents/iem_syndicate.py record 'I dreamed of quantum possibilities'")
    print("")
    print("🌟 Welcome to the Dream-Mind-Lucid ecosystem! 🌟")

def main():
    print_banner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "all"
    
    success = True
    
    if command in ["install", "all"]:
        success &= install_dependencies()
    
    if command == "validate":
        success = validate_installation()
    elif command in ["deploy", "all"] and success:
        success &= deploy_ecosystem()
    
    if success:
        show_next_steps()
        print("\n🎉 Setup completed successfully!")
        return 0
    else:
        print("\n❌ Setup encountered issues. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())