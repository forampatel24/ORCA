import asyncio
import os
import json
from app.agents.orchestrator.graph import orchestrator_app

async def test_graph():
    initial_state = {
        "session_id": "test-session-123",
        "user_query": "Is it safe to fish tomorrow near Ratnagiri?",
    }
    
    print("Running orchestrator graph...")
    final_state = await orchestrator_app.ainvoke(initial_state)
    
    print("\n--- FINAL STATE ---")
    print(f"Intent: {final_state.get('intent')}")
    print(f"Location: {final_state.get('location')}")
    print(f"Time Range: {final_state.get('time_range')}")
    print(f"\nPlan Tasks:")
    for task in final_state.get('plan', []):
        print(f" - [{task['agent_name']}] {task['task_description']} (deps: {task['dependencies']})")
        
    print(f"\nAgent Results:\n{json.dumps(final_state.get('agent_results'), indent=2)}")
    print(f"\nFinal Response:\n{final_state.get('final_response')}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Ensure OpenAI key is available, else it will fail
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping real test: OPENAI_API_KEY is not set.")
    else:
        asyncio.run(test_graph())
