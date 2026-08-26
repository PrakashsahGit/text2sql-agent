from utils.llm import llm

from schemas.clarification_schema import (
    ClarificationDecision
)


# ===================================
# PROCESS QUERY
# ===================================
def process_query(
    query: str,

    clarification_response: str = None
):


    print(
        "\n🚦 STEP A: Clarification Engine"
    )


    # ===================================
    # USER ALREADY REPLIED
    # ===================================
    if clarification_response:


        resolved_query = (

            query
            + " "
            + clarification_response
        )


        print(
            "\n✅ HITL Response Received"
        )

        print(
            f"\nResolved Query:\n"
            f"{resolved_query}"
        )


        return {

            "status":
            "ready",

            "query":
            query,

            "clarification_question":
            None,

            "clarification_response":
            clarification_response,

            "resolved_query":
            resolved_query
        }


    # ===================================
    # LLM CLARIFICATION
    # ===================================
    prompt = f"""
You are the clarification engine
for an AI Analytics Copilot.

Your job:

Determine whether the user query
contains enough information
for analytical processing.


If ambiguous:

status="clarification_needed"

Ask exactly ONE
short clarification question.


If clear:

status="ready"


RULES:

Only ask clarification
when required.


Ambiguous examples:

Top products

Best customers

Highest sales

Top brands


Clear examples:

Compare Nike and Samsung sales

Revenue by region

Revenue of Nike

Top products by revenue

Average delivery time by region


USER QUERY:

{query}
"""


    structured_llm = (

        llm.with_structured_output(
            ClarificationDecision,
            method="json_schema"
        )
    )


    response = structured_llm.invoke(
        prompt
    )


    print(
        "\n📌 Clarification Decision"
    )

    print(response)


    output = response.model_dump()


    # ===================================
    # PRESERVE ORIGINAL QUERY
    # ===================================
    output["query"] = query


    output[
        "clarification_response"
    ] = None


    output[
        "resolved_query"
    ] = None


    return output