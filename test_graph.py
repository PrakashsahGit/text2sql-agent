from planner.clarification_loop import (
    clarification_loop
)


query = input(
    "\nEnter Query: "
)


final_query = clarification_loop(
    query
)


print("\n" + "=" * 60)

print("FINAL QUERY")

print("=" * 60)

print(final_query)