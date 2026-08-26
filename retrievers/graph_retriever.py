# import networkx as nx

# from database.schema_graph import (
#     build_schema_graph
# )


# # ===================================
# # BUILD GRAPH
# # ===================================
# graph = build_schema_graph()


# # ===================================
# # EXTRACT TABLE NAME
# # ===================================
# def get_table_name(
#     column_node: str
# ):

#     return column_node.split(".")[0]


# # ===================================
# # EXTRACT COLUMN NAME
# # ===================================
# def get_column_name(
#     column_node: str
# ):

#     return column_node.split(".")[1]


# # ===================================
# # FIND JOIN PATHS
# # ===================================
# def find_join_paths(
#     retrieved_entities
# ):

#     joins = []

#     tables = set()


#     # ===================================
#     # EXTRACT TABLES
#     # ===================================
#     for entity in retrieved_entities:

#         column_node = entity["entity"]

#         table_name = get_table_name(
#             column_node
#         )

#         tables.add(table_name)


#     tables = list(tables)


#     # ===================================
#     # FIND FK PATHS
#     # ===================================
#     for source_table in tables:

#         for target_table in tables:


#             # ===============================
#             # SKIP SAME TABLE
#             # ===============================
#             if source_table == target_table:

#                 continue


#             # ===============================
#             # SOURCE TABLE COLUMNS
#             # ===============================
#             source_columns = [

#                 node

#                 for node in graph.nodes

#                 if (
#                     isinstance(node, str)
#                     and
#                     node.startswith(
#                         f"{source_table}."
#                     )
#                 )
#             ]


#             # ===============================
#             # TARGET TABLE COLUMNS
#             # ===============================
#             target_columns = [

#                 node

#                 for node in graph.nodes

#                 if (
#                     isinstance(node, str)
#                     and
#                     node.startswith(
#                         f"{target_table}."
#                     )
#                 )
#             ]


#             # ===================================
#             # SEARCH FK RELATIONSHIPS
#             # ===================================
#             for source_col in source_columns:

#                 for target_col in target_columns:


#                     # ===============================
#                     # FK EDGE EXISTS
#                     # ===============================
#                     if graph.has_edge(

#                         source_col,

#                         target_col
#                     ):


#                         edge_data = graph.get_edge_data(

#                             source_col,

#                             target_col
#                         )


#                         # ===============================
#                         # VALID FK RELATIONSHIP
#                         # ===============================
#                         if edge_data.get(
#                             "relationship"
#                         ) == "FOREIGN_KEY":


#                             source_column_name = (
#                                 get_column_name(
#                                     source_col
#                                 )
#                             )

#                             target_column_name = (
#                                 get_column_name(
#                                     target_col
#                                 )
#                             )


#                             # ===============================
#                             # STRUCTURED JOIN METADATA
#                             # ===============================
#                             join_metadata = {

#                                 # =======================
#                                 # SOURCE
#                                 # =======================
#                                 "source_table":
#                                 source_table,

#                                 "source_column":
#                                 source_column_name,

#                                 "source_node":
#                                 source_col,

#                                 "source_is_fk":
#                                 True,


#                                 # =======================
#                                 # TARGET
#                                 # =======================
#                                 "target_table":
#                                 target_table,

#                                 "target_column":
#                                 target_column_name,

#                                 "target_node":
#                                 target_col,

#                                 "target_is_pk":
#                                 True,


#                                 # =======================
#                                 # RELATIONSHIP
#                                 # =======================
#                                 "relationship":
#                                 "FOREIGN_KEY",

#                                 "relationship_type":
#                                 "many-to-one",


#                                 # =======================
#                                 # SQL JOIN
#                                 # =======================
#                                 "join_condition":
#                                 (
#                                     f"{source_col} = "
#                                     f"{target_col}"
#                                 )
#                             }


#                             # ===============================
#                             # AVOID DUPLICATES
#                             # ===============================
#                             existing_conditions = [

#                                 join[
#                                     "join_condition"
#                                 ]

#                                 for join in joins
#                             ]


#                             if (
#                                 join_metadata[
#                                     "join_condition"
#                                 ]

#                                 not in existing_conditions
#                             ):

#                                 joins.append(
#                                     join_metadata
#                                 )


#     # ===================================
#     # CONNECTIVITY CHECK
#     # ===================================
#     joinable = len(joins) > 0


#     # ===================================
#     # RETURN GRAPH CONTEXT
#     # ===================================
#     return {

#         "tables": tables,

#         "joins": joins,

#         "joinable": joinable
#     }


import networkx as nx

from database.schema_graph import (
    build_schema_graph
)


# ===================================
# BUILD GRAPH
# ===================================
graph = build_schema_graph()


# ===================================
# EXTRACT TABLE NAME
# ===================================
def get_table_name(
    column_node: str
):

    return column_node.split(".")[0]


# ===================================
# EXTRACT COLUMN NAME
# ===================================
def get_column_name(
    column_node: str
):

    return column_node.split(".")[1]


# ===================================
# FIND JOIN PATHS
# ===================================
def find_join_paths(
    retrieved_entities
):

    joins = []

    tables = set()


    # ===================================
    # EXTRACT TABLES
    # ===================================
    for entity in retrieved_entities:

        column_node = entity["entity"]

        table_name = get_table_name(
            column_node
        )

        tables.add(
            table_name
        )


    tables = list(tables)


    # ===================================
    # FIND FK PATHS
    # ===================================
    for source_table in tables:

        for target_table in tables:


            # ===============================
            # SKIP SAME TABLE
            # ===============================
            if source_table == target_table:

                continue


            # ===============================
            # SOURCE TABLE COLUMNS
            # ===============================
            source_columns = [

                node

                for node in graph.nodes

                if (
                    isinstance(node, str)
                    and
                    node.startswith(
                        f"{source_table}."
                    )
                )
            ]


            # ===============================
            # TARGET TABLE COLUMNS
            # ===============================
            target_columns = [

                node

                for node in graph.nodes

                if (
                    isinstance(node, str)
                    and
                    node.startswith(
                        f"{target_table}."
                    )
                )
            ]


            # ===================================
            # SEARCH FK RELATIONSHIPS
            # ===================================
            for source_col in source_columns:

                for target_col in target_columns:


                    # ===============================
                    # FK EDGE EXISTS
                    # ===============================
                    if graph.has_edge(

                        source_col,

                        target_col
                    ):


                        edge_data = graph.get_edge_data(

                            source_col,

                            target_col
                        )


                        # ===============================
                        # VALID FK RELATIONSHIP
                        # ===============================
                        if edge_data.get(
                            "relationship"
                        ) == "FOREIGN_KEY":


                            source_column_name = (
                                get_column_name(
                                    source_col
                                )
                            )

                            target_column_name = (
                                get_column_name(
                                    target_col
                                )
                            )


                            # ===============================
                            # STRUCTURED JOIN METADATA
                            # ===============================
                            join_metadata = {

                                # =======================
                                # SOURCE
                                # =======================
                                "source_table":
                                source_table,

                                "source_column":
                                source_column_name,

                                "source_node":
                                source_col,

                                "source_is_fk":
                                True,


                                # =======================
                                # TARGET
                                # =======================
                                "target_table":
                                target_table,

                                "target_column":
                                target_column_name,

                                "target_node":
                                target_col,

                                "target_is_pk":
                                True,


                                # =======================
                                # RELATIONSHIP
                                # =======================
                                "relationship":
                                "FOREIGN_KEY",

                                "relationship_type":
                                "many-to-one",


                                # =======================
                                # SQL JOIN
                                # =======================
                                "join_condition":
                                (
                                    f"{source_col} = "
                                    f"{target_col}"
                                )
                            }


                            # ===============================
                            # AVOID DUPLICATES
                            # ===============================
                            existing_conditions = [

                                join[
                                    "join_condition"
                                ]

                                for join in joins
                            ]


                            if (
                                join_metadata[
                                    "join_condition"
                                ]

                                not in existing_conditions
                            ):

                                joins.append(
                                    join_metadata
                                )


    # ===================================
    # CONNECTIVITY CHECK
    # ===================================
    joinable = len(joins) > 0


    # ===================================
    # RETURN GRAPH CONTEXT
    # ===================================
    return {

        "tables": tables,

        "joins": joins,

        "joinable": joinable
    }