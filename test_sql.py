from router.clarification_loop import (
    process_query
)

from agent.graph import build_graph


# ===================================
# BUILD GRAPH
# ===================================
graph = build_graph()


# ===================================
# USER QUERY
# ===================================
query = input(
    "\nEnter Query: "
)


print("\n🚦 STEP A: Processing Query")


# ===================================
# PROCESS QUERY
# ===================================
response = process_query(query)


print("\n🚦 STEP B: Process Query Complete")


print("\n📌 Process Response:")

print(response)


# ===================================
# CLARIFICATION
# ===================================
if response["status"] == (
    "clarification_needed"
):

    print(
        "\n⚠️ Clarification Needed:"
    )

    print(
        response[
            "clarification_question"
        ]
    )


    user_response = input(
        "\nYour Response: "
    )


    query = (
        query + " " + user_response
    )


    print("\n🔄 Updated Query:")

    print(query)


# ===================================
# EXECUTE GRAPH
# ===================================
print("\n🚀 STEP C: Invoking Graph")


result = graph.invoke({

    "query": query
})


print("\n✅ STEP D: Graph Complete")


# ===================================
# OUTPUT
# ===================================
print("\n" + "=" * 60)

print("FINAL ANSWER")

print("=" * 60)

print(result.get("final_answer"))