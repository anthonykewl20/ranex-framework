#!/usr/bin/env python3
"""
Ranex Framework - Workflow Management Demo

This demo showcases project workflow and phase management.
It demonstrates:
1. Project phase management (Requirements → Design → Implementation)
2. Phase locking/unlocking
3. Task tracking
4. Workflow state persistence

Run: python examples/workflow_management_demo.py
"""

import os
import tempfile
import shutil
from ranex_core import WorkflowManager, ProjectPhase


def demo_workflow_management():
    """Demonstrate workflow management capabilities."""
    print("=" * 70)
    print("Ranex Framework - Workflow Management Demo")
    print("=" * 70)
    print()
    
    # Create temporary project directory
    temp_dir = tempfile.mkdtemp()
    print(f"Created temporary project: {temp_dir}")
    
    try:
        manager = WorkflowManager(temp_dir)
        print("✅ Workflow manager initialized")
        print(f"   Current phase: {manager.get_phase()}")
        print()
        
        # Demo 1: Phase progression
        print("📝 Demo 1: Phase Progression")
        print("-" * 70)
        
        phases = [
            ProjectPhase.Requirements,
            ProjectPhase.Design,
            ProjectPhase.Implementation,
            ProjectPhase.Review,
            ProjectPhase.Maintenance,
        ]
        
        print("Project phases (in order):")
        for i, phase in enumerate(phases, 1):
            print(f"  {i}. {phase}")
        print()
        
        print("Transitioning through phases:")
        for phase in phases:
            try:
                manager.set_phase(phase)
                current = manager.get_phase()
                print(f"  ✅ Set phase to: {current}")
            except Exception as e:
                print(f"  ❌ Error setting phase: {e}")
        print()
        
        # Demo 2: Task management
        print("📝 Demo 2: Task Management")
        print("-" * 70)
        
        tasks = [
            "Implement payment feature",
            "Add user authentication",
            "Create database migrations",
        ]
        
        print("Managing tasks:")
        for task in tasks:
            try:
                manager.set_task(task)
                print(f"  ✅ Set active task: {task}")
                print(f"     Current phase: {manager.get_phase()}")
                
                # Complete task
                manager.complete_task()
                print(f"  ✅ Completed task: {task}")
            except Exception as e:
                print(f"  ❌ Error managing task: {e}")
        print()
        
        # Demo 3: Phase locking
        print("📝 Demo 3: Phase Locking")
        print("-" * 70)
        print("Ranex enforces phase-based development:")
        print()
        print("  Requirements Phase:")
        print("    • Write requirements documents")
        print("    • Define feature specifications")
        print("    • ❌ Cannot write code")
        print()
        print("  Design Phase:")
        print("    • Create architecture diagrams")
        print("    • Design database schemas")
        print("    • ❌ Cannot write code")
        print()
        print("  Implementation Phase:")
        print("    • ✅ Can write code")
        print("    • ✅ Can create features")
        print("    • ✅ Can run tests")
        print()
        print("  Review Phase:")
        print("    • Code review")
        print("    • Testing")
        print("    • ❌ Limited code changes")
        print()
        print("  Maintenance Phase:")
        print("    • Bug fixes")
        print("    • Performance improvements")
        print("    • ✅ Can write code")
        print()
        
        # Demo 4: Workflow state persistence
        print("📝 Demo 4: Workflow State Persistence")
        print("-" * 70)
        
        # Create new manager instance (simulates restart)
        manager2 = WorkflowManager(temp_dir)
        print(f"Loaded workflow state:")
        print(f"  Current phase: {manager2.get_phase()}")
        print(f"  Active task: {manager2.config.active_task}")
        print(f"  Completed tasks: {len(manager2.config.completed_tasks)}")
        print()
        
        # Demo 5: Integration example
        print("📝 Demo 5: Integration Example")
        print("-" * 70)
        print("""
# Example: Phase-based development workflow

from ranex_core import WorkflowManager, ProjectPhase

manager = WorkflowManager(".")

# Check current phase
phase = manager.get_phase()

if phase == ProjectPhase.Requirements:
    print("📝 Write requirements document")
    # After requirements are done:
    manager.set_phase(ProjectPhase.Design)
    
elif phase == ProjectPhase.Design:
    print("📐 Create architecture design")
    # After design is done:
    manager.set_phase(ProjectPhase.Implementation)
    
elif phase == ProjectPhase.Implementation:
    print("💻 Write code")
    manager.set_task("Implement feature X")
    # After implementation:
    manager.complete_task()
    manager.set_phase(ProjectPhase.Review)
    
elif phase == ProjectPhase.Review:
    print("🔍 Review code")
    # After review:
    manager.set_phase(ProjectPhase.Maintenance)
""")
        print()
        
        print("=" * 70)
        print("✅ Demo Complete!")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  • Workflow enforces structured development")
        print("  • Prevents premature coding")
        print("  • Tracks tasks and progress")
        print("  • State persists across sessions")
        print()
        print("Next Steps:")
        print("  • Try examples/intent_airlock_demo.py for intent validation")
        print("  • Use with @Contract decorator")
        print("  • Integrate into development workflow")
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    demo_workflow_management()

