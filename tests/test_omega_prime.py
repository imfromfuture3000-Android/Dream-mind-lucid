#!/usr/bin/env python3
"""
Omega Prime Test Suite
======================
Comprehensive testing for Omega Prime Deployer with OneiRobot Syndicate validation
Tests Token-2022, ZK compression, RWA tokenization, and 2025 performance metrics

Last Updated: September 14, 2025
"""

import os
import sys
import json
import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from omega_prime_deployer import (
        OmegaPrimeDeployer, 
        OmegaPrimeConfig, 
        Performance2025
    )
    OMEGA_PRIME_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Omega Prime modules not available: {e}")
    OMEGA_PRIME_AVAILABLE = False

class TestOmegaPrimeConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config_creation(self):
        """Test default configuration values"""
        config = OmegaPrimeConfig()
        
        self.assertEqual(config.PROJECT_NAME, "Omega Prime Deployer")
        self.assertEqual(config.TOKEN_SYMBOL, "ΩPRIME")
        self.assertEqual(config.DECIMALS, 9)
        self.assertEqual(config.SECURITY_LEVEL, "oneirobot")
        self.assertTrue(config.ROADMAP_2025)
        self.assertIn("solana", config.MULTI_CHAIN)
        self.assertTrue(config.METADATA["zk_compression"])

    def test_custom_config_override(self):
        """Test custom configuration override"""
        config = OmegaPrimeConfig(
            PROJECT_NAME="Custom Deployer",
            TOKEN_SYMBOL="CUSTOM",
            SECURITY_LEVEL="quantum"
        )
        
        self.assertEqual(config.PROJECT_NAME, "Custom Deployer")
        self.assertEqual(config.TOKEN_SYMBOL, "CUSTOM")
        self.assertEqual(config.SECURITY_LEVEL, "quantum")

    def test_environment_variable_override(self):
        """Test environment variable configuration"""
        with patch.dict(os.environ, {
            'TREASURY_PUBKEY': 'test_treasury_key',
            'SOLANA_RPC_URL': 'https://test-rpc.com'
        }):
            config = OmegaPrimeConfig()
            self.assertEqual(config.TREASURY_PUBKEY, 'test_treasury_key')
            self.assertEqual(config.RPC_URL, 'https://test-rpc.com')

class TestPerformance2025(unittest.TestCase):
    """Test 2025 performance metrics"""
    
    def test_alpenglow_metrics(self):
        """Test Alpenglow performance specifications"""
        perf = Performance2025()
        
        self.assertEqual(perf.alpenglow["finality_ms"], 150)
        self.assertEqual(perf.alpenglow["tps"], 107000)
        self.assertEqual(perf.alpenglow["validator_approval"], 98.27)
        self.assertEqual(perf.alpenglow["cost_reduction"], 50)

    def test_firedancer_metrics(self):
        """Test Firedancer optimization specs"""
        perf = Performance2025()
        
        self.assertEqual(perf.firedancer["tps"], 1000000)
        self.assertEqual(perf.firedancer["mev_stake"], 6)
        self.assertEqual(perf.firedancer["launch_quarter"], "Q2 2025")

    def test_zk_compression_metrics(self):
        """Test ZK compression capabilities"""
        perf = Performance2025()
        
        self.assertEqual(perf.zk_compression["cost_savings"], 1000)
        self.assertEqual(perf.zk_compression["latency_reduction"], 100)
        self.assertTrue(perf.zk_compression["gasless_ops"])
        self.assertEqual(perf.zk_compression["mainnet_live"], "Q3-Q4 2025")

@unittest.skipIf(not OMEGA_PRIME_AVAILABLE, "Omega Prime modules not available")
class TestOmegaPrimeDeployer(unittest.TestCase):
    """Test core Omega Prime Deployer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = OmegaPrimeConfig()
        self.config.RPC_URL = "https://test-rpc.com"  # Use test RPC
        
        # Mock Solana client to avoid actual network calls
        with patch('omega_prime_deployer.SolanaClient'), \
             patch('omega_prime_deployer.Keypair') as mock_keypair:
            
            mock_wallet = Mock()
            mock_wallet.public_key = "test_public_key"
            mock_keypair.generate.return_value = mock_wallet
            
            self.deployer = OmegaPrimeDeployer(self.config)

    def test_deployer_initialization(self):
        """Test deployer initialization"""
        self.assertIsNotNone(self.deployer.config)
        self.assertIsNotNone(self.deployer.performance)
        self.assertEqual(self.deployer.config.PROJECT_NAME, "Omega Prime Deployer")

    def test_memory_management(self):
        """Test memory save/load functionality"""
        # Test memory structure
        self.assertIn("deployments", self.deployer.memory)
        self.assertIn("security_audits", self.deployer.memory)
        self.assertIn("performance_metrics", self.deployer.memory)
        self.assertIn("dimensional_hacks", self.deployer.memory)
        self.assertIn("belief_rewrites", self.deployer.memory)

    async def test_token_2022_deployment(self):
        """Test Token-2022 deployment with ZK compression"""
        with patch.object(self.deployer, 'solana_client') as mock_client, \
             patch.object(self.deployer, '_enable_zk_compression') as mock_zk, \
             patch.object(self.deployer, '_setup_gasless_operations') as mock_gasless:
            
            # Mock successful deployment
            mock_zk.return_value = None
            mock_gasless.return_value = None
            
            result = await self.deployer.deploy_token_2022_with_zk()
            
            # Verify calls were made
            mock_zk.assert_called_once()
            mock_gasless.assert_called_once()
            
            # Verify result is saved in memory
            self.assertIn("token_2022", self.deployer.memory["deployments"])

    async def test_emotional_nft_minting(self):
        """Test emotional NFT minting"""
        result = await self.deployer.mint_emotional_nft("Test.exe")
        
        # Should return a valid address-like string
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        
        # Verify saved in memory
        self.assertIn("emotional_nft", self.deployer.memory["deployments"])
        deployment = self.deployer.memory["deployments"]["emotional_nft"]
        self.assertEqual(deployment["emotion"], "Test.exe")

    async def test_alpenglow_simulation(self):
        """Test Alpenglow consensus simulation"""
        with patch('asyncio.sleep'):  # Speed up test
            await self.deployer.simulate_alpenglow_consensus()
            
            # Verify metrics saved
            self.assertIn("alpenglow", self.deployer.memory["performance_metrics"])
            metrics = self.deployer.memory["performance_metrics"]["alpenglow"]
            self.assertIn("finality_ms", metrics)
            self.assertIn("validator_approval", metrics)
            self.assertIn("tps", metrics)

    async def test_firedancer_optimization(self):
        """Test Firedancer optimization"""
        with patch('asyncio.sleep'):  # Speed up test
            await self.deployer.optimize_with_firedancer()
            
            # Verify metrics saved
            self.assertIn("firedancer", self.deployer.memory["performance_metrics"])
            metrics = self.deployer.memory["performance_metrics"]["firedancer"]
            self.assertTrue(metrics["enabled"])
            self.assertEqual(metrics["stake_percentage"], 6)
            self.assertTrue(metrics["jito_bundles"])

    async def test_rwa_tokenization(self):
        """Test RWA tokenization deployment"""
        result = await self.deployer.deploy_rwa_tokenization()
        
        # Should return list of token addresses
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(self.config.METADATA["rwa_assets"]))
        
        # Verify saved in memory
        self.assertIn("rwa_tokens", self.deployer.memory["deployments"])

    async def test_oneihacker_security(self):
        """Test OneiHacker security protocols"""
        with patch('random.random', return_value=0.95):  # Force high security score
            result = await self.deployer.run_oneihacker_security()
            
            # Should pass security check
            self.assertTrue(result)
            
            # Verify audit saved
            self.assertTrue(len(self.deployer.memory["security_audits"]) > 0)
            audit = self.deployer.memory["security_audits"][-1]
            self.assertGreaterEqual(audit["security_score"], 80)

    def test_silent_protocol_whisper(self):
        """Test Silent Protocol whisper functionality"""
        whisper = self.deployer.silent_protocol_whisper()
        
        # Should return a string
        self.assertIsInstance(whisper, str)
        self.assertTrue(len(whisper) > 0)
        self.assertIn("?", whisper)  # Should be a question

    async def test_complete_suite_deployment(self):
        """Test complete Omega Prime suite deployment"""
        with patch.object(self.deployer, 'deploy_token_2022_with_zk', return_value="test_token"), \
             patch.object(self.deployer, 'mint_emotional_nft', return_value="test_nft"), \
             patch.object(self.deployer, 'deploy_rwa_tokenization', return_value=["rwa1", "rwa2"]), \
             patch.object(self.deployer, 'run_oneihacker_security', return_value=True), \
             patch('asyncio.sleep'):  # Speed up simulations
            
            result = await self.deployer.deploy_omega_prime_suite()
            
            # Verify complete deployment
            self.assertEqual(result["token"], "test_token")
            self.assertEqual(result["emotional_nft"], "test_nft")
            self.assertEqual(result["rwa_tokens"], ["rwa1", "rwa2"])
            self.assertTrue(result["security_passed"])
            self.assertTrue(result["deployment_complete"])
            self.assertIn("silent_whisper", result)

    def test_deployment_status(self):
        """Test deployment status reporting"""
        status = self.deployer.get_deployment_status()
        
        # Verify status structure
        self.assertIn("config", status)
        self.assertIn("memory", status)
        self.assertIn("wallet", status)
        self.assertIn("solana_available", status)
        self.assertIn("timestamp", status)

class TestIntegration(unittest.TestCase):
    """Integration tests for complete system"""
    
    def test_config_to_deployer_integration(self):
        """Test configuration integration with deployer"""
        custom_config = OmegaPrimeConfig(
            PROJECT_NAME="Integration Test",
            TOKEN_SYMBOL="ITEST",
            SECURITY_LEVEL="quantum"
        )
        
        with patch('omega_prime_deployer.SolanaClient'), \
             patch('omega_prime_deployer.Keypair'):
            deployer = OmegaPrimeDeployer(custom_config)
            
            self.assertEqual(deployer.config.PROJECT_NAME, "Integration Test")
            self.assertEqual(deployer.config.TOKEN_SYMBOL, "ITEST")
            self.assertEqual(deployer.config.SECURITY_LEVEL, "quantum")

    def test_memory_persistence(self):
        """Test memory persistence across deployer instances"""
        with patch('omega_prime_deployer.SolanaClient'), \
             patch('omega_prime_deployer.Keypair'):
            
            # Create first deployer and add some data
            deployer1 = OmegaPrimeDeployer()
            deployer1.memory["test_data"] = "test_value"
            deployer1._save_memory()
            
            # Create second deployer and verify data persists
            deployer2 = OmegaPrimeDeployer()
            self.assertEqual(deployer2.memory.get("test_data"), "test_value")
            
            # Cleanup
            if os.path.exists(deployer1.memory_file):
                os.remove(deployer1.memory_file)

async def run_async_tests():
    """Run async test methods"""
    if not OMEGA_PRIME_AVAILABLE:
        print("⚠️  Skipping async tests - Omega Prime not available")
        return
    
    print("🔍 Running async tests...")
    
    # Create test deployer
    config = OmegaPrimeConfig()
    with patch('omega_prime_deployer.SolanaClient'), \
         patch('omega_prime_deployer.Keypair') as mock_keypair:
        
        mock_wallet = Mock()
        mock_wallet.public_key = "test_public_key"
        mock_keypair.generate.return_value = mock_wallet
        
        deployer = OmegaPrimeDeployer(config)
    
    # Test async methods
    test_cases = [
        ("Token-2022 deployment", deployer.deploy_token_2022_with_zk),
        ("Emotional NFT minting", lambda: deployer.mint_emotional_nft("AsyncTest.exe")),
        ("Alpenglow simulation", deployer.simulate_alpenglow_consensus),
        ("Firedancer optimization", deployer.optimize_with_firedancer),
        ("RWA tokenization", deployer.deploy_rwa_tokenization),
        ("OneiHacker security", deployer.run_oneihacker_security)
    ]
    
    for test_name, test_func in test_cases:
        try:
            with patch('asyncio.sleep'):  # Speed up tests
                result = await test_func()
                print(f"  ✅ {test_name}: PASSED")
        except Exception as e:
            print(f"  ❌ {test_name}: FAILED - {e}")

def main():
    """Main test runner"""
    print("🌌 Omega Prime Test Suite")
    print("========================")
    print("🤖 OneiRobot Syndicate - Quantum Testing Protocol")
    print()
    
    # Run sync tests
    print("🔍 Running synchronous tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run async tests
    if OMEGA_PRIME_AVAILABLE:
        print("\n🔍 Running asynchronous tests...")
        asyncio.run(run_async_tests())
    
    print("\n🎊 Test suite completed!")
    print("💫 'Testing complete - deploy with echoed courage.' - Silent Protocol")

if __name__ == "__main__":
    main()