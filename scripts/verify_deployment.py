#!/usr/bin/env python3
"""
Deployment Verification Script
=============================
Verifies that all deployments are working correctly across chains.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

def verify_deployment(chain: str) -> bool:
    """Verify deployment for a specific chain"""
    print(f"🔍 Verifying {chain} deployment...")
    
    # Check deployment file exists
    deployment_file = Path(f"deployments/{chain}_mainnet.json")
    if not deployment_file.exists():
        print(f"❌ Deployment file not found: {deployment_file}")
        return False
    
    # Load deployment info
    with open(deployment_file, 'r') as f:
        deployment_info = json.load(f)
    
    # Verify basic structure
    required_fields = ['chain', 'environment', 'deployed_at', 'contracts']
    for field in required_fields:
        if field not in deployment_info:
            print(f"❌ Missing field '{field}' in deployment info")
            return False
    
    # Verify contracts
    contracts = deployment_info.get('contracts', {})
    if not contracts:
        print(f"❌ No contracts found in deployment")
        return False
    
    for contract_name, contract_data in contracts.items():
        if isinstance(contract_data, dict):
            if 'address' not in contract_data:
                print(f"❌ Contract {contract_name} missing address")
                return False
            
            address = contract_data['address']
            if not address or address == '':
                print(f"❌ Contract {contract_name} has empty address")
                return False
                
            print(f"✅ {contract_name}: {address}")
    
    # Verify relayer configuration if applicable
    relayer_file = Path(f"deployments/relayers/{chain}_relayers.json")
    if relayer_file.exists():
        with open(relayer_file, 'r') as f:
            relayer_config = json.load(f)
        
        enabled_relayers = [name for name, config in relayer_config.get('relayers', {}).items() 
                          if config.get('enabled', False)]
        
        if enabled_relayers:
            print(f"✅ Gasless relayers enabled: {', '.join(enabled_relayers)}")
        else:
            print(f"⚠️  No gasless relayers enabled for {chain}")
    
    print(f"✅ {chain} deployment verified successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Verify deployment')
    parser.add_argument('--chain', 
                       choices=['solana', 'skale', 'polygon', 'base', 'arbitrum'],
                       help='Chain to verify (if not specified, verifies all)')
    
    args = parser.parse_args()
    
    if args.chain:
        chains = [args.chain]
    else:
        # Find all deployment files
        deployment_dir = Path("deployments")
        if not deployment_dir.exists():
            print("❌ No deployments directory found")
            sys.exit(1)
        
        chains = []
        for file in deployment_dir.glob("*_mainnet.json"):
            chain_name = file.stem.replace('_mainnet', '')
            chains.append(chain_name)
    
    if not chains:
        print("❌ No deployments found to verify")
        sys.exit(1)
    
    print(f"🔍 Verifying deployments for: {', '.join(chains)}")
    print("=" * 50)
    
    all_verified = True
    for chain in chains:
        try:
            if not verify_deployment(chain):
                all_verified = False
        except Exception as e:
            print(f"❌ Verification failed for {chain}: {e}")
            all_verified = False
        print()
    
    if all_verified:
        print("🎉 All deployments verified successfully!")
        sys.exit(0)
    else:
        print("❌ Some deployments failed verification")
        sys.exit(1)

if __name__ == "__main__":
    main()