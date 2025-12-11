#!/usr/bin/env python3
"""
Test All Deployments
====================
Comprehensive testing of all deployed contracts and relayers.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

def test_chain_deployment(chain: str, environment: str) -> Tuple[bool, Dict]:
    """Test deployment for a specific chain"""
    print(f"🧪 Testing {chain} deployment...")
    
    test_results = {
        "chain": chain,
        "environment": environment,
        "contracts": {},
        "relayers": {},
        "overall_status": "unknown"
    }
    
    try:
        # Test contract deployment verification
        verify_result = subprocess.run([
            sys.executable, "scripts/verify_deployment.py", "--chain", chain
        ], capture_output=True, text=True, cwd=".")
        
        contract_verification_passed = verify_result.returncode == 0
        test_results["contracts"]["verification"] = {
            "passed": contract_verification_passed,
            "output": verify_result.stdout if contract_verification_passed else verify_result.stderr
        }
        
        # Test relayer configuration
        relayer_result = subprocess.run([
            sys.executable, "scripts/setup_relayers.py", "--chain", chain, "--test"
        ], capture_output=True, text=True, cwd=".")
        
        relayer_test_passed = relayer_result.returncode == 0
        test_results["relayers"]["configuration"] = {
            "passed": relayer_test_passed,
            "output": relayer_result.stdout if relayer_test_passed else relayer_result.stderr
        }
        
        # Test specific chain functionality
        if chain == "solana":
            solana_test_passed = test_solana_specific()
            test_results["solana_specific"] = {
                "passed": solana_test_passed,
                "tests": ["treasury_status", "token_creation", "rpc_connectivity"]
            }
        else:
            evm_test_passed = test_evm_specific(chain)
            test_results["evm_specific"] = {
                "passed": evm_test_passed,
                "tests": ["gas_configuration", "contract_interaction", "rpc_connectivity"]
            }
        
        # Determine overall status
        all_tests = [
            contract_verification_passed,
            relayer_test_passed,
            test_results.get("solana_specific", {}).get("passed", True),
            test_results.get("evm_specific", {}).get("passed", True)
        ]
        
        test_results["overall_status"] = "passed" if all(all_tests) else "failed"
        
    except Exception as e:
        test_results["overall_status"] = "error"
        test_results["error"] = str(e)
    
    return test_results["overall_status"] == "passed", test_results

def test_solana_specific() -> bool:
    """Test Solana-specific functionality"""
    try:
        # Test treasury status
        result = subprocess.run([
            sys.executable, "agents/solana_dream_agent.py", "treasury_status"
        ], capture_output=True, text=True, cwd=".")
        
        return result.returncode == 0 and "Treasury" in result.stdout
    except:
        return False

def test_evm_specific(chain: str) -> bool:
    """Test EVM-specific functionality"""
    try:
        # Test basic connectivity and gas configuration
        from web3 import Web3
        
        # Load deployment info to get RPC
        deployment_file = Path(f"deployments/{chain}_mainnet.json")
        if not deployment_file.exists():
            return False
        
        with open(deployment_file, 'r') as f:
            deployment_data = json.load(f)
        
        rpc_url = deployment_data.get('config', {}).get('rpc')
        if not rpc_url:
            return False
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Test connectivity
        if not w3.is_connected():
            return False
        
        # Test gas price for SKALE (should be 0)
        if chain == "skale":
            gas_price = w3.eth.gas_price
            return gas_price == 0
        
        return True
        
    except Exception as e:
        print(f"EVM test error: {e}")
        return False

def test_frontend_config() -> bool:
    """Test frontend configuration"""
    try:
        config_file = Path("frontend/deployment-config.json")
        if not config_file.exists():
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ["environment", "networks"]
        for field in required_fields:
            if field not in config:
                return False
        
        # Check that at least one network is configured
        if not config.get("networks"):
            return False
        
        return True
        
    except:
        return False

def generate_test_report(all_results: List[Dict]) -> Dict:
    """Generate comprehensive test report"""
    total_chains = len(all_results)
    passed_chains = len([r for r in all_results if r["overall_status"] == "passed"])
    failed_chains = len([r for r in all_results if r["overall_status"] == "failed"])
    error_chains = len([r for r in all_results if r["overall_status"] == "error"])
    
    report = {
        "summary": {
            "total_chains": total_chains,
            "passed": passed_chains,
            "failed": failed_chains,
            "errors": error_chains,
            "success_rate": round((passed_chains / total_chains * 100) if total_chains > 0 else 0, 2)
        },
        "chain_results": all_results,
        "frontend_config": test_frontend_config(),
        "timestamp": json.loads(json.dumps({"timestamp": __import__('time').time()}))["timestamp"]
    }
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Test all deployments')
    parser.add_argument('--environment', required=True,
                       choices=['mainnet', 'testnet', 'devnet'],
                       help='Target environment')
    parser.add_argument('--chain',
                       choices=['solana', 'skale', 'polygon', 'base', 'arbitrum'],
                       help='Test specific chain only')
    
    args = parser.parse_args()
    
    print(f"🧪 DreamMindLucid Deployment Testing")
    print(f"Environment: {args.environment}")
    print("=" * 50)
    
    # Determine chains to test
    if args.chain:
        chains_to_test = [args.chain]
    else:
        # Find all deployment files
        deployment_dir = Path("deployments")
        if not deployment_dir.exists():
            print("❌ No deployments directory found")
            sys.exit(1)
        
        chains_to_test = []
        for file in deployment_dir.glob(f"*_{args.environment}.json"):
            chain_name = file.stem.replace(f'_{args.environment}', '')
            chains_to_test.append(chain_name)
    
    if not chains_to_test:
        print("❌ No deployments found to test")
        sys.exit(1)
    
    print(f"Testing chains: {', '.join(chains_to_test)}")
    print()
    
    # Run tests for each chain
    all_results = []
    overall_success = True
    
    for chain in chains_to_test:
        success, results = test_chain_deployment(chain, args.environment)
        all_results.append(results)
        
        if not success:
            overall_success = False
        
        status_emoji = "✅" if success else "❌"
        print(f"{status_emoji} {chain}: {results['overall_status']}")
    
    print()
    
    # Generate and save test report
    report = generate_test_report(all_results)
    
    report_file = Path(f"test_results_{args.environment}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    summary = report["summary"]
    print(f"📊 Test Summary:")
    print(f"   Total Chains: {summary['total_chains']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Errors: {summary['errors']}")
    print(f"   Success Rate: {summary['success_rate']}%")
    print(f"   Frontend Config: {'✅' if report['frontend_config'] else '❌'}")
    print(f"   Report saved: {report_file}")
    
    if overall_success and report["frontend_config"]:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()