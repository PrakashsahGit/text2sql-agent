from langgraph.graph import (
    StateGraph,
    END
)

from agent.state import (
    AgentState
)

from agent.nodes.retrieval_node import (
    retrieval_node
)

from agent.nodes.planner_node import (
    planner_node
)

from agent.nodes.sql_node import (
    sql_node
)

from agent.nodes.reasoning_node import (
    reasoning_node
)


# ===================================
# BUILD GRAPH
# ===================================
def build_graph():

    graph = StateGraph(
        AgentState
    )


    # ===================================
    # NODES
    # ===================================
    graph.add_node(

        "retrieval",

        retrieval_node
    )


    graph.add_node(

        "planner",

        planner_node
    )


    graph.add_node(

        "sql",

        sql_node
    )


    graph.add_node(

        "reasoning",

        reasoning_node
    )


    # ===================================
    # ENTRY POINT
    # ===================================
    graph.set_entry_point(
        "retrieval"
    )


    # ===================================
    # FLOW
    # ===================================
    graph.add_edge(
        "retrieval",
        "planner"
    )


    graph.add_edge(
        "planner",
        "sql"
    )


    graph.add_edge(
        "sql",
        "reasoning"
    )


    graph.add_edge(
        "reasoning",
        END
    )


    return graph.compile()