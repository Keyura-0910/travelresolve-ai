"""
LangGraph stateful workflow construction for TravelResolve AI.
Assembles the complete DAG with conditional routing, checkpoints, and thread resumability.
"""

from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import TicketWorkflowState
from app.agents.nodes import (
    node_intake_classification,
    node_booking_investigation,
    node_knowledge_retrieval,
    node_resolution_drafting,
    node_resolution_auditor,
    node_routing_decision,
    node_human_review,
    node_finalization
)


def route_after_decision(state: TicketWorkflowState) -> str:
    """Conditional router: directs uncertain/sensitive cases to human review, otherwise finalizes."""
    if state.get("needs_human_review"):
        return "human_review"
    return "finalization"


def build_workflow_graph():
    """Builds and compiles the full LangGraph ticket resolution workflow."""
    workflow = StateGraph(TicketWorkflowState)

    # Add all 8 specialized workflow nodes
    workflow.add_node("intake_classification", node_intake_classification)
    workflow.add_node("booking_investigation", node_booking_investigation)
    workflow.add_node("knowledge_retrieval", node_knowledge_retrieval)
    workflow.add_node("resolution_drafting", node_resolution_drafting)
    workflow.add_node("resolution_auditor", node_resolution_auditor)
    workflow.add_node("routing_decision", node_routing_decision)
    workflow.add_node("human_review", node_human_review)
    workflow.add_node("finalization", node_finalization)

    # Establish linear workflow progression
    workflow.add_edge(START, "intake_classification")
    workflow.add_edge("intake_classification", "booking_investigation")
    workflow.add_edge("booking_investigation", "knowledge_retrieval")
    workflow.add_edge("knowledge_retrieval", "resolution_drafting")
    workflow.add_edge("resolution_drafting", "resolution_auditor")
    workflow.add_edge("resolution_auditor", "routing_decision")

    # Conditional routing based on auditor and safety checks
    workflow.add_conditional_edges(
        "routing_decision",
        route_after_decision,
        {
            "human_review": "human_review",
            "finalization": "finalization"
        }
    )

    workflow.add_edge("human_review", "finalization")
    workflow.add_edge("finalization", END)

    checkpointer = MemorySaver()
    compiled_app = workflow.compile(checkpointer=checkpointer)
    return compiled_app


# Singleton compiled graph instance
compiled_workflow = build_workflow_graph()


def run_ticket_workflow(
    initial_state: TicketWorkflowState,
    thread_id: Optional[str] = None
) -> TicketWorkflowState:
    """
    Executes the ticket workflow through LangGraph.
    
    Args:
        initial_state: Dict matching TicketWorkflowState
        thread_id: Resumable thread identifier (defaults to ticket_id)
        
    Returns:
        Final updated state dictionary.
    """
    t_id = thread_id or initial_state.get("ticket_id", "default_thread")
    config = {"configurable": {"thread_id": t_id}}

    result = compiled_workflow.invoke(initial_state, config=config)
    return result


def resume_ticket_workflow(
    thread_id: str,
    human_decision: str,
    reviewer_name: str = "Support Supervisor",
    reviewer_notes: str = ""
) -> TicketWorkflowState:
    """
    Resumes a workflow thread previously paused for human review.
    Updates the state with human decision and executes finalization.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Retrieve existing state
    current_state = compiled_workflow.get_state(config).values
    if not current_state:
        raise ValueError(f"No active workflow found for thread ID: {thread_id}")

    # Inject human review findings
    updated_state = dict(current_state)
    updated_state["human_approval_status"] = human_decision
    updated_state["human_reviewer"] = reviewer_name
    updated_state["reviewer_notes"] = reviewer_notes

    # Execute human_review and finalization
    updated_state = node_human_review(updated_state)
    updated_state = node_finalization(updated_state)

    # Save to checkpointer
    compiled_workflow.update_state(config, updated_state)
    return updated_state
