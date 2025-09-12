#!/usr/bin/env python3
"""
README Deployment Info Updater
==============================
Updates README.md with current deployment information.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def load_deployment_info(deployments_dir: str, environment: str) -> Dict:
    """Load all deployment information"""
    deployments_path = Path(deployments_dir)
    deployment_info = {
        "environment": environment,
        "chains": {},
        "total_contracts": 0,
        "gasless_chains": 0,
        "last_updated": datetime.now().isoformat()
    }
    
    for deployment_file in deployments_path.glob(f"*_{environment}.json"):
        try:
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
            
            chain_name = deployment_file.stem.replace(f'_{environment}', '')
            
            contracts = {}
            for contract_name, contract_data in deployment_data.get('contracts', {}).items():
                if isinstance(contract_data, dict) and 'address' in contract_data:
                    contracts[contract_name] = {
                        "address": contract_data['address'],
                        "deployed_at": deployment_data.get('deployed_at'),
                        "gasless": contract_data.get('gasless', False)
                    }
            
            deployment_info["chains"][chain_name] = {
                "name": deployment_data.get('config', {}).get('name', chain_name.title()),
                "chain_id": deployment_data.get('config', {}).get('chain_id'),
                "rpc": deployment_data.get('config', {}).get('rpc'),
                "contracts": contracts,
                "gasless_enabled": deployment_data.get('gasless_enabled', False),
                "contract_count": len(contracts)
            }
            
            deployment_info["total_contracts"] += len(contracts)
            if deployment_data.get('gasless_enabled', False):
                deployment_info["gasless_chains"] += 1
                
        except Exception as e:
            print(f"⚠️  Failed to load {deployment_file}: {e}")
    
    return deployment_info

def generate_deployment_section(deployment_info: Dict) -> str:
    """Generate the deployment section for README"""
    
    section = f"""
## 🚀 Live Deployments ({deployment_info['environment'].title()})

> **Zero-Cost Achievement Unlocked!** 🎉  
> All contracts deployed with gasless transactions across {len(deployment_info['chains'])} networks.

### 📊 Deployment Summary

| Metric | Value |
|--------|-------|
| **Networks** | {len(deployment_info['chains'])} |
| **Total Contracts** | {deployment_info['total_contracts']} |
| **Gasless Networks** | {deployment_info['gasless_chains']} |
| **Last Updated** | {deployment_info['last_updated'][:10]} |

### 🌐 Network Deployments

"""
    
    for chain_name, chain_info in deployment_info['chains'].items():
        gasless_badge = "🆓 **Gasless**" if chain_info['gasless_enabled'] else "⛽ Standard"
        
        section += f"""
#### {chain_info['name']} {gasless_badge}

**Network Details:**
- **Chain ID:** `{chain_info.get('chain_id', 'N/A')}`
- **RPC:** `{chain_info.get('rpc', 'N/A')}`
- **Contracts Deployed:** {chain_info['contract_count']}

**Contract Addresses:**
"""
        
        for contract_name, contract_data in chain_info['contracts'].items():
            section += f"- **{contract_name}:** [`{contract_data['address']}`]({chain_info.get('rpc', '#')}) "
            if contract_data.get('gasless'):
                section += "🆓"
            section += "\n"
        
        section += "\n"
    
    section += f"""
### ⚡ Gasless Transaction Features

Our zero-cost deployment system enables:

- **🆓 Zero Gas Fees** on SKALE Europa Hub
- **🤖 Meta-Transactions** via Biconomy on EVM chains  
- **🍦 Gelato Relayers** for automated execution
- **🟣 MEV Protection** on Solana with Helius RPC
- **💰 Fee Rebates** through optimized transaction routing

### 🔗 Quick Connect

Add networks to your wallet:

"""
    
    for chain_name, chain_info in deployment_info['chains'].items():
        if chain_info.get('chain_id') and chain_info.get('rpc'):
            section += f"""
<details>
<summary><strong>{chain_info['name']}</strong></summary>

```
Network Name: {chain_info['name']}
RPC URL: {chain_info['rpc']}
Chain ID: {chain_info['chain_id']}
Currency Symbol: {'SKL' if 'skale' in chain_name.lower() else 'ETH'}
```
</details>
"""
    
    section += f"""

### 🎯 Interact with Contracts

**Web Interface:** [Live DApp](https://dream-mind-lucid.vercel.app)  
**Documentation:** [API Docs](https://dream-mind-lucid.vercel.app/docs)  
**GitHub:** [Source Code](https://github.com/imfromfuture3000-Android/Dream-mind-lucid)

---

*Deployment info auto-updated by GitHub Actions on {deployment_info['last_updated'][:10]}*
"""
    
    return section

def update_readme(readme_path: str, deployment_section: str):
    """Update README.md with deployment information"""
    
    # Read current README
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Find deployment section markers
    start_marker = "## 🚀 Live Deployments"
    end_marker = "*Deployment info auto-updated by GitHub Actions"
    
    start_idx = readme_content.find(start_marker)
    if start_idx != -1:
        # Find the end of the deployment section
        end_idx = readme_content.find(end_marker)
        if end_idx != -1:
            # Find the end of the line
            end_idx = readme_content.find('\n', end_idx) + 1
            # Replace the section
            new_readme = readme_content[:start_idx] + deployment_section + readme_content[end_idx:]
        else:
            # No end marker found, append to the section
            next_section = readme_content.find('\n## ', start_idx + 1)
            if next_section != -1:
                new_readme = readme_content[:start_idx] + deployment_section + readme_content[next_section:]
            else:
                new_readme = readme_content[:start_idx] + deployment_section
    else:
        # No deployment section found, add it before the roadmap section
        roadmap_idx = readme_content.find("## 🔮 Roadmap")
        if roadmap_idx != -1:
            new_readme = readme_content[:roadmap_idx] + deployment_section + '\n' + readme_content[roadmap_idx:]
        else:
            # Add at the end
            new_readme = readme_content + '\n' + deployment_section
    
    # Write updated README
    with open(readme_path, 'w') as f:
        f.write(new_readme)
    
    print(f"✅ README updated with deployment information")

def main():
    parser = argparse.ArgumentParser(description='Update README with deployment info')
    parser.add_argument('--deployments', required=True, help='Deployments directory')
    parser.add_argument('--environment', required=True, help='Target environment')
    parser.add_argument('--readme', default='README.md', help='README file path')
    
    args = parser.parse_args()
    
    print(f"📝 Updating README with deployment information")
    print(f"Deployments: {args.deployments}")
    print(f"Environment: {args.environment}")
    print("=" * 50)
    
    # Load deployment information
    deployment_info = load_deployment_info(args.deployments, args.environment)
    
    if not deployment_info['chains']:
        print("❌ No deployment information found")
        return
    
    # Generate deployment section
    deployment_section = generate_deployment_section(deployment_info)
    
    # Update README
    update_readme(args.readme, deployment_section)
    
    print(f"📊 Updated README with:")
    print(f"   - {len(deployment_info['chains'])} networks")
    print(f"   - {deployment_info['total_contracts']} contracts")
    print(f"   - {deployment_info['gasless_chains']} gasless networks")

if __name__ == "__main__":
    main()