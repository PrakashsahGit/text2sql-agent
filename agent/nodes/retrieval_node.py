# from retrievers.schema_retriever import (
#     retrieve_relevant_entities
# )

# from retrievers.graph_retriever import (
#     find_join_paths
# )


# # ===================================
# # RETRIEVAL NODE
# # ===================================
# def retrieval_node(state):


#     # ===================================
#     # RESOLVED QUERY
#     # ===================================
#     query = (

#         state.get(
#             "resolved_query"
#         )

#         or

#         state["query"]
#     )


#     print(
#         "\n📚 STEP: Semantic Retrieval"
#     )


#     # ===================================
#     # SCHEMA RETRIEVAL
#     # ===================================
#     retrieved_entities = (

#         retrieve_relevant_entities(
#             query
#         )
#     )


#     print(
#         "\n📚 Retrieved Entities:\n"
#     )


#     for entity in retrieved_entities:

#         print(
#             entity[
#                 "entity"
#             ]
#         )


#     # ===================================
#     # GRAPH RETRIEVAL
#     # ===================================
#     graph_context = (

#         find_join_paths(
#             retrieved_entities
#         )
#     )


#     joins = graph_context.get(

#         "joins",

#         []
#     )


#     tables = graph_context.get(

#         "tables",

#         []
#     )


#     print(
#         "\n🔗 Graph Join Paths:\n"
#     )


#     for join in joins:

#         print(
#             join[
#                 "join_condition"
#             ]
#         )


#     # ===================================
#     # RETRIEVAL SUCCESS
#     # ===================================
#     print(
#         "\n✅ Retrieval Completed"
#     )


#     return {

#         **state,

#         "retrieved_entities":
#         retrieved_entities,

#         "joins":
#         joins,

#         "graph_tables":
#         tables
#     }



from retrievers.schema_retriever import (
    retrieve_relevant_entities
)

from retrievers.graph_retriever import (
    find_join_paths
)


# ===================================
# RETRIEVAL NODE
# ===================================
def retrieval_node(state):


    # ===================================
    # RESOLVED QUERY
    # ===================================
    query = (

        state.get(
            "resolved_query"
        )

        or

        state["query"]
    )


    print(
        "\n📚 STEP: Semantic Retrieval"
    )


    # ===================================
    # SCHEMA RETRIEVAL
    # ===================================
    retrieved_entities = (

        retrieve_relevant_entities(
            query
        )
    )


    print(
        "\n📚 Retrieved Entities:\n"
    )


    for entity in retrieved_entities:

        print(
            entity[
                "entity"
            ]
        )


    # ===================================
    # GRAPH RETRIEVAL
    # ===================================
    graph_context = (

        find_join_paths(
            retrieved_entities
        )
    )


    joins = graph_context.get(

        "joins",

        []
    )


    tables = graph_context.get(

        "tables",

        []
    )


    print(
        "\n🔗 Graph Join Paths:\n"
    )


    for join in joins:

        print(
            join[
                "join_condition"
            ]
        )


    # ===================================
    # ADD GRAPH-CONFIRMED JOIN COLUMNS
    # ===================================
    existing_entities = {

        entity["entity"]

        for entity in retrieved_entities
    }


    graph_join_entities = []


    for join in joins:


        # ===================================
        # SOURCE JOIN COLUMN
        # ===================================
        source_entity = (

            f"{join['source_table']}."
            f"{join['source_column']}"
        )


        # ===================================
        # TARGET JOIN COLUMN
        # ===================================
        target_entity = (

            f"{join['target_table']}."
            f"{join['target_column']}"
        )


        # ===================================
        # ADD SOURCE COLUMN
        # ===================================
        if source_entity not in existing_entities:

            graph_join_entities.append({

                "entity":
                source_entity,

                "table":
                join["source_table"],

                "column":
                join["source_column"],

                "type":
                "graph_confirmed_join_column",

                "text":
                (
                    f"table: "
                    f"{join['source_table']}\n\n"

                    f"column: "
                    f"{join['source_column']}\n\n"

                    f"source: graph relationship\n\n"

                    f"join confirmed:\n"
                    f"{join['join_condition']}"
                )
            })


            existing_entities.add(
                source_entity
            )


        # ===================================
        # ADD TARGET COLUMN
        # ===================================
        if target_entity not in existing_entities:

            graph_join_entities.append({

                "entity":
                target_entity,

                "table":
                join["target_table"],

                "column":
                join["target_column"],

                "type":
                "graph_confirmed_join_column",

                "text":
                (
                    f"table: "
                    f"{join['target_table']}\n\n"

                    f"column: "
                    f"{join['target_column']}\n\n"

                    f"source: graph relationship\n\n"

                    f"join confirmed:\n"
                    f"{join['join_condition']}"
                )
            })


            existing_entities.add(
                target_entity
            )


    # ===================================
    # APPEND GRAPH COLUMNS
    # ===================================
    if graph_join_entities:


        print(
            "\n🔗 Graph-Confirmed Columns:\n"
        )


        for entity in graph_join_entities:

            print(
                entity["entity"]
            )


        retrieved_entities.extend(
            graph_join_entities
        )


    # ===================================
    # RETRIEVAL SUMMARY
    # ===================================
    print(
        "\n📦 Total Retrieved Entities: "
        f"{len(retrieved_entities)}"
    )


    print(
        "\n📋 Retrieved Tables:\n"
    )


    for table in tables:

        print(
            table
        )


    # ===================================
    # RETRIEVAL SUCCESS
    # ===================================
    print(
        "\n✅ Retrieval Completed"
    )


    return {

        **state,

        "retrieved_entities":
        retrieved_entities,

        "joins":
        joins,

        "graph_tables":
        tables
    }
