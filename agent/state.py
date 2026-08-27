from typing import (
    TypedDict,
    List,
    Dict,
    Any,
    Optional
)


# ===================================
# OBSERVABILITY STATE
# ===================================

class ObservabilityState(TypedDict, total=False):

    # -----------------------------------
    # REQUEST
    # -----------------------------------
    request_id: str

    started_at: str

    finished_at: str

    total_latency_ms: float

    status: str

    error: Optional[str]


    # -----------------------------------
    # NODE TRACES
    # -----------------------------------
    nodes: List[
        Dict[str, Any]
    ]


    # -----------------------------------
    # LLM CALLS
    # -----------------------------------
    llm_calls: List[
        Dict[str, Any]
    ]


    # -----------------------------------
    # LLM TOTALS
    # -----------------------------------
    total_llm_calls: int

    total_input_tokens: int

    total_output_tokens: int

    total_tokens: int


    # -----------------------------------
    # SQL OBSERVABILITY
    # -----------------------------------
    sql_generation_latency_ms: float

    sql_validation_latency_ms: float

    sql_execution_latency_ms: float

    sql_retry_count: int

    rows_returned: int


    # -----------------------------------
    # ERRORS
    # -----------------------------------
    errors: List[
        Dict[str, Any]
    ]


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

    observability: ObservabilityState


    # ===================================
    # ERROR HANDLING
    # ===================================
    error: str