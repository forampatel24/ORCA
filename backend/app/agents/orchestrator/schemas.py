from pydantic import BaseModel, Field
from typing import List, Optional

class IntentInterpretation(BaseModel):
    """Interpreted intent from the user query."""
    intent: str = Field(description="The primary intent of the user (e.g., 'check_safety', 'find_pfz', 'weather_forecast', 'general_knowledge')")
    location: Optional[str] = Field(description="The specific location mentioned, if any")
    time_range: Optional[str] = Field(description="The time or date mentioned, if any")
    
class AgentTask(BaseModel):
    """A specific task assigned to an agent."""
    agent_name: str = Field(description="The name of the agent (e.g., 'weather_agent', 'marine_agent', 'risk_agent', 'rag_agent')")
    task_description: str = Field(description="Detailed instructions of what the agent needs to do")
    dependencies: List[str] = Field(default_factory=list, description="List of agent_names that must complete before this task")

class TaskPlan(BaseModel):
    """The complete execution plan."""
    tasks: List[AgentTask] = Field(description="The list of tasks to execute")
