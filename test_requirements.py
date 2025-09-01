#!/usr/bin/env python3
"""
Test script to validate requirements.txt dependencies
"""

def test_web3():
    """Test Web3 functionality"""
    try:
        from web3 import Web3
        # Test basic Web3 functionality
        w3 = Web3()
        print("✅ web3: Basic import and instantiation works")
        return True
    except Exception as e:
        print(f"❌ web3: {e}")
        return False

def test_solcx():
    """Test py-solc-x functionality"""
    try:
        from solcx import compile_standard, install_solc
        print("✅ py-solc-x: Import works")
        return True
    except Exception as e:
        print(f"❌ py-solc-x: {e}")
        return False

def test_ipfs():
    """Test IPFS client (without requiring local IPFS daemon)"""
    try:
        import ipfshttpclient
        print("✅ ipfshttpclient: Import works")
        return True
    except Exception as e:
        print(f"❌ ipfshttpclient: {e}")
        return False

def test_mcp():
    """Test MCP server functionality"""
    try:
        import mcp.server
        print("✅ mcp: Server module import works")
        return True
    except Exception as e:
        print(f"❌ mcp: {e}")
        return False

def test_exiftool():
    """Test PyExifTool functionality"""
    try:
        import exiftool
        print("✅ PyExifTool: Import works")
        return True
    except Exception as e:
        print(f"❌ PyExifTool: {e}")
        return False

def test_optional_dependencies():
    """Test optional dependencies and provide guidance"""
    print("\n--- Optional Dependencies ---")
    
    # Test biconomy-sdk
    try:
        from biconomy.client import Biconomy
        print("✅ biconomy-sdk: Available")
    except ImportError:
        print("⚠️ biconomy-sdk: Not available (expected)")
        print("   → Using standard Web3 transactions (SKALE has zero gas)")

def main():
    """Run all tests"""
    print("Testing Dream-Mind-Lucid Dependencies")
    print("=" * 40)
    
    tests = [
        test_web3,
        test_solcx,
        test_ipfs,
        test_mcp,
        test_exiftool,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    test_optional_dependencies()
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} core dependencies working")
    
    if passed == total:
        print("🎉 All required dependencies are working!")
        print("✅ requirements.txt is properly configured")
        return True
    else:
        print("❌ Some dependencies failed")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)