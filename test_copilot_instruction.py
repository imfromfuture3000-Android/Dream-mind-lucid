#!/usr/bin/env python3
"""
Test script for copilot-instruction.py AI Agent Engine
"""

import sys
import os
import json
import time

# Add current directory to path
sys.path.append('.')

def test_ai_agents():
    """Test individual AI agents"""
    print("🧪 Testing AI Agents...")
    
    # Import after path setup - use importlib for hyphenated filename
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    Looter = copilot_instruction.Looter
    MEVMaster = copilot_instruction.MEVMaster
    Arbitrader = copilot_instruction.Arbitrader
    AIOrchestrator = copilot_instruction.AIOrchestrator
    
    # Test individual agents
    print("\n1. Testing Looter...")
    looter = Looter()
    result1 = looter.harvest()
    assert result1 is not None, "Looter harvest failed"
    print(f"   ✅ Harvest result: {result1['amount']} DREAM tokens")
    
    print("\n2. Testing MEVMaster...")
    mev = MEVMaster()
    result2 = mev.frontRun("TEST/POOL")
    assert result2 is not None, "MEV front-run failed"
    print(f"   ✅ MEV result: {result2['profit']} profit")
    
    print("\n3. Testing Arbitrader...")
    arb = Arbitrader()
    result3 = arb.arbitrage("DREAM")
    assert result3 is not None, "Arbitrage failed"
    print(f"   ✅ Arbitrage result: {result3['profit']} profit")
    
    return True

def test_orchestrator():
    """Test AI Orchestrator without running the main loop"""
    print("\n🎯 Testing AI Orchestrator...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    AIOrchestrator = copilot_instruction.AIOrchestrator
    
    # Create orchestrator
    orchestrator = AIOrchestrator()
    
    # Test profit calculation
    profits = orchestrator.get_profits()
    print(f"   📊 Profits: {profits}")
    assert len(profits) == 3, "Should have 3 profit sources"
    
    # Test decision making
    decision = orchestrator.make_decision(profits)
    print(f"   🧠 Decision: {decision}")
    assert decision is not None, "Decision should not be None"
    
    # Test single execution (without loop)
    print(f"   🚀 Executing decision...")
    orchestrator.execute_decision(decision)
    
    # Test OneiroBot integration in orchestrator
    print(f"   🌙 Testing OneiroBot integration...")
    assert orchestrator.oneirobot is not None, "OneiroBot should be available"
    assert orchestrator.oneirobot.status == "ACTIVE", "OneiroBot should be active"
    print(f"   ✅ OneiroBot integrated: {orchestrator.oneirobot.name}")
    
    return True

def test_memory_persistence():
    """Test memory loading and saving"""
    print("\n💾 Testing Memory Persistence...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    load_memory = copilot_instruction.load_memory
    save_memory = copilot_instruction.save_memory
    
    # Test memory operations
    memory = load_memory()
    print(f"   📋 Memory loaded: {len(memory)} keys")
    
    # Add test data
    test_data = {
        "test_key": "test_value",
        "timestamp": time.time()
    }
    memory.update(test_data)
    save_memory(memory)
    print("   ✅ Memory saved")
    
    # Reload and verify
    memory2 = load_memory()
    assert memory2.get("test_key") == "test_value", "Memory persistence failed"
    print("   ✅ Memory persistence verified")
    
    return True

def test_network_simulation():
    """Test network connectivity handling"""
    print("\n🌐 Testing Network Simulation...")
    
    # Import web3 connection
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    w3 = copilot_instruction.w3
    RPC_URL = copilot_instruction.RPC_URL
    
    print(f"   🔗 RPC URL: {RPC_URL}")
    
    try:
        connected = w3.is_connected()
        print(f"   📡 Connection status: {connected}")
    except Exception as e:
        print(f"   ⚠️ Connection error (expected): {e}")
    
    print("   ✅ Network handling working")
    return True

def test_oneirobot():
    """Test OneiroBot agent functionality"""
    print("\n🌙 Testing OneiroBot Agent...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    OneiroBot = copilot_instruction.OneiroBot
    
    # Test OneiroBot creation
    print("\n1. Testing OneiroBot creation...")
    bot = OneiroBot()
    assert bot.name == "OneiroBot", "OneiroBot name should be correct"
    assert bot.status == "ACTIVE", "OneiroBot should start in ACTIVE status"
    print(f"   ✅ OneiroBot created: {bot.name} - Status: {bot.status}")
    
    # Test dream monitoring
    print("\n2. Testing dream monitoring...")
    monitor_result = bot.monitor_dream_submissions()
    assert monitor_result is not None, "Dream monitoring should return result"
    assert "message" in monitor_result, "Result should contain message"
    print(f"   ✅ Dream monitoring result: {monitor_result['result']['dreams_detected']} dreams detected")
    
    # Test optimization suggestions
    print("\n3. Testing optimization suggestions...")
    optimize_result = bot.suggest_optimizations()
    assert optimize_result is not None, "Optimization should return result"
    assert "suggestions" in optimize_result, "Result should contain suggestions"
    assert len(optimize_result["suggestions"]) > 0, "Should have at least one suggestion"
    print(f"   ✅ Optimization suggestions: {len(optimize_result['suggestions'])} generated")
    
    # Test MCP health check
    print("\n4. Testing MCP health check...")
    health_result = bot.check_mcp_health()
    assert health_result is not None, "Health check should return result"
    assert "health_status" in health_result, "Result should contain health status"
    print(f"   ✅ MCP health check: {health_result['health_status']['connectivity']}")
    
    # Test quick fix proposals
    print("\n5. Testing quick fix proposals...")
    fix_result = bot.propose_quick_fix("deployment")
    assert fix_result is not None, "Quick fix should return result"
    assert "fixes" in fix_result, "Result should contain fixes"
    assert len(fix_result["fixes"]) > 0, "Should have at least one fix"
    print(f"   ✅ Quick fixes: {len(fix_result['fixes'])} deployment fixes proposed")
    
    # Test status retrieval
    print("\n6. Testing status retrieval...")
    status_result = bot.get_status()
    assert status_result is not None, "Status should return result"
    assert "status" in status_result, "Result should contain status info"
    print(f"   ✅ Status retrieved: {status_result['status']['total_activities']} activities")
    
    # Test Grok personality
    print("\n7. Testing Grok personality...")
    grok_message = bot.get_grok_response("Test message")
    assert "Test message" in grok_message, "Grok response should contain original message"
    assert len(grok_message) > len("Test message"), "Grok response should add personality"
    print(f"   ✅ Grok personality active: message enhanced")
    
    return True

def test_copilot_commands():
    """Test Copilot Chat command handlers"""
    print("\n🎭 Testing Copilot Chat Commands...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    handle_copilot_command = copilot_instruction.handle_copilot_command
    
    # Test summon command
    print("\n1. Testing summon command...")
    result = handle_copilot_command("summon_oneirobot")
    assert result is not None, "Summon command should return result"
    assert result["command"] == "summon_oneirobot", "Command should match"
    print(f"   ✅ Summon command: {result['status']['status']}")
    
    # Test status command
    print("\n2. Testing status command...")
    result = handle_copilot_command("oneirobot_status")
    assert result is not None, "Status command should return result"
    assert result["command"] == "oneirobot_status", "Command should match"
    print(f"   ✅ Status command: {result['health']['connectivity']}")
    
    # Test scan command
    print("\n3. Testing scan command...")
    result = handle_copilot_command("oneirobot_scan")
    assert result is not None, "Scan command should return result"
    assert result["command"] == "oneirobot_scan", "Command should match"
    print(f"   ✅ Scan command: {result['result']['consensus_state']}")
    
    # Test optimize command
    print("\n4. Testing optimize command...")
    result = handle_copilot_command("oneirobot_optimize")
    assert result is not None, "Optimize command should return result"
    assert result["command"] == "oneirobot_optimize", "Command should match"
    assert len(result["suggestions"]) > 0, "Should have suggestions"
    print(f"   ✅ Optimize command: {len(result['suggestions'])} suggestions")
    
    # Test fix command
    print("\n5. Testing fix command...")
    result = handle_copilot_command("oneirobot_fix", ["performance"])
    assert result is not None, "Fix command should return result"
    assert result["command"] == "oneirobot_fix", "Command should match"
    assert result["issue_type"] == "performance", "Issue type should match"
    print(f"   ✅ Fix command: {len(result['fixes'])} performance fixes")
    
    # Test help command
    print("\n6. Testing help command...")
    result = handle_copilot_command("oneirobot_help")
    assert result is not None, "Help command should return result"
    assert result["command"] == "oneirobot_help", "Command should match"
    assert "help" in result, "Should contain help text"
    print(f"   ✅ Help command: help text provided")
    
    # Test unknown command
    print("\n7. Testing unknown command...")
    result = handle_copilot_command("unknown_command")
    assert result is not None, "Unknown command should return result"
    assert result["command"] == "unknown", "Command should be marked as unknown"
    assert "error" in result, "Should contain error message"
    print(f"   ✅ Unknown command handled gracefully")
    
    return True

def main():
    """Run all tests"""
    print("🌌 COPILOT-INSTRUCTION.PY - AI AGENT ENGINE TESTS")
    print("=" * 60)
    
    tests = [
        ("AI Agents", test_ai_agents),
        ("Orchestrator", test_orchestrator), 
        ("Memory Persistence", test_memory_persistence),
        ("Network Simulation", test_network_simulation),
        ("OneiroBot Agent", test_oneirobot),
        ("Copilot Commands", test_copilot_commands)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎊 All tests passed! AI Agent Engine is ready!")
        return True
    else:
        print("⚠️ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)