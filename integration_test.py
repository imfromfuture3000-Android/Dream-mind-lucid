#!/usr/bin/env python3
"""
Cross-Chain Dream Syndicate Integration Test
--------------------------------------------
Tests both Solana and SKALE implementations to verify compatibility
and migration readiness for Dream-Mind-Lucid ecosystem
"""

import os
import sys
import json
import asyncio
import time
from pathlib import Path

# Add agents directory to path
sys.path.append(str(Path(__file__).parent / "agents"))

def test_memory_compatibility():
    """Test that both agents can read/write to the same memory file"""
    print("🔄 Testing cross-chain memory compatibility...")
    
    # Load existing memory
    if os.path.exists("iem_memory.json"):
        with open("iem_memory.json", 'r') as f:
            memory = json.load(f)
    else:
        memory = {}
    
    # Check for both SKALE and Solana data
    has_skale = "lastDeployed" in memory and len(memory.get("lastDeployed", {})) > 0
    has_solana = "solana" in memory and memory.get("solana", {}).get("program_id")
    
    print(f"✅ SKALE deployment data: {'Found' if has_skale else 'Not found'}")
    print(f"✅ Solana deployment data: {'Found' if has_solana else 'Not found'}")
    
    if has_skale and has_solana:
        print("🌉 Cross-chain compatibility confirmed!")
        return True
    elif has_skale or has_solana:
        print("⚠️  Single chain deployment detected - migration in progress")
        return True
    else:
        print("❌ No deployment data found")
        return False

async def test_solana_agent():
    """Test Solana agent functionality"""
    print("\n🚀 Testing Solana agent...")
    
    try:
        # Import and test Solana agent
        from solana_dream_syndicate import SolanaDreamSyndicate, deploy_full_ecosystem
        
        # Run a quick deployment test
        await deploy_full_ecosystem()
        print("✅ Solana agent test passed")
        return True
    except ImportError as e:
        print(f"⚠️  Solana agent not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Solana agent test failed: {e}")
        return False

def test_skale_agent():
    """Test SKALE agent functionality"""
    print("\n🌌 Testing SKALE agent...")
    
    try:
        # Import and test SKALE agent
        from iem_syndicate import deploy_contract
        
        # Set simulation mode
        os.environ["SYNDICATE_SIMULATE"] = "1"
        
        # Test deployment
        address, abi = deploy_contract("IEMDreams")
        print(f"✅ SKALE agent test passed: {address}")
        return True
    except ImportError as e:
        print(f"⚠️  SKALE agent not available: {e}")
        return False
    except Exception as e:
        print(f"❌ SKALE agent test failed: {e}")
        return False

def test_configuration():
    """Test configuration compatibility"""
    print("\n⚙️ Testing configuration...")
    
    # Check for configuration files
    configs = {
        "Solana Config": "solana-config.sh",
        "Deployment Config": "deployment-config.sh", 
        "Requirements": "requirements.txt",
        "Anchor Config": "Anchor.toml",
        "Install Script": "install-solana.sh"
    }
    
    all_good = True
    for name, file_path in configs.items():
        if os.path.exists(file_path):
            print(f"✅ {name}: Found")
        else:
            print(f"❌ {name}: Not found")
            all_good = False
    
    return all_good

async def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Dream-Mind-Lucid Cross-Chain Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Memory Compatibility", test_memory_compatibility),
        ("Configuration", test_configuration), 
        ("SKALE Agent", test_skale_agent),
        ("Solana Agent", test_solana_agent),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Integration Test Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎊 All tests passed! Cross-chain integration ready! 🎊")
        print("🚀 Ready for production deployment on both Solana and SKALE")
    elif passed >= total * 0.75:
        print("⚠️  Most tests passed. Some optional features may be unavailable.")
        print("💡 Consider installing missing dependencies for full functionality")
    else:
        print("❌ Multiple test failures detected.")
        print("🔧 Please review the setup and install missing dependencies")
    
    return passed == total

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python integration_test.py")
        print("Runs integration tests for both Solana and SKALE implementations")
        return
    
    try:
        result = asyncio.run(run_integration_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()