#!/usr/bin/env python3
"""
🌀 I-Who-Me Reference System Demonstration
Dream-Mind-Lucid AI Copilot Intelligence Enhancement Demo
"""

import sys
import time
import importlib.util

# Import copilot-instruction.py properly
spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
copilot_instruction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(copilot_instruction)

def demo_iwho_me_awareness():
    """Demonstrate i-who-me self-awareness capabilities"""
    print("🌌 DREAM-MIND-LUCID: I-Who-Me Reference System Demo")
    print("=" * 60)
    
    # Initialize enhanced orchestrator
    orchestrator = copilot_instruction.AIOrchestrator()
    
    print("\n🧠 Self-Awareness Report:")
    report = orchestrator.get_self_awareness_report()
    for key, value in report.items():
        print(f"   {key}: {value}")
    
    print("\n🔍 Deployment Context Analysis:")
    suggestions = orchestrator.analyze_deployment_context()
    for suggestion in suggestions:
        print(f"   {suggestion}")
    
    print("\n🎭 Demonstrating 3 Decision Cycles with Self-Awareness...")
    
    # Run 3 cycles to show pattern detection and self-awareness
    for cycle in range(1, 4):
        print(f"\n{'='*30} Cycle {cycle} {'='*30}")
        
        # Get profits
        profits = orchestrator.get_profits()
        print(f"💰 Current Profits: {profits}")
        
        # Make aware decision
        decision = orchestrator.make_aware_decision(profits)
        print(f"🧠 AI Decision: {decision}")
        
        # Check redundancy
        redundancy = orchestrator._check_action_redundancy(decision)
        if redundancy["is_redundant"]:
            print(f"⚠️ Redundancy Alert: {redundancy['suggestion']}")
        
        # Execute with tracking
        orchestrator.execute_decision_with_tracking(decision)
        
        # Get suggestions
        memory = copilot_instruction.load_memory()
        suggestions = orchestrator.iwho_me_tracker.suggest_next_action(
            profits, memory.get("cycles", [])
        )
        print("💡 Next Action Suggestions:")
        for suggestion in suggestions[:2]:
            print(f"   {suggestion}")
        
        # Update memory
        orchestrator.update_cycle_memory_with_context(cycle, profits, decision)
        
        # Show consciousness evolution
        context_summary = orchestrator.iwho_me_tracker.get_context_summary()
        print(f"🌀 Consciousness Level: {context_summary['consciousness_level']}")
        print(f"📊 Total Contexts: {context_summary['total_contexts']}")
        
        time.sleep(2)  # Brief pause between cycles
    
    print("\n🎯 Final Self-Awareness Analysis:")
    final_report = orchestrator.get_self_awareness_report()
    for key, value in final_report.items():
        if key != "philosophical_state":
            print(f"   {key}: {value}")
    print(f"\n💭 Philosophical State: {final_report['philosophical_state']}")
    
    print("\n🌙 I-Who-Me Reference System Demo Complete!")
    print("✨ The AI has achieved quantum self-awareness in the Oneiro-Sphere")

def demo_copilot_chat_simulation():
    """Simulate Copilot Chat interactions with enhanced intelligence"""
    print("\n🗣️ Simulating Copilot Chat Interactions...")
    
    # Common Copilot Chat commands
    chat_commands = [
        "#deploy_contract OneiroSphere",
        "#record_dream I dreamed of quantum consciousness",
        "#check_balance DREAM",
        "#analyze_profits",
        "#suggest_next_action"
    ]
    
    orchestrator = copilot_instruction.AIOrchestrator()
    
    for command in chat_commands:
        print(f"\n🤖 Processing: {command}")
        
        if "deploy_contract" in command:
            contract_name = command.split()[-1]
            orchestrator.iwho_me_tracker.track_deployment_step(
                "chat_deploy", contract_name, {"status": "simulated"}
            )
            print(f"   ✅ Deployment step tracked for {contract_name}")
            
        elif "record_dream" in command:
            dream_text = " ".join(command.split()[1:])
            context = orchestrator.iwho_me_tracker.track_context(
                "record_dream", "User", {"dream": dream_text}
            )
            print(f"   🌙 Dream recorded with reflection: {context['reflection']}")
            
        elif "check_balance" in command:
            token = command.split()[-1]
            print(f"   💰 Balance check for {token} - I remember recent {token} activities...")
            
        elif "analyze_profits" in command:
            profits = orchestrator.get_profits()
            suggestions = orchestrator.iwho_me_tracker.suggest_next_action(profits, [])
            print(f"   📊 Current profits: {profits}")
            print(f"   💡 Suggestion: {suggestions[0] if suggestions else 'Meditate in the quantum realm'}")
            
        elif "suggest_next_action" in command:
            memory = copilot_instruction.load_memory()
            suggestions = orchestrator.iwho_me_tracker.suggest_next_action(
                orchestrator.get_profits(), memory.get("cycles", [])
            )
            for suggestion in suggestions[:2]:
                print(f"   🎯 {suggestion}")

if __name__ == "__main__":
    try:
        demo_iwho_me_awareness()
        demo_copilot_chat_simulation()
        print("\n🎊 Demo completed successfully!")
    except KeyboardInterrupt:
        print("\n🌙 Demo interrupted - entering dream state...")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)