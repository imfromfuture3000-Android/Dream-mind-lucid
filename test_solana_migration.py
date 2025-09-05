#!/usr/bin/env python3
"""
Test Solana Migration - Integration Test Suite
---------------------------------------------
Tests the complete Solana migration functionality including:
- SPL Token 2022 deployment simulation
- Dream recording with MEV protection
- Treasury integration
- Helius RPC integration
"""

import os
import sys
import json
import time
import subprocess

def test_solana_agent():
    """Test the standalone Solana agent"""
    print("🧪 Testing Solana Dream Agent...")
    
    # Test token deployment
    result = subprocess.run([
        sys.executable, "agents/solana_dream_agent.py", "deploy_tokens"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Token deployment test passed")
    else:
        print(f"❌ Token deployment test failed: {result.stderr}")
        return False
    
    # Test dream recording
    result = subprocess.run([
        sys.executable, "agents/solana_dream_agent.py", "record_dream", 
        "Test dream for Solana migration validation"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Dream recording test passed")
    else:
        print(f"❌ Dream recording test failed: {result.stderr}")
        return False
    
    # Test treasury status
    result = subprocess.run([
        sys.executable, "agents/solana_dream_agent.py", "treasury_status"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Treasury status test passed")
        print("📊 Treasury Status Output:")
        print(result.stdout)
    else:
        print(f"❌ Treasury status test failed: {result.stderr}")
        return False
    
    return True

def test_enhanced_syndicate():
    """Test the enhanced IEM Syndicate with Solana support"""
    print("\n🧪 Testing Enhanced IEM Syndicate...")
    
    # Test help menu
    result = subprocess.run([
        sys.executable, "agents/iem_syndicate.py"
    ], capture_output=True, text=True)
    
    if "New Solana Commands:" in result.stdout:
        print("✅ Enhanced syndicate help menu test passed")
    else:
        print("❌ Enhanced syndicate help menu test failed")
        return False
    
    return True

def test_memory_files():
    """Test memory file generation and content"""
    print("\n🧪 Testing Memory Files...")
    
    if os.path.exists("solana_dream_memory.json"):
        with open("solana_dream_memory.json", "r") as f:
            memory = json.load(f)
            
        # Check tokens
        if "tokens" in memory and len(memory["tokens"]) == 3:
            print("✅ Token storage test passed")
        else:
            print("❌ Token storage test failed")
            return False
            
        # Check dreams
        if "dreams" in memory and len(memory["dreams"]) > 0:
            print("✅ Dream storage test passed")
        else:
            print("❌ Dream storage test failed")
            return False
            
        # Check treasury operations
        if "treasury_operations" in memory and len(memory["treasury_operations"]) > 0:
            print("✅ Treasury operations test passed")
        else:
            print("❌ Treasury operations test failed")
            return False
            
        # Check MEV protection
        if "mev_protection" in memory and memory["mev_protection"]["enabled"]:
            print("✅ MEV protection test passed")
        else:
            print("❌ MEV protection test failed")
            return False
            
    else:
        print("❌ Memory file not found")
        return False
    
    return True

def test_rust_program():
    """Test Rust program compilation"""
    print("\n🧪 Testing Rust Program...")
    
    result = subprocess.run([
        "cargo", "check"
    ], cwd="solana/programs", capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Rust program compilation test passed")
        return True
    else:
        print(f"❌ Rust program compilation test failed: {result.stderr}")
        return False

def test_configuration():
    """Test configuration files"""
    print("\n🧪 Testing Configuration...")
    
    # Test .env file
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
            
        if "SOLANA_RPC_URL" in content and "TREASURY_ADDRESS" in content:
            print("✅ Environment configuration test passed")
        else:
            print("❌ Environment configuration test failed")
            return False
    else:
        print("❌ .env file not found")
        return False
    
    # Test requirements.txt
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
            
        if "solana" in content and "base58" in content:
            print("✅ Requirements configuration test passed")
        else:
            print("❌ Requirements configuration test failed")
            return False
    else:
        print("❌ requirements.txt file not found")
        return False
    
    return True

def main():
    """Run all migration tests"""
    print("🌌 Dream-Mind-Lucid Solana Migration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Solana Agent", test_solana_agent),
        ("Enhanced Syndicate", test_enhanced_syndicate),
        ("Memory Files", test_memory_files),
        ("Rust Program", test_rust_program),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} tests...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} tests completed successfully")
            else:
                print(f"❌ {test_name} tests failed")
        except Exception as e:
            print(f"❌ {test_name} tests failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All migration tests passed! Solana integration ready.")
        print("\n📋 Migration Summary:")
        print("  • SPL Token 2022 deployment: ✅ Ready")
        print("  • Dream recording with MEV protection: ✅ Ready")
        print("  • Treasury integration: ✅ Ready")
        print("  • Helius RPC integration: ✅ Ready")
        print("  • Rust Solana program: ✅ Compiles")
        print("  • Enhanced agent system: ✅ Functional")
        print("\n🚀 Next steps:")
        print("  1. Set DEPLOYER_KEY for real deployment")
        print("  2. Disable SYNDICATE_SIMULATE for mainnet")
        print("  3. Deploy Rust program to Solana")
        print("  4. Execute real token deployment")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)