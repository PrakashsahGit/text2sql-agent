import streamlit as st
import pandas as pd

from agent.graph import build_graph

from query_classifier.clarification_loop import (
    process_query,
    generate_conversation_reply
)

from utils.observability import (
    create_request_observability,
    initialize_request_timer,
    finalize_request_observability,
    finalize_request_error
)

from utils.llm import (
    set_observability_context
)


# ===================================
# SESSION DEFAULTS
# ===================================

defaults = {

    "query_value": "",

    "waiting_for_clarification": False,

    "clarification_question": None,

    "resolved_query": None,

    "original_query": None,

    "agent_result": None,

    "observability": None,

    "intent": None,

    "conversation_reply": None
}


for k, v in defaults.items():

    if k not in st.session_state:

        st.session_state[k] = v


# ===================================
# PAGE CONFIG
# ===================================

st.set_page_config(

    page_title=
    "Graph-RAG Analytics Copilot",

    page_icon="📊",

    layout="wide"
)


# ===================================
# TITLE
# ===================================

st.title(
    "📊 Graph-RAG Analytics Copilot"
)


st.markdown("""
Ask business questions naturally.

Examples:

• Compare Nike and Samsung sales

• Revenue by region

• Top 5 products by profit

• Which customer segment generated highest revenue?
""")


# ===================================
# BUILD GRAPH
# ===================================

graph = build_graph()


# ===================================
# QUERY INPUT
# ===================================

query = st.text_input(

    "Ask your question",

    value=
    st.session_state[
        "query_value"
    ]
)


# ===================================
# RUN BUTTON
# ===================================

if st.button(
    "Run Analysis"
):

    if not query:

        st.warning(
            "Enter query"
        )

        st.stop()


    # ===================================
    # CLEAR STALE STATE FROM ANY
    # PREVIOUS RUN
    # ===================================

    st.session_state[
        "conversation_reply"
    ] = None


    st.session_state[
        "agent_result"
    ] = None


    # ===================================
    # SAVE ORIGINAL QUERY
    # ===================================

    st.session_state[
        "original_query"
    ] = query


    # ===================================
    # CREATE OBSERVABILITY CONTEXT
    # ===================================

    observability = (
        create_request_observability()
    )


    initialize_request_timer(
        observability
    )


    # ===================================
    # SET REQUEST-SCOPED LLM CONTEXT
    # ===================================

    set_observability_context(
        observability
    )


    # ===================================
    # SAVE OBSERVABILITY IN SESSION
    # ===================================

    st.session_state[
        "observability"
    ] = observability


    # ===================================
    # ENTRY GATE:
    # INTENT + CLARIFICATION
    # ===================================

    try:

        response = (
            process_query(
                query
            )
        )


        st.session_state[
            "intent"
        ] = response.get(
            "intent"
        )


        st.subheader(
            "🚦 Clarification Engine"
        )


        st.json(
            response
        )


        # ===================================
        # ROUTE 1:
        # ANALYTICS — CLARIFICATION NEEDED
        # ===================================

        if response[
            "status"
        ] == "clarification_needed":


            st.session_state[
                "waiting_for_clarification"
            ] = True


            st.session_state[
                "clarification_question"
            ] = (

                response[
                    "clarification_question"
                ]
            )


            # -----------------------------------
            # IMPORTANT
            #
            # Do NOT finalize observability here.
            #
            # The request is still alive because
            # we are waiting for the user's HITL
            # clarification response.
            # -----------------------------------

            st.rerun()


        # ===================================
        # ROUTE 2:
        # CONVERSATION
        #
        # NEVER TOUCH THE GRAPH
        # ===================================

        elif response[
            "intent"
        ] == "conversation":


            reply = (
                generate_conversation_reply(
                    query
                )
            )


            st.session_state[
                "conversation_reply"
            ] = reply


            # -----------------------------------
            # Conversation is a completed request.
            # Finalize observability here.
            # -----------------------------------

            observability = (
                finalize_request_observability(
                    observability,
                    status="completed"
                )
            )


            st.session_state[
                "observability"
            ] = observability


            # -----------------------------------
            # No resolved_query / analytics result
            # applies here.
            # -----------------------------------

            st.rerun()


        # ===================================
        # ROUTE 3:
        # ANALYTICS — READY
        # ===================================

        else:


            resolved = (

                response.get(
                    "resolved_query"
                )

                or

                query
            )


            st.session_state[
                "resolved_query"
            ] = resolved


            st.session_state[
                "query_value"
            ] = resolved


            # ===================================
            # GET OBSERVABILITY CONTEXT
            # ===================================

            observability = (
                st.session_state[
                    "observability"
                ]
            )


            # ===================================
            # RESTORE LLM CONTEXT
            # ===================================

            set_observability_context(
                observability
            )


            # ===================================
            # GRAPH EXECUTION
            # ===================================

            result = graph.invoke({

                "query":
                query,

                "resolved_query":
                resolved,

                "observability":
                observability
            })


            # ===================================
            # GET FINAL OBSERVABILITY
            # ===================================

            observability = (
                result.get(
                    "observability"
                )
                or
                observability
            )


            # ===================================
            # FINALIZE REQUEST
            # ===================================

            observability = (
                finalize_request_observability(
                    observability,
                    status="completed"
                )
            )


            # ===================================
            # PUT FINAL OBSERVABILITY BACK INTO
            # RESULT
            # ===================================

            result[
                "observability"
            ] = observability


            # ===================================
            # SAVE FINAL OBSERVABILITY
            # ===================================

            st.session_state[
                "observability"
            ] = observability


            st.session_state[
                "agent_result"
            ] = result


            # ===================================
            # RERUN
            # ===================================

            st.rerun()


    except Exception as e:


        # ===================================
        # FINALIZE FAILED REQUEST
        # ===================================

        observability = (
            finalize_request_error(
                observability,
                e
            )
        )


        # ===================================
        # SAVE FAILED OBSERVABILITY
        # ===================================

        st.session_state[
            "observability"
        ] = observability


        # ===================================
        # SHOW ERROR
        # ===================================

        st.error(
            "The request could not be completed."
        )


        # -----------------------------------
        # Show useful debugging information
        # while developing.
        # -----------------------------------

        with st.expander(
            "Error Details"
        ):

            st.exception(e)


# ===================================
# HITL UI
# ===================================

if st.session_state[
    "waiting_for_clarification"
]:


    clarification = st.text_input(

        st.session_state[
            "clarification_question"
        ],

        key="clarification"
    )


    if clarification:


        # ===================================
        # CAPTURE THE QUESTION BEFORE
        # WE CLEAR IT BELOW
        # ===================================

        asked_question = (

            st.session_state[
                "clarification_question"
            ]
        )


        # ===================================
        # GET EXISTING OBSERVABILITY CONTEXT
        # ===================================

        observability = (
            st.session_state[
                "observability"
            ]
        )


        # ===================================
        # RESTORE LLM CONTEXT
        # ===================================

        set_observability_context(
            observability
        )


        try:


            # ===================================
            # PROCESS CLARIFICATION RESPONSE
            # ===================================

            response = (
                process_query(

                    query=
                    st.session_state[
                        "original_query"
                    ],

                    clarification_response=
                    clarification,

                    clarification_question=
                    asked_question
                )
            )


            st.session_state[
                "intent"
            ] = response.get(
                "intent"
            )


            # ===================================
            # RESOLVED QUERY
            # ===================================

            resolved = (
                response[
                    "resolved_query"
                ]
            )


            # ===================================
            # UPDATE SEARCH BOX
            # ===================================

            st.session_state[
                "query_value"
            ] = resolved


            st.session_state[
                "resolved_query"
            ] = resolved


            # ===================================
            # CLEAR HITL STATE
            # ===================================

            st.session_state[
                "waiting_for_clarification"
            ] = False


            st.session_state[
                "clarification_question"
            ] = None


            # ===================================
            # GRAPH EXECUTION
            # ===================================

            result = graph.invoke({

                "query":
                st.session_state[
                    "original_query"
                ],

                "resolved_query":
                resolved,

                "observability":
                observability
            })


            # ===================================
            # GET FINAL OBSERVABILITY
            # ===================================

            observability = (
                result.get(
                    "observability"
                )
                or
                observability
            )


            # ===================================
            # FINALIZE REQUEST
            # ===================================

            observability = (
                finalize_request_observability(
                    observability,
                    status="completed"
                )
            )


            # ===================================
            # PUT FINAL OBSERVABILITY INTO RESULT
            # ===================================

            result[
                "observability"
            ] = observability


            # ===================================
            # SAVE FINAL OBSERVABILITY
            # ===================================

            st.session_state[
                "observability"
            ] = observability


            # ===================================
            # SAVE RESULT
            # ===================================

            st.session_state[
                "agent_result"
            ] = result


            # ===================================
            # RERUN
            # ===================================

            st.rerun()


        except Exception as e:


            # ===================================
            # FINALIZE FAILED HITL REQUEST
            # ===================================

            observability = (
                finalize_request_error(
                    observability,
                    e
                )
            )


            st.session_state[
                "observability"
            ] = observability


            st.error(
                "The request could not be completed."
            )


            with st.expander(
                "Error Details"
            ):

                st.exception(e)


# ===================================
# CONVERSATION REPLY UI
# ===================================

if st.session_state[
    "conversation_reply"
]:


    st.subheader(
        "💬 Copilot"
    )


    st.info(
        st.session_state[
            "conversation_reply"
        ]
    )


# ===================================
# GET RESULT
# ===================================

result = (
    st.session_state[
        "agent_result"
    ]
)


# ===================================
# OBSERVABILITY
# ===================================

if result:


    observability = result.get(
        "observability"
    )


    if observability:


        st.subheader(
            "📊 LLM Observability"
        )


        # ===================================
        # SUMMARY METRICS
        # ===================================

        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(

                "LLM Calls",

                observability.get(
                    "total_llm_calls",
                    0
                )
            )


        with c2:

            st.metric(

                "Input Tokens",

                observability.get(
                    "total_input_tokens",
                    0
                )
            )


        with c3:

            st.metric(

                "Output Tokens",

                observability.get(
                    "total_output_tokens",
                    0
                )
            )


        with c4:

            st.metric(

                "Total Tokens",

                observability.get(
                    "total_tokens",
                    0
                )
            )


        # ===================================
        # REQUEST INFORMATION
        # ===================================

        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(

                "Request ID",

                observability.get(
                    "request_id",
                    "N/A"
                )
            )


        with c2:

            st.metric(

                "Status",

                observability.get(
                    "status",
                    "N/A"
                )
            )


        with c3:

            st.metric(

                "Latency",

                f"{observability.get(
                    'total_latency_ms',
                    0
                )} ms"
            )


        # ===================================
        # REQUEST TIMESTAMPS
        # ===================================

        with st.expander(
            "Request Timing",
            expanded=False
        ):

            st.json({

                "started_at":
                observability.get(
                    "started_at"
                ),

                "finished_at":
                observability.get(
                    "finished_at"
                ),

                "total_latency_ms":
                observability.get(
                    "total_latency_ms",
                    0
                ),

                "status":
                observability.get(
                    "status"
                )
            })


        # ===================================
        # LLM CALL DETAILS
        # ===================================

        with st.expander(

            "LLM Call Details",

            expanded=True
        ):


            llm_calls = (
                observability.get(
                    "llm_calls",
                    []
                )
            )


            if llm_calls:


                for i, call in enumerate(
                    llm_calls
                ):


                    st.markdown(
                        f"### LLM Call {i + 1}"
                    )


                    st.json(
                        call
                    )


            else:

                st.info(
                    "No LLM calls recorded."
                )


        # ===================================
        # OBSERVABILITY ERRORS
        # ===================================

        errors = (
            observability.get(
                "errors",
                []
            )
        )


        if errors:

            with st.expander(

                "Observability Errors",

                expanded=True
            ):

                st.json(
                    errors
                )


# ===================================
# SHOW RESULTS
# ===================================

if result:


    # ===================================
    # QUERY RESOLUTION
    # ===================================

    st.subheader(
        "🧾 Query Resolution"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "### Original Query"
        )


        st.code(
            st.session_state[
                "original_query"
            ]
        )


    with c2:

        st.markdown(
            "### Final Query"
        )


        st.code(
            st.session_state[
                "resolved_query"
            ]
        )


    # ===================================
    # RETRIEVAL
    # ===================================

    entities = result.get(
        "retrieved_entities",
        []
    )


    st.subheader(
        "📚 Retrieval Node"
    )


    st.metric(

        "Retrieved Columns",

        len(entities)
    )


    with st.expander(

        "Retrieved Schema",

        expanded=False
    ):


        for e in entities:


            st.markdown(
                f"### {e['entity']}"
            )


            st.code(
                e["text"]
            )


    # ===================================
    # GRAPH
    # ===================================

    st.subheader(
        "🔗 Graph Retrieval"
    )


    tables = result.get(
        "graph_tables",
        []
    )


    joins = result.get(
        "joins",
        []
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "### Connected Tables"
        )


        st.json(
            tables
        )


    with c2:

        st.metric(

            "Relationships",

            len(joins)
        )


    with st.expander(

        "Join Paths",

        expanded=True
    ):


        for join in joins:


            st.code(
                join[
                    "join_condition"
                ]
            )


            st.caption(

                f"{join['source_table']}."
                f"{join['source_column']}"
                f" → "
                f"{join['target_table']}."
                f"{join['target_column']}"
                f" ({join['relationship_type']})"
            )


    # ===================================
    # PLANNER
    # ===================================

    planner = result.get(
        "planner_output"
    )


    if planner:


        st.subheader(
            "🧠 Planner Output"
        )


        st.json(
            planner
        )


    # ===================================
    # SQL
    # ===================================

    sql = result.get(
        "sql"
    )


    if sql:


        st.subheader(
            "🧠 Generated SQL"
        )


        st.code(
            sql,
            language="sql"
        )


    # ===================================
    # TRACE
    # ===================================

    logs = result.get(
        "debug_logs",
        []
    )


    if logs:


        st.subheader(
            "🛠 Execution Trace"
        )


        for i, log in enumerate(
            logs
        ):


            with st.expander(
                f"Step {i + 1}"
            ):


                st.code(
                    log
                )


    # ===================================
    # RESULTS
    # ===================================

    rows = result.get(
        "result"
    )


    if rows:


        st.subheader(
            "📋 SQL Results"
        )


        st.dataframe(

            pd.DataFrame(
                rows
            ),

            width="stretch"
        )


    # ===================================
    # ANSWER
    # ===================================

    answer = result.get(
        "final_answer"
    )


    if answer:


        st.subheader(
            "✅ Final Answer"
        )


        st.markdown(
            answer
        )


    # ===================================
    # ERROR
    # ===================================

    error = result.get(
        "error"
    )


    if error:


        st.subheader(
            "❌ Error"
        )


        st.error(
            error
        )