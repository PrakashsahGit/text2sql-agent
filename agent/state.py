from typing import (

    TypedDict,

    List,

    Dict,

    Any,

    Optional
)


# ===================================
# AGENT STATE
# ===================================
class AgentState(TypedDict, total=False):


    # ===================================
    # USER INPUT
    # ===================================
    query: str
    resolved_query: str


    # ===================================
    # ROUTER NODE
    # ===================================
    router_output: Dict[str, Any]

    proceed_to_pipeline: bool

    clarification_needed: bool

    clarification_question: Optional[str]


    # ===================================
    # PLANNER NODE
    # ===================================
    planner_output: Dict[str, Any]


    # ===================================
    # SEMANTIC RETRIEVAL
    # ===================================
    retrieved_entities: List[
        Dict[str, Any]
    ]


    # ===================================
    # GRAPH RETRIEVAL
    # ===================================
    graph_tables: List[str]

    joins: List[str]


    # ===================================
    # SQL GENERATION
    # ===================================
    schema_context: str

    sql: str

    failed_sql: str


    # ===================================
    # SQL EXECUTION
    # ===================================
    result: List[
        Dict[str, Any]
    ]


    # ===================================
    # REASONING NODE
    # ===================================
    reasoning_output: str

    insight: str

    final_answer: str


    # ===================================
    # DEBUGGING / OBSERVABILITY
    # ===================================
    debug_logs: List[str]


    # ===================================
    # ERROR HANDLING
    # ===================================
    error: str