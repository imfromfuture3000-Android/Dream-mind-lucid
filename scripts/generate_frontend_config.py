#!/usr/bin/env python3
"""
Frontend Configuration Generator
===============================
Generates deployment configuration for the frontend based on deployment artifacts.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

def generate_frontend_config(deployments_dir: str, environment: str) -> Dict[str, Any]:
    """Generate frontend configuration from deployment artifacts"""
    print(f"📝 Generating frontend config for {environment}")
    
    deployments_path = Path(deployments_dir)
    config = {
        "environment": environment,
        "networks": {},
        "relayers": {},
        "ipfs": {
            "gateway": "https://gateway.pinata.cloud/ipfs/",
            "api_url": "https://api.pinata.cloud"
        },
        "features": {
            "gasless_transactions": True,
            "multi_chain": True,
            "staking_rewards": True,
            "analytics": True
        }
    }
    
    # Process deployment files
    for deployment_file in deployments_path.glob(f"*_{environment}.json"):
        try:
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
            
            chain_name = deployment_file.stem.replace(f'_{environment}', '')
            
            # Extract contract addresses
            contracts = {}
            for contract_name, contract_data in deployment_data.get('contracts', {}).items():
                if isinstance(contract_data, dict) and 'address' in contract_data:
                    contracts[contract_name] = {
                        "address": contract_data['address'],
                        "deployed_at": contract_data.get('deployed_at'),
                        "gasless": contract_data.get('gasless', False)
                    }
            
            # Add network configuration
            config["networks"][chain_name] = {
                "name": deployment_data.get('config', {}).get('name', chain_name),
                "chain_id": deployment_data.get('config', {}).get('chain_id'),
                "rpc": deployment_data.get('config', {}).get('rpc'),
                "contracts": contracts,
                "gasless_enabled": deployment_data.get('gasless_enabled', False),
                "deployed_at": deployment_data.get('deployed_at')
            }
            
            print(f"✅ Added {chain_name} configuration")
            
        except Exception as e:
            print(f"⚠️  Failed to process {deployment_file}: {e}")
    
    # Process relayer configurations
    relayers_dir = deployments_path / "relayers"
    if relayers_dir.exists():
        for relayer_file in relayers_dir.glob("*_relayers.json"):
            try:
                with open(relayer_file, 'r') as f:
                    relayer_data = json.load(f)
                
                chain_name = relayer_file.stem.replace('_relayers', '')
                
                # Extract enabled relayers
                enabled_relayers = {}
                for relayer_name, relayer_config in relayer_data.get('relayers', {}).items():
                    if relayer_config.get('enabled', False):
                        enabled_relayers[relayer_name] = {
                            "type": relayer_config.get('type'),
                            "api_key": relayer_config.get('api_key', ''),
                            "chain_id": relayer_config.get('chain_id'),
                            "contracts": relayer_config.get('contracts', []),
                            "gasless_methods": relayer_config.get('gasless_methods', {})
                        }
                
                if enabled_relayers:
                    config["relayers"][chain_name] = enabled_relayers
                    print(f"✅ Added {chain_name} relayer configuration")
                
            except Exception as e:
                print(f"⚠️  Failed to process {relayer_file}: {e}")
    
    return config

def generate_env_file(config: Dict[str, Any], output_path: str):
    """Generate .env file for frontend"""
    env_lines = [
        "# Dream-Mind-Lucid Frontend Configuration",
        "# Generated automatically - do not edit manually",
        "",
        f"VITE_ENVIRONMENT={config['environment']}",
        "",
        "# Network Configuration"
    ]
    
    for chain_name, network_config in config.get("networks", {}).items():
        chain_upper = chain_name.upper()
        env_lines.extend([
            f"VITE_{chain_upper}_RPC={network_config.get('rpc', '')}",
            f"VITE_{chain_upper}_CHAIN_ID={network_config.get('chain_id', '')}",
        ])
        
        # Add contract addresses
        for contract_name, contract_data in network_config.get("contracts", {}).items():
            contract_upper = contract_name.upper()
            env_lines.append(f"VITE_{chain_upper}_{contract_upper}_ADDRESS={contract_data.get('address', '')}")
        
        env_lines.append("")
    
    # Add relayer configuration
    env_lines.extend([
        "# Relayer Configuration",
        "# Add your API keys here"
    ])
    
    for chain_name, relayers in config.get("relayers", {}).items():
        for relayer_name in relayers.keys():
            relayer_upper = relayer_name.upper()
            env_lines.append(f"VITE_{relayer_upper}_API_KEY=your_{relayer_name}_api_key_here")
    
    env_lines.extend([
        "",
        "# IPFS Configuration",
        f"VITE_IPFS_GATEWAY={config['ipfs']['gateway']}",
        f"VITE_IPFS_API_URL={config['ipfs']['api_url']}",
        "VITE_PINATA_API_KEY=your_pinata_api_key_here",
        "VITE_PINATA_SECRET_KEY=your_pinata_secret_key_here",
        "",
        "# Wallet Connect",
        "VITE_WALLET_CONNECT_PROJECT_ID=your_wallet_connect_project_id_here",
        "",
        "# App Configuration",
        "VITE_APP_URL=https://dream-mind-lucid.vercel.app"
    ])
    
    # Write .env file
    with open(output_path, 'w') as f:
        f.write('\n'.join(env_lines))
    
    print(f"📝 Generated .env file: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate frontend configuration')
    parser.add_argument('--deployments', required=True, help='Deployments directory')
    parser.add_argument('--environment', required=True, help='Target environment')
    parser.add_argument('--output', default='frontend/deployment-config.json', help='Output file')
    
    args = parser.parse_args()
    
    print(f"🔧 Generating frontend configuration")
    print(f"Deployments: {args.deployments}")
    print(f"Environment: {args.environment}")
    print("=" * 50)
    
    # Generate configuration
    config = generate_frontend_config(args.deployments, args.environment)
    
    # Save configuration file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Configuration saved to: {output_path}")
    
    # Generate .env file for frontend
    env_path = output_path.parent / '.env.production'
    generate_env_file(config, str(env_path))
    
    # Generate example .env file
    env_example_path = output_path.parent / '.env.example'
    generate_env_file(config, str(env_example_path))
    
    print("✅ Frontend configuration generated successfully!")

if __name__ == "__main__":
    main()