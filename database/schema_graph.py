import os
import networkx as nx
import mysql.connector

from dotenv import load_dotenv

load_dotenv()


# ===================================
# DB CONFIG
# ===================================
DB_CONFIG = {

    "host": os.getenv("DB_HOST"),

    "user": os.getenv("DB_USER"),

    "password": os.getenv("DB_PASSWORD"),

    "database": os.getenv("DB_NAME")
}


# ===================================
# BUILD SCHEMA KNOWLEDGE GRAPH
# ===================================
def build_schema_graph():

    graph = nx.DiGraph()


    conn = mysql.connector.connect(

        **DB_CONFIG
    )

    cursor = conn.cursor(dictionary=True)


    # ===================================
    # GET TABLES
    # ===================================
    cursor.execute("""

        SELECT table_name

        FROM information_schema.tables

        WHERE table_schema = %s

    """, (DB_CONFIG["database"],))


    tables = cursor.fetchall()


    # ===================================
    # ADD TABLE NODES
    # ===================================
    for table in tables:

        table_name = table["TABLE_NAME"]


        graph.add_node(

            table_name,

            node_type="table"
        )


    # ===================================
    # GET COLUMNS
    # ===================================
    cursor.execute("""

        SELECT
            table_name,
            column_name,
            data_type

        FROM information_schema.columns

        WHERE table_schema = %s

    """, (DB_CONFIG["database"],))


    columns = cursor.fetchall()


    # ===================================
    # ADD COLUMN NODES
    # ===================================
    for col in columns:

        table_name = col["TABLE_NAME"]

        column_name = col["COLUMN_NAME"]

        data_type = col["DATA_TYPE"]


        # Unique column node name
        column_node = (
            f"{table_name}.{column_name}"
        )


        # Add column node
        graph.add_node(

            column_node,

            node_type="column",

            data_type=data_type
        )


        # TABLE → COLUMN
        graph.add_edge(

            table_name,

            column_node,

            relationship="HAS_COLUMN"
        )


    # ===================================
    # GET FOREIGN KEYS
    # ===================================
    cursor.execute("""

        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME

        FROM information_schema.KEY_COLUMN_USAGE

        WHERE
            TABLE_SCHEMA = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL

    """, (DB_CONFIG["database"],))


    foreign_keys = cursor.fetchall()


    # ===================================
    # ADD FK RELATIONSHIPS
    # ===================================
    for fk in foreign_keys:

        source_table = fk["TABLE_NAME"]

        source_column = fk["COLUMN_NAME"]

        target_table = fk[
            "REFERENCED_TABLE_NAME"
        ]

        target_column = fk[
            "REFERENCED_COLUMN_NAME"
        ]


        source_node = (
            f"{source_table}.{source_column}"
        )

        target_node = (
            f"{target_table}.{target_column}"
        )


        # COLUMN → COLUMN FK
        graph.add_edge(

            source_node,

            target_node,

            relationship="FOREIGN_KEY"
        )


    cursor.close()

    conn.close()


    return graph