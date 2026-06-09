from pydantic import BaseModel
from typing import Optional, List, Annotated
from langgraph.graph.message import add_messages


class LeadInfo(BaseModel):
    name: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[str] = None
    phone: Optional[str] = None


class AgentState(BaseModel):
    messages: Annotated[list, add_messages] = []
    session_id: str = ""
    retrieved_docs: List[str] = []
    retry_count: int = 0

    answer: str = ""
    intent: str = ""
    lead_info: Optional[LeadInfo] = None
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True