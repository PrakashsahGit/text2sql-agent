import streamlit as st
import pandas as pd

from agent.graph import build_graph

from query_classifier.clarification_loop import (
    process_query
)


# ===================================
# SESSION DEFAULTS
# ===================================
defaults = {

    "query_value":"",

    "waiting_for_clarification":False,

    "clarification_question":None,

    "resolved_query":None,

    "original_query":None,

    "agent_result":None
}


for k,v in defaults.items():

    if k not in st.session_state:

        st.session_state[k]=v


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

    value=st.session_state[
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
    # SAVE ORIGINAL
    # ===================================
    st.session_state[
        "original_query"
    ] = query


    # ===================================
    # CLARIFICATION
    # ===================================
    response=(

        process_query(
            query
        )
    )


    st.subheader(
        "🚦 Clarification Engine"
    )

    st.json(
        response
    )


    # ===================================
    # HITL REQUIRED
    # ===================================
    if response[
        "status"
    ]=="clarification_needed":


        st.session_state[
            "waiting_for_clarification"
        ]=True


        st.session_state[
            "clarification_question"
        ]=(

            response[
                "clarification_question"
            ]
        )


        st.rerun()


    # ===================================
    # DIRECT QUERY
    # ===================================
    else:


        resolved=(

            response.get(
                "resolved_query"
            )

            or

            query
        )


        st.session_state[
            "resolved_query"
        ]=resolved


        st.session_state[
            "query_value"
        ]=resolved


        result=graph.invoke({

            "query":
            query,

            "resolved_query":
            resolved
        })


        st.session_state[
            "agent_result"
        ]=result


        st.rerun()


# ===================================
# HITL UI
# ===================================
if st.session_state[
    "waiting_for_clarification"
]:


    clarification=st.text_input(

        st.session_state[
            "clarification_question"
        ],

        key="clarification"
    )


    if clarification:


        response=(

            process_query(

                query=st.session_state[
                    "original_query"
                ],

                clarification_response=
                clarification
            )
        )


        resolved=(

            response[
                "resolved_query"
            ]
        )


        # ===================================
        # UPDATE SEARCH BOX
        # ===================================
        st.session_state[
            "query_value"
        ]=resolved


        st.session_state[
            "resolved_query"
        ]=resolved


        st.session_state[
            "waiting_for_clarification"
        ]=False


        result=graph.invoke({

            "query":
            st.session_state[
                "original_query"
            ],

            "resolved_query":
            resolved
        })


        st.session_state[
            "agent_result"
        ]=result


        st.rerun()


# ===================================
# SHOW RESULTS
# ===================================
result=(

    st.session_state[
        "agent_result"
    ]
)


if result:


    st.subheader(
        "🧾 Query Resolution"
    )


    c1,c2=st.columns(2)


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
    entities=result.get(

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


    tables=result.get(

        "graph_tables",

        []
    )


    joins=result.get(

        "joins",

        []
    )


    c1,c2=st.columns(2)


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
    planner=result.get(
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
    sql=result.get(
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
    logs=result.get(
        "debug_logs",
        []
    )


    if logs:

        st.subheader(
            "🛠 Execution Trace"
        )


        for i,log in enumerate(
            logs
        ):


            with st.expander(

                f"Step {i+1}"
            ):


                st.code(
                    log
                )


    # ===================================
    # RESULTS
    # ===================================
    rows=result.get(
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
    answer=result.get(
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
    error=result.get(
        "error"
    )


    if error:

        st.subheader(
            "❌ Error"
        )

        st.error(
            error
        )