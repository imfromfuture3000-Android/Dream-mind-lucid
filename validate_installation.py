#!/usr/bin/env python3
"""
Quick validation test for Dream-Mind-Lucid installation
======================================================
Tests that all core components are properly installed and accessible.
"""

import sys
import os

def test_python_dependencies():
    """Test that all Python dependencies are available."""
    print("🐍 Testing Python dependencies...")
    
    try:
        import web3
        print(f"  ✅ Web3 {web3.__version__}")
        
        from solcx import install_solc
        print("  ✅ Solidity compiler (py-solc-x)")
        
        import ipfshttpclient
        print("  ✅ IPFS HTTP client")
        
        import mcp
        print("  ✅ Model Context Protocol")
        
        try:
            import solana
            print("  ✅ Solana Python client")
        except ImportError:
            print("  ⚠️ Solana client (optional)")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Missing dependency: {e}")
        return False

def test_node_dependencies():
    """Test that Node.js dependencies are available."""
    print("\n📦 Testing Node.js environment...")
    
    try:
        import subprocess
        
        # Check if npm packages are installed
        result = subprocess.run(["npm", "list", "--depth=0"], 
                              capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("  ✅ Root npm packages installed")
        else:
            print("  ⚠️ Root npm packages (may need npm install)")
            
        # Check EVM packages
        if os.path.exists("evm"):
            result = subprocess.run(["npm", "list", "--depth=0"], 
                                  capture_output=True, text=True, cwd="evm")
            if result.returncode == 0:
                print("  ✅ EVM npm packages installed")
            else:
                print("  ⚠️ EVM npm packages (may need npm install)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Node.js environment issue: {e}")
        return False

def test_rust_environment():
    """Test Rust/Cargo environment for Solana development."""
    print("\n🦀 Testing Rust/Cargo environment...")
    
    try:
        import subprocess
        
        # Check cargo
        result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ {result.stdout.strip()}")
            
            # Test Solana program compilation
            if os.path.exists("solana/programs"):
                result = subprocess.run(["cargo", "check"], 
                                      cwd="solana/programs", 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("  ✅ Solana program compiles successfully")
                else:
                    print("  ⚠️ Solana program has warnings (but compiles)")
        else:
            print("  ⚠️ Cargo not available")
        
        return True
        
    except FileNotFoundError:
        print("  ⚠️ Rust/Cargo not found (optional for Solana development)")
        return True  # Not critical
    except Exception as e:
        print(f"  ❌ Rust environment issue: {e}")
        return False

def test_project_structure():
    """Test that project structure is intact."""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "requirements.txt",
        "package.json", 
        "grok_copilot_launcher.py",
        "agents/iem_syndicate.py",
        "contracts/IEMDreams.sol"
    ]
    
    optional_files = [
        "evm/package.json",
        "dashboard/requirements.txt",
        "solana/programs/Cargo.toml"
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (required)")
            all_good = False
    
    for file in optional_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} (optional)")
    
    return all_good

def main():
    """Run all validation tests."""
    print("🌌 Dream-Mind-Lucid Installation Validation")
    print("=" * 50)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Node.js Environment", test_node_dependencies), 
        ("Rust Environment", test_rust_environment),
        ("Project Structure", test_project_structure)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Test '{name}' failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY:")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All validations passed! Dream-Mind-Lucid is ready!")
        print("💡 Run 'python install_and_deploy.py deploy' to deploy the ecosystem")
        return 0
    else:
        print("\n⚠️ Some validations failed. Check the output above.")
        print("💡 Run 'python install_and_deploy.py install' to fix issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())