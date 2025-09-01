#!/usr/bin/env python3
"""
Validate Dream-Mind-Lucid Requirements
-------------------------------------
This script validates that requirements.txt is properly formatted
and compatible with the project dependencies.

Usage: python3 validate_requirements.py
"""

import sys
import os

# Add deprecation warning suppression for pkg_resources
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

try:
    import pkg_resources
except ImportError:
    print("❌ pkg_resources not available. Please install setuptools.")
    sys.exit(1)

def validate_requirements():
    """Validate requirements.txt file format and dependencies."""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found")
        return False
    
    print("🔍 Validating Dream-Mind-Lucid requirements.txt...")
    print("=" * 50)
    
    try:
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Check for old placeholder
        if '<content_of_requirements.txt>' in content:
            print("❌ File still contains placeholder text")
            return False
        
        # Parse and validate each requirement
        valid_requirements = []
        for line_num, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    req = pkg_resources.Requirement.parse(line)
                    valid_requirements.append((req.project_name, str(req.specifier)))
                except Exception as e:
                    print(f"❌ Line {line_num}: Invalid requirement '{line}' - {e}")
                    return False
        
        # Report results
        print(f"✅ Requirements file syntax is valid!")
        print(f"📦 Found {len(valid_requirements)} package requirements:")
        
        expected_packages = {
            'web3': 'Web3 blockchain interaction',
            'py-solc-x': 'Solidity compiler',
            'ipfshttpclient': 'IPFS client',
            'modelcontextprotocol': 'MCP server',
            'PyExifTool': 'Image metadata extraction'
        }
        
        for pkg_name, version_spec in valid_requirements:
            description = expected_packages.get(pkg_name, 'Additional dependency')
            print(f"   📍 {pkg_name} {version_spec} - {description}")
        
        # Check for missing expected packages
        found_packages = [pkg for pkg, _ in valid_requirements]
        missing = set(expected_packages.keys()) - set(found_packages)
        if missing:
            print(f"⚠️  Missing expected packages: {', '.join(missing)}")
        
        print("\n🎯 Compatibility Notes:")
        print("   • Python 3.11+ required")
        print("   • Biconomy SDK needs manual installation")
        print("   • SKALE blockchain compatible")
        
        print(f"\n✅ Requirements validation successful!")
        print(f"💡 To install: pip install -r {requirements_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating requirements: {e}")
        return False

if __name__ == "__main__":
    success = validate_requirements()
    if not success:
        print("\n❌ Requirements validation failed!")
        sys.exit(1)
    else:
        print("\n🎉 All validations passed!")