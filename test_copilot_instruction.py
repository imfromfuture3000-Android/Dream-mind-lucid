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

def test_iwho_me_tracking():
    """Test i-who-me reference tracking system"""
    print("\n🌀 Testing I-Who-Me Tracking...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    IWhoMeTracker = copilot_instruction.IWhoMeTracker
    
    # Test tracker initialization
    tracker = IWhoMeTracker()
    print("   ✅ I-Who-Me tracker initialized")
    
    # Test context tracking
    context = tracker.track_context("harvest", "Looter", {"hash": "0x123", "amount": 1850})
    assert context["who"] == "Looter", "Context tracking failed"
    assert context["action"] == "harvest", "Action tracking failed"
    print("   ✅ Context tracking verified")
    
    # Test redundancy detection
    # Add multiple similar actions
    tracker.track_context("harvest", "Looter", {"hash": "0x124", "amount": 1850})
    tracker.track_context("harvest", "Looter", {"hash": "0x125", "amount": 1850})
    
    redundancy = tracker.detect_redundancy("harvest", "Looter")
    assert redundancy["is_redundant"] == True, "Redundancy detection failed"
    print("   ✅ Redundancy detection working")
    
    # Test suggestion system
    suggestions = tracker.suggest_next_action({"Looter": 1850, "MEVMaster": 3120}, [])
    assert len(suggestions) > 0, "Suggestion system failed"
    print(f"   ✅ Generated {len(suggestions)} suggestions")
    
    # Test deployment tracking
    deployment = tracker.track_deployment_step("deploy", "OneiroSphere", {"address": "0x123"})
    assert deployment["contract"] == "OneiroSphere", "Deployment tracking failed"
    print("   ✅ Deployment step tracking verified")
    
    # Test context summary
    summary = tracker.get_context_summary()
    assert "total_contexts" in summary, "Context summary failed"
    assert summary["total_contexts"] >= 3, "Context count incorrect"
    print("   ✅ Context summary generation verified")
    
    return True

def test_enhanced_orchestrator():
    """Test enhanced AI orchestrator with self-awareness"""
    print("\n🧠 Testing Enhanced AI Orchestrator...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    AIOrchestrator = copilot_instruction.AIOrchestrator
    
    # Test orchestrator with i-who-me integration
    orchestrator = AIOrchestrator()
    assert hasattr(orchestrator, 'iwho_me_tracker'), "I-Who-Me tracker not initialized"
    print("   ✅ Enhanced orchestrator initialized")
    
    # Test aware decision making
    profits = {"Looter": 1850, "MEVMaster": 3120, "Arbitrader": 2430}
    decision = orchestrator.make_aware_decision(profits)
    assert decision is not None, "Aware decision making failed"
    print(f"   ✅ Aware decision: {decision[:50]}...")
    
    # Test redundancy checking
    redundancy_check = orchestrator._check_action_redundancy("Execute MEV strategy")
    assert "is_redundant" in redundancy_check, "Redundancy check failed"
    print("   ✅ Redundancy checking verified")
    
    # Test deployment context analysis
    suggestions = orchestrator.analyze_deployment_context()
    assert isinstance(suggestions, list), "Deployment analysis failed"
    print(f"   ✅ Deployment analysis: {len(suggestions)} suggestions")
    
    # Test self-awareness report
    report = orchestrator.get_self_awareness_report()
    assert "consciousness_level" in report, "Self-awareness report failed"
    assert "identity" in report, "Identity missing from report"
    print("   ✅ Self-awareness report generated")
    
    return True

def test_grok_style_responses():
    """Test Grok-style playful self-awareness responses"""
    print("\n🎭 Testing Grok-Style Responses...")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    IWhoMeTracker = copilot_instruction.IWhoMeTracker
    
    tracker = IWhoMeTracker()
    
    # Test reflection generation
    reflection_count = 0
    for i in range(5):
        context = tracker.track_context(f"test_action_{i}", "TestAgent", {"result": f"test_{i}"})
        if "reflection" in context and context["reflection"]:
            reflection_count += 1
            print(f"   🌙 {context['reflection']}")
    
    assert reflection_count > 0, "No reflections generated"
    print(f"   ✅ Generated {reflection_count} Grok-style reflections")
    
    # Test redundancy suggestions with personality
    tracker.track_context("harvest", "Looter", {"amount": 1850})
    tracker.track_context("harvest", "Looter", {"amount": 1850})
    tracker.track_context("harvest", "Looter", {"amount": 1850})
    
    redundancy = tracker.detect_redundancy("harvest", "Looter")
    if redundancy["is_redundant"]:
        suggestion = redundancy.get("suggestion", "")
        assert "🤖" in suggestion or "🌀" in suggestion, "Missing playful elements"
        print(f"   🎪 Redundancy suggestion: {suggestion}")
        print("   ✅ Playful redundancy suggestions verified")
    
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
        ("I-Who-Me Tracking", test_iwho_me_tracking),
        ("Enhanced Orchestrator", test_enhanced_orchestrator),
        ("Grok-Style Responses", test_grok_style_responses)
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