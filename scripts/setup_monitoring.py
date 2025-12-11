#!/usr/bin/env python3
"""
Deployment Monitoring Setup
===========================
Sets up monitoring and health checks for deployed contracts.

Author: DreamMindLucid
Version: 1.0.0
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

def setup_monitoring(environment: str):
    """Setup monitoring for deployed contracts"""
    print(f"📊 Setting up monitoring for {environment}")
    
    deployments_dir = Path("deployments")
    monitoring_config = {
        "environment": environment,
        "health_checks": [],
        "alerts": {
            "enabled": True,
            "webhook_url": os.getenv("MONITORING_WEBHOOK_URL", ""),
            "check_interval": 300  # 5 minutes
        },
        "metrics": {
            "contract_calls": True,
            "gas_usage": True,
            "transaction_success_rate": True,
            "user_activity": True
        }
    }
    
    # Process each deployment
    for deployment_file in deployments_dir.glob(f"*_{environment}.json"):
        try:
            with open(deployment_file, 'r') as f:
                deployment_data = json.load(f)
            
            chain_name = deployment_file.stem.replace(f'_{environment}', '')
            chain_config = deployment_data.get('config', {})
            
            # Add health checks for each contract
            for contract_name, contract_data in deployment_data.get('contracts', {}).items():
                if isinstance(contract_data, dict) and 'address' in contract_data:
                    health_check = {
                        "name": f"{chain_name}_{contract_name}",
                        "chain": chain_name,
                        "contract": contract_name,
                        "address": contract_data['address'],
                        "rpc_url": chain_config.get('rpc', ''),
                        "chain_id": chain_config.get('chain_id'),
                        "checks": [
                            "contract_code_exists",
                            "contract_responsive",
                            "recent_activity"
                        ]
                    }
                    monitoring_config["health_checks"].append(health_check)
                    
            print(f"✅ Added monitoring for {chain_name}")
            
        except Exception as e:
            print(f"⚠️  Failed to setup monitoring for {deployment_file}: {e}")
    
    # Save monitoring configuration
    monitoring_file = deployments_dir / f"monitoring_{environment}.json"
    with open(monitoring_file, 'w') as f:
        json.dump(monitoring_config, f, indent=2)
    
    print(f"💾 Monitoring config saved to: {monitoring_file}")
    
    # Generate monitoring script
    generate_monitoring_script(monitoring_config, environment)
    
    return monitoring_config

def generate_monitoring_script(config: Dict, environment: str):
    """Generate monitoring script"""
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated monitoring script for {environment}
Run this script periodically to check contract health
"""

import requests
import json
from web3 import Web3
from datetime import datetime

def check_contract_health(check_config):
    """Check health of a single contract"""
    try:
        # Connect to RPC
        w3 = Web3(Web3.HTTPProvider(check_config["rpc_url"]))
        
        if not w3.is_connected():
            return {{"status": "error", "message": "RPC not connected"}}
        
        address = check_config["address"]
        
        # Check if contract code exists
        code = w3.eth.get_code(address)
        if len(code) == 0:
            return {{"status": "error", "message": "Contract code not found"}}
        
        # Check recent activity (simplified)
        try:
            latest_block = w3.eth.get_block("latest")
            return {{
                "status": "healthy",
                "latest_block": latest_block.number,
                "timestamp": datetime.now().isoformat()
            }}
        except Exception as e:
            return {{"status": "warning", "message": f"Activity check failed: {{e}}"}}
            
    except Exception as e:
        return {{"status": "error", "message": str(e)}}

def main():
    """Run all health checks"""
    config = {json.dumps(config, indent=4)}
    
    results = []
    
    for check in config["health_checks"]:
        print(f"Checking {{check['name']}}...")
        result = check_contract_health(check)
        result["check_name"] = check["name"]
        result["chain"] = check["chain"]
        result["contract"] = check["contract"]
        results.append(result)
        
        status_emoji = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "warning" else "❌"
        print(f"  {{status_emoji}} {{result['status'].title()}}: {{result.get('message', 'OK')}}")
    
    # Save results
    with open("monitoring_results_{environment}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Send alerts if needed
    failed_checks = [r for r in results if r["status"] == "error"]
    if failed_checks and config["alerts"]["enabled"]:
        webhook_url = config["alerts"]["webhook_url"]
        if webhook_url:
            alert_data = {{
                "text": f"🚨 {{len(failed_checks)}} contract health checks failed!",
                "failures": failed_checks
            }}
            try:
                requests.post(webhook_url, json=alert_data)
            except:
                pass
    
    print(f"\\n📊 Health check complete: {{len([r for r in results if r['status'] == 'healthy'])}} healthy, {{len(failed_checks)}} failed")

if __name__ == "__main__":
    main()
'''
    
    script_path = Path(f"scripts/monitor_{environment}.py")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    print(f"📝 Generated monitoring script: {script_path}")

def main():
    parser = argparse.ArgumentParser(description='Setup deployment monitoring')
    parser.add_argument('--environment', required=True, 
                       choices=['mainnet', 'testnet', 'devnet'],
                       help='Target environment')
    
    args = parser.parse_args()
    
    print(f"📊 DreamMindLucid Monitoring Setup")
    print(f"Environment: {args.environment}")
    print("=" * 40)
    
    config = setup_monitoring(args.environment)
    
    health_checks_count = len(config.get("health_checks", []))
    if health_checks_count > 0:
        print(f"✅ Monitoring setup complete!")
        print(f"   Health checks: {health_checks_count}")
        print(f"   Run: python scripts/monitor_{args.environment}.py")
    else:
        print("❌ No contracts found to monitor")
        sys.exit(1)

if __name__ == "__main__":
    main()