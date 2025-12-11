#!/usr/bin/env python3
"""
Demo script for copilot-instruction.py AI Agent Engine
Shows the AI agents working for a few cycles
"""

import sys
import time
import importlib.util

def run_demo():
    """Run a demonstration of the AI Agent Engine"""
    print("🌌 DREAM-MIND-LUCID: AI Agent Demo")
    print("=" * 50)
    
    # Import the AI Agent Engine
    spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
    copilot_instruction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_instruction)
    
    # Create orchestrator
    orchestrator = copilot_instruction.AIOrchestrator()
    
    print("\n🚀 Running 3-cycle demonstration...")
    
    # Run for 3 cycles only
    for cycle in range(1, 4):
        try:
            print(f"\n{'='*30}")
            print(f"🔄 Demo Cycle #{cycle}")
            print(f"{'='*30}")
            
            # Get current profits
            profits = orchestrator.get_profits()
            print(f"📊 Current Profits: {profits}")
            
            # Make AI decision
            decision = orchestrator.make_decision(profits)
            print(f"[🧠] AI Decision: {decision}")
            
            # Execute decision
            orchestrator.execute_decision(decision)
            
            # Update memory
            orchestrator.update_cycle_memory(cycle, profits, decision)
            
            print(f"[✅] Cycle {cycle} completed successfully")
            
            if cycle < 3:
                print("⏰ Waiting 3 seconds before next cycle...")
                time.sleep(3)
                
        except Exception as e:
            print(f"[❌] Error in cycle {cycle}: {e}")
    
    print(f"\n{'='*50}")
    print("🎊 Demo completed successfully!")
    print("📝 Check iem_memory.json for detailed logs")
    print("🚀 To run the full AI Agent Engine: python copilot-instruction.py")
    print("💡 Press Ctrl+C to stop the main engine when running")

if __name__ == "__main__":
    run_demo()