#!/usr/bin/env python3
"""
Deployment Summary Generator
===========================
Generates a summary of all deployments for GitHub Actions output.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import json
from pathlib import Path
from datetime import datetime

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return "Unknown"

def main():
    """Generate deployment summary"""
    deployments_dir = Path("deployments")
    
    if not deployments_dir.exists():
        print("❌ No deployments found")
        return
    
    print("| Chain | Status | Contracts | Gasless | Deployed |")
    print("|-------|--------|-----------|---------|----------|")
    
    total_contracts = 0
    successful_chains = 0
    
    # Process each deployment file
    for deployment_file in sorted(deployments_dir.glob("*_mainnet.json")):
        try:
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
            
            chain_name = deployment_file.stem.replace('_mainnet', '')
            chain_display = chain_name.title()
            
            # Count contracts
            contracts = deployment_data.get('contracts', {})
            contract_count = len([c for c in contracts.values() 
                                if isinstance(c, dict) and c.get('address')])
            total_contracts += contract_count
            
            # Check if gasless is enabled
            gasless = "✅" if deployment_data.get('gasless_enabled', False) else "❌"
            
            # Format deployment time
            deployed_at = format_timestamp(deployment_data.get('deployed_at', 0))
            
            # Status
            status = "✅ Success" if contract_count > 0 else "❌ Failed"
            if contract_count > 0:
                successful_chains += 1
            
            print(f"| {chain_display} | {status} | {contract_count} | {gasless} | {deployed_at} |")
            
        except Exception as e:
            chain_name = deployment_file.stem.replace('_mainnet', '')
            print(f"| {chain_name.title()} | ❌ Error | 0 | ❌ | Error |")
    
    print("")
    print(f"**📊 Summary:**")
    print(f"- **Chains Deployed:** {successful_chains}")
    print(f"- **Total Contracts:** {total_contracts}")
    
    # Check relayer status
    relayers_dir = deployments_dir / "relayers"
    if relayers_dir.exists():
        total_relayers = 0
        for relayer_file in relayers_dir.glob("*_relayers.json"):
            try:
                with open(relayer_file, 'r') as f:
                    relayer_data = json.load(f)
                
                enabled_relayers = [name for name, config in relayer_data.get('relayers', {}).items() 
                                  if config.get('enabled', False)]
                total_relayers += len(enabled_relayers)
            except:
                continue
        
        print(f"- **Gasless Relayers:** {total_relayers}")
    
    # Check frontend deployment
    frontend_config = Path("frontend/deployment-config.json")
    if frontend_config.exists():
        print(f"- **Frontend Config:** ✅ Generated")
    else:
        print(f"- **Frontend Config:** ❌ Missing")
    
    print("")
    print("🔗 **Quick Links:**")
    print("- [GitHub Repository](https://github.com/imfromfuture3000-Android/Dream-mind-lucid)")
    print("- [Live Demo](https://dream-mind-lucid.vercel.app)")
    print("- [Documentation](https://dream-mind-lucid.vercel.app/docs)")

if __name__ == "__main__":
    main()