
from langgraph.graph import StateGraph, START, END

from agents import (
    LinkedInState,
    writer_node,
    reviewer_node
)


def review_router(state: LinkedInState):

    # Stop if the reviewer approves the post.
    if state["approved"]:
        return END

    # Stop after three review attempts.
    if state["attempts"] >= 3:
        return END

    # Otherwise, send the post back to Gemini.
    return "writer"


def build_workflow():

    graph = StateGraph(LinkedInState)

    # Register workflow nodes.
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)

    # Initial flow.
    graph.add_edge(START, "writer")

    # Writer sends draft to reviewer.
    graph.add_edge("writer", "reviewer")

    # Reviewer decides whether to approve or request revision.
    graph.add_conditional_edges(
        "reviewer",
        review_router,
        {
            "writer": "writer",
            END: END
        }
    )

    return graph.compile()


# Compile workflow.
app = build_workflow()


def generate_post(topic: str):

    initial_state = {
        "topic": topic,
        "search_results": "",
        "draft": "",
        "last_draft": "",
        "feedback": "",
        "reviewer_response": "",
        "approved": False,
        "attempts": 0
    }

    result = app.invoke(initial_state)

    # Safety fallback: preserve the latest available draft.
    if not result.get("draft"):
        result["draft"] = result.get("last_draft", "")

    return result
