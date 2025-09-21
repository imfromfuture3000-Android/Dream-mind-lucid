#!/usr/bin/env python3
"""
Dream-Mind-Lucid Deployment Data Scanner
Scans all data in Dream-mind-lucid repository and collects real contract addresses 
with transaction hashes for mainnet deployments only.
"""
import json
import os
import re
import glob
from typing import Dict, List, Any
from datetime import datetime

class DeploymentDataScanner:
    def __init__(self, repo_path: str = "/home/runner/work/Dream-mind-lucid/Dream-mind-lucid"):
        self.repo_path = repo_path
        self.real_deployments = {
            "solana_mainnet": {},
            "skale_mainnet": {},
            "ethereum_mainnet": {},
            "other_mainnets": {}
        }
        self.simulation_data = []
        self.testnet_data = []
        
    def is_real_address(self, address: str) -> bool:
        """Check if an address appears to be real (not simulation)"""
        if not address:
            return False
        
        # Simulation indicators
        simulation_patterns = [
            r'^SIM_',
            r'^0xSIM',
            r'simulation',
            r'test.*addr',
            r'^0x[0-9a-f]*777777777',  # Test pattern
            r'^0x[0-9a-f]*[a-f]{20,}$',  # All letters pattern (likely test)
        ]
        
        address_lower = address.lower()
        for pattern in simulation_patterns:
            if re.search(pattern, address_lower):
                return False
                
        # Real address patterns
        real_patterns = [
            r'^[1-9A-HJ-NP-Za-km-z]{32,44}$',  # Solana address
            r'^0x[a-fA-F0-9]{40}$',  # Ethereum address
        ]
        
        for pattern in real_patterns:
            if re.match(pattern, address):
                return True
                
        return False
    
    def is_real_tx_hash(self, tx_hash: str) -> bool:
        """Check if a transaction hash appears to be real"""
        if not tx_hash:
            return False
            
        if tx_hash.startswith('sim_') or tx_hash.startswith('0xSIM'):
            return False
            
        # Real transaction hash patterns
        if re.match(r'^0x[a-fA-F0-9]{64}$', tx_hash):  # Ethereum tx
            return True
        if re.match(r'^[1-9A-HJ-NP-Za-km-z]{87,88}$', tx_hash):  # Solana tx
            return True
            
        return False
    
    def is_mainnet_network(self, network_info: Dict) -> bool:
        """Determine if network configuration is mainnet"""
        if isinstance(network_info, str):
            network_str = network_info.lower()
        else:
            network_str = str(network_info).lower()
            
        mainnet_indicators = [
            'mainnet',
            'europa-mainnet',
            'elated-tan-skat',  # SKALE Europa Hub
            'helius-rpc.com',
            'chain_id.*2046399126',  # SKALE Europa
        ]
        
        testnet_indicators = [
            'testnet',
            'test',
            'simulation',
            'devnet',
            'localhost',
            'juicy-low-small-testnet'
        ]
        
        # Check for testnet first (more specific)
        for indicator in testnet_indicators:
            if indicator in network_str:
                return False
                
        # Then check for mainnet
        for indicator in mainnet_indicators:
            if indicator in network_str:
                return True
                
        return False
    
    def scan_json_files(self) -> None:
        """Scan all JSON files for deployment data"""
        json_files = glob.glob(f"{self.repo_path}/**/*.json", recursive=True)
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.extract_deployment_data(data, file_path)
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  Error reading {file_path}: {e}")
    
    def extract_deployment_data(self, data: Any, source_file: str) -> None:
        """Extract deployment data from JSON structure"""
        if isinstance(data, dict):
            # Check for contract addresses
            for key, value in data.items():
                if 'address' in key.lower() and isinstance(value, str):
                    if self.is_real_address(value):
                        # Determine network
                        network = self.determine_network(data, source_file)
                        if network and self.is_mainnet_network(data):
                            self.add_real_deployment(network, key, value, data, source_file)
                
                # Check for transaction hashes
                if 'tx' in key.lower() or 'hash' in key.lower():
                    if isinstance(value, str) and self.is_real_tx_hash(value):
                        network = self.determine_network(data, source_file)
                        if network and self.is_mainnet_network(data):
                            self.add_tx_hash(network, key, value, data, source_file)
                
                # Check for nested deployment data
                if isinstance(value, dict):
                    if 'contracts' in key.lower() or 'tokens' in key.lower():
                        self.extract_nested_contracts(value, source_file, data)
                
                # Recursively check nested dictionaries
                if isinstance(value, dict):
                    self.extract_deployment_data(value, source_file)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self.extract_deployment_data(item, source_file)
    
    def extract_nested_contracts(self, contracts_data: Dict, source_file: str, parent_data: Dict) -> None:
        """Extract contract data from nested structures"""
        for contract_name, contract_info in contracts_data.items():
            if isinstance(contract_info, dict):
                address = contract_info.get('address') or contract_info.get('mint_address')
                tx_hash = contract_info.get('txHash') or contract_info.get('tx_signature') or contract_info.get('transactionHash')
                
                if address and self.is_real_address(address):
                    network = self.determine_network(parent_data, source_file)
                    if network and self.is_mainnet_network(parent_data):
                        deployment_info = {
                            'name': contract_name,
                            'address': address,
                            'tx_hash': tx_hash if self.is_real_tx_hash(tx_hash) else None,
                            'source_file': source_file,
                            'additional_info': contract_info
                        }
                        
                        if network not in self.real_deployments:
                            self.real_deployments[network] = {}
                        self.real_deployments[network][contract_name] = deployment_info
    
    def determine_network(self, data: Dict, source_file: str) -> str:
        """Determine which network based on context"""
        data_str = str(data).lower()
        file_str = source_file.lower()
        
        if 'solana' in data_str or 'solana' in file_str:
            return 'solana_mainnet'
        elif 'skale' in data_str or 'skale' in file_str or 'elated-tan-skat' in data_str:
            return 'skale_mainnet'
        elif 'ethereum' in data_str or 'ethereum' in file_str:
            return 'ethereum_mainnet'
        else:
            return 'other_mainnets'
    
    def add_real_deployment(self, network: str, name: str, address: str, data: Dict, source_file: str) -> None:
        """Add a real deployment to our collection"""
        if network not in self.real_deployments:
            self.real_deployments[network] = {}
        
        self.real_deployments[network][name] = {
            'address': address,
            'source_file': source_file,
            'full_data': data
        }
    
    def add_tx_hash(self, network: str, name: str, tx_hash: str, data: Dict, source_file: str) -> None:
        """Add transaction hash to existing deployment or create new entry"""
        if network not in self.real_deployments:
            self.real_deployments[network] = {}
        
        # Try to find existing deployment to add tx_hash to
        for contract_name, contract_info in self.real_deployments[network].items():
            if 'tx_hash' not in contract_info or not contract_info['tx_hash']:
                contract_info['tx_hash'] = tx_hash
                return
        
        # Create new entry if no existing deployment found
        self.real_deployments[network][f"tx_{name}"] = {
            'tx_hash': tx_hash,
            'source_file': source_file,
            'full_data': data
        }
    
    def scan_python_files(self) -> None:
        """Scan Python files for deployment configurations"""
        python_files = glob.glob(f"{self.repo_path}/**/*.py", recursive=True)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.extract_from_python_code(content, file_path)
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")
    
    def extract_from_python_code(self, content: str, file_path: str) -> None:
        """Extract deployment data from Python code"""
        # Look for RPC URLs that indicate mainnet
        mainnet_rpcs = [
            r'https://mainnet\.skalenodes\.com/v1/elated-tan-skat',
            r'https://mainnet\.helius-rpc\.com',
        ]
        
        for rpc_pattern in mainnet_rpcs:
            if re.search(rpc_pattern, content):
                # This file appears to have mainnet configuration
                # Look for contract addresses and tx hashes
                address_matches = re.findall(r'(?:address|contract)["\s]*=?["\s]*([0x][a-fA-F0-9]{40})', content)
                tx_matches = re.findall(r'(?:tx_?hash|transaction)["\s]*=?["\s]*([0x][a-fA-F0-9]{64})', content)
                
                for addr in address_matches:
                    if self.is_real_address(addr):
                        network = 'skale_mainnet' if 'skalenodes' in content else 'ethereum_mainnet'
                        self.add_real_deployment(network, f"from_{os.path.basename(file_path)}", addr, {}, file_path)
                
                for tx in tx_matches:
                    if self.is_real_tx_hash(tx):
                        network = 'skale_mainnet' if 'skalenodes' in content else 'ethereum_mainnet'
                        self.add_tx_hash(network, f"from_{os.path.basename(file_path)}", tx, {}, file_path)
    
    def scan_readme_files(self) -> None:
        """Scan README and documentation files for deployment addresses"""
        doc_files = glob.glob(f"{self.repo_path}/**/*.md", recursive=True)
        
        for file_path in doc_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.extract_from_documentation(content, file_path)
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")
    
    def extract_from_documentation(self, content: str, file_path: str) -> None:
        """Extract deployment addresses from documentation"""
        # Look for deployment sections with real addresses
        if 'mainnet' in content.lower():
            # Extract Solana addresses
            solana_addresses = re.findall(r'[1-9A-HJ-NP-Za-km-z]{32,44}', content)
            for addr in solana_addresses:
                if self.is_real_address(addr) and len(addr) >= 32:
                    # Check if it's in a mainnet context
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if addr in line:
                            context = ' '.join(lines[max(0, i-2):i+3]).lower()
                            if 'mainnet' in context and 'solana' in context:
                                self.add_real_deployment('solana_mainnet', 
                                                       f"from_{os.path.basename(file_path)}", 
                                                       addr, {'context': context}, file_path)
            
            # Extract Ethereum/SKALE addresses
            eth_addresses = re.findall(r'0x[a-fA-F0-9]{40}', content)
            for addr in eth_addresses:
                if self.is_real_address(addr):
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if addr in line:
                            context = ' '.join(lines[max(0, i-2):i+3]).lower()
                            if 'mainnet' in context:
                                if 'skale' in context:
                                    self.add_real_deployment('skale_mainnet', 
                                                           f"from_{os.path.basename(file_path)}", 
                                                           addr, {'context': context}, file_path)
                                else:
                                    self.add_real_deployment('ethereum_mainnet', 
                                                           f"from_{os.path.basename(file_path)}", 
                                                           addr, {'context': context}, file_path)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive deployment report"""
        report = {
            "scan_metadata": {
                "timestamp": datetime.now().isoformat(),
                "repository": "imfromfuture3000-Android/Dream-mind-lucid",
                "scan_type": "mainnet_deployments_only",
                "total_files_scanned": self.count_scanned_files()
            },
            "summary": {
                "total_mainnet_networks": len([k for k, v in self.real_deployments.items() if v]),
                "total_real_contracts": sum(len(contracts) for contracts in self.real_deployments.values()),
                "networks_with_deployments": [k for k, v in self.real_deployments.items() if v]
            },
            "mainnet_deployments": self.real_deployments,
            "verification_status": {},
            "recommendations": []
        }
        
        # Add verification recommendations
        for network, contracts in self.real_deployments.items():
            if contracts:
                report["verification_status"][network] = {
                    "contracts_found": len(contracts),
                    "needs_verification": True,
                    "explorer_urls": self.get_explorer_urls(network)
                }
        
        # Add recommendations
        if not any(self.real_deployments.values()):
            report["recommendations"].append("⚠️  No real mainnet deployments found. All detected data appears to be simulation/testnet.")
            report["recommendations"].append("📝 Consider running actual mainnet deployments and updating documentation with real addresses.")
        else:
            report["recommendations"].append("✅ Real mainnet deployments detected.")
            report["recommendations"].append("🔍 Verify all addresses against blockchain explorers.")
            report["recommendations"].append("📋 Update central documentation with verified deployment information.")
        
        return report
    
    def count_scanned_files(self) -> int:
        """Count total files scanned"""
        json_count = len(glob.glob(f"{self.repo_path}/**/*.json", recursive=True))
        py_count = len(glob.glob(f"{self.repo_path}/**/*.py", recursive=True))
        md_count = len(glob.glob(f"{self.repo_path}/**/*.md", recursive=True))
        return json_count + py_count + md_count
    
    def get_explorer_urls(self, network: str) -> List[str]:
        """Get blockchain explorer URLs for verification"""
        explorers = {
            "solana_mainnet": [
                "https://explorer.solana.com/",
                "https://solscan.io/"
            ],
            "skale_mainnet": [
                "https://elated-tan-skat.explorer.mainnet.skalenodes.com/"
            ],
            "ethereum_mainnet": [
                "https://etherscan.io/"
            ]
        }
        return explorers.get(network, [])
    
    def run_comprehensive_scan(self) -> Dict:
        """Run comprehensive scan of all deployment data"""
        print("🔍 Starting comprehensive Dream-Mind-Lucid deployment scan...")
        print(f"📁 Scanning repository: {self.repo_path}")
        
        print("📄 Scanning JSON files...")
        self.scan_json_files()
        
        print("🐍 Scanning Python files...")
        self.scan_python_files()
        
        print("📖 Scanning documentation files...")
        self.scan_readme_files()
        
        print("📊 Generating comprehensive report...")
        report = self.generate_report()
        
        print("✅ Scan complete!")
        return report

def main():
    scanner = DeploymentDataScanner()
    report = scanner.run_comprehensive_scan()
    
    # Save report
    with open("/home/runner/work/Dream-mind-lucid/Dream-mind-lucid/DEPLOYMENT_SCAN_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Create formatted markdown report
    create_formatted_report(report)
    
    # Print summary
    print("\n" + "="*60)
    print("🌌 DREAM-MIND-LUCID DEPLOYMENT SCAN SUMMARY")
    print("="*60)
    print(f"📊 Total Files Scanned: {report['scan_metadata']['total_files_scanned']}")
    print(f"🌐 Mainnet Networks Found: {report['summary']['total_mainnet_networks']}")
    print(f"📝 Real Contracts Found: {report['summary']['total_real_contracts']}")
    
    if report['summary']['total_real_contracts'] > 0:
        print("\n✅ REAL MAINNET DEPLOYMENTS FOUND:")
        for network in report['summary']['networks_with_deployments']:
            contracts = report['mainnet_deployments'][network]
            print(f"\n🔹 {network.upper()}:")
            for name, info in contracts.items():
                print(f"   📍 {name}: {info.get('address', 'N/A')}")
                if info.get('tx_hash'):
                    print(f"      🔗 TX: {info['tx_hash']}")
    else:
        print("\n⚠️  NO REAL MAINNET DEPLOYMENTS FOUND")
        print("   All detected data appears to be simulation/testnet")
    
    print(f"\n📋 Full report saved to: DEPLOYMENT_SCAN_REPORT.json")
    print(f"📄 Formatted report saved to: DEPLOYMENT_SCAN_REPORT.md")

def create_formatted_report(report: Dict):
    """Create formatted markdown report"""
    md_content = f"""# 🌌 Dream-Mind-Lucid Deployment Scan Report

**Generated:** {report['scan_metadata']['timestamp']}  
**Repository:** {report['scan_metadata']['repository']}  
**Scan Type:** {report['scan_metadata']['scan_type']}  

## 📊 Summary

- **Total Files Scanned:** {report['scan_metadata']['total_files_scanned']}
- **Mainnet Networks:** {report['summary']['total_mainnet_networks']}
- **Real Contracts Found:** {report['summary']['total_real_contracts']}
- **Networks with Deployments:** {', '.join(report['summary']['networks_with_deployments']) if report['summary']['networks_with_deployments'] else 'None'}

## 🚀 Mainnet Deployments

"""
    
    if report['summary']['total_real_contracts'] > 0:
        for network, contracts in report['mainnet_deployments'].items():
            if contracts:
                md_content += f"\n### {network.replace('_', ' ').title()}\n\n"
                md_content += "| Contract | Address | Transaction Hash | Source |\n"
                md_content += "|----------|---------|------------------|--------|\n"
                
                for name, info in contracts.items():
                    address = info.get('address', 'N/A')
                    tx_hash = info.get('tx_hash', 'N/A')
                    source = os.path.basename(info.get('source_file', 'Unknown'))
                    md_content += f"| {name} | `{address}` | `{tx_hash}` | {source} |\n"
    else:
        md_content += "⚠️ **No real mainnet deployments found.**\n\n"
        md_content += "All detected data appears to be simulation or testnet deployments.\n\n"
    
    md_content += "\n## 🔍 Verification Status\n\n"
    
    for network, status in report['verification_status'].items():
        md_content += f"### {network.replace('_', ' ').title()}\n\n"
        md_content += f"- **Contracts Found:** {status['contracts_found']}\n"
        md_content += f"- **Needs Verification:** {'Yes' if status['needs_verification'] else 'No'}\n"
        md_content += "- **Blockchain Explorers:**\n"
        for explorer in status['explorer_urls']:
            md_content += f"  - [{explorer}]({explorer})\n"
        md_content += "\n"
    
    md_content += "\n## 📋 Recommendations\n\n"
    for rec in report['recommendations']:
        md_content += f"- {rec}\n"
    
    md_content += f"\n---\n*Report generated by Dream-Mind-Lucid Deployment Scanner*"
    
    with open("/home/runner/work/Dream-mind-lucid/Dream-mind-lucid/DEPLOYMENT_SCAN_REPORT.md", "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    main()