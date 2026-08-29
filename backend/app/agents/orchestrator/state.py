from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import add_messages
from typing_extensions import Annotated

class OrcaState(TypedDict):
    """The central state object for the ORCA Orchestrator."""
    session_id: str
    user_query: str
    
    # Intent extraction
    intent: Optional[str]
    location: Optional[str]
    time_range: Optional[str]
    
    # Planning
    plan: List[Dict[str, Any]]
    required_agents: List[str]
    
    # Execution State
    agent_results: Dict[str, Any]
    errors: List[str]
    replan_count: int
    
    # Final Response
    final_response: Optional[str]
    
    # Message history (optional, for streaming or conversation)
    messages: Annotated[list, add_messages]
