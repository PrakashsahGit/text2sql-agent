# from agent.state import AgentState

# from tools.analyzer import analyze_data


# # ===================================
# # REASONING NODE
# # ===================================
# def reasoning_node(state: AgentState) -> AgentState:


#     # ===================================
#     # Handle Non-SQL Responses
#     # ===================================
#     if state.get("final_answer"):

#         return state


#     query = state.get("resolved_query") or state["query"]

#     result = state.get("result", [])


#     # ===================================
#     # Handle Empty Results
#     # ===================================
#     if not result:

#         return {

#             **state,

#             "final_answer":
#             (
#                 "Query executed successfully "
#                 "but no matching data was found."
#             )
#         }


#     # ===================================
#     # Limit Large Results
#     # ===================================
#     limited_result = result[:10]


#     # ===================================
#     # Generate AI Insights
#     # ===================================
#     insight = analyze_data(

#         query,

#         limited_result
#     )


#     # ===================================
#     # Return Final State
#     # ===================================
#     return {

#         **state,

#         "final_answer": insight
#     }



from agent.state import AgentState

from tools.analyzer import analyze_data


# ===================================
# REASONING NODE
# ===================================
def reasoning_node(
    state: AgentState
) -> AgentState:


    # ===================================
    # HANDLE EXISTING FINAL ANSWER
    # ===================================
    if state.get("final_answer"):

        return state


    # ===================================
    # QUERY
    # ===================================
    query = (

        state.get(
            "resolved_query"
        )

        or

        state["query"]
    )


    # ===================================
    # RESULT
    # ===================================
    result = state.get(
        "result",
        []
    )


    # ===================================
    # DATABASE ERROR
    # ===================================
    error = state.get(
        "error"
    )


    if error:

        return {

            **state,

            "final_answer":
            (
                "The database query could "
                "not be completed.\n\n"
                f"Error: {error}"
            )
        }


    # ===================================
    # EMPTY RESULT
    # ===================================
    if not result:

        return {

            **state,

            "final_answer":
            (
                "The query executed successfully "
                "but no matching data was found."
            )
        }


    # ===================================
    # HANDLE NULL AGGREGATION
    # ===================================
    if len(result) == 1:

        row = result[0]


        # -----------------------------------
        # Check if all returned values
        # are NULL
        # -----------------------------------
        if row and all(

            value is None

            for value in row.values()

        ):

            columns = ", ".join(
                row.keys()
            )


            return {

                **state,

                "final_answer":
                (
                    "The query executed successfully, "
                    "but no data was found for the "
                    "specified filter.\n\n"

                    f"Returned columns: {columns}"
                )
            }


    # ===================================
    # PRESERVE NULL VALUES
    # ===================================
    normalized_result = [

        dict(row)

        for row in result
    ]


    # ===================================
    # LIMIT LARGE RESULTS
    # ===================================
    limited_result = (

        normalized_result[:10]
    )


    # ===================================
    # GENERATE AI INSIGHTS
    # ===================================
    insight = analyze_data(

        query,

        limited_result
    )


    # ===================================
    # RETURN FINAL STATE
    # ===================================
    return {

        **state,

        "final_answer":
        insight
    }