from database.db import get_connection


# ===================================
# LOAD SCHEMA
# ===================================
def load_schema():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)


    # ===================================
    # LOAD COLUMNS
    # ===================================
    cursor.execute("""

        SELECT
            c.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.COLUMN_KEY

        FROM INFORMATION_SCHEMA.COLUMNS c

        WHERE c.TABLE_SCHEMA = DATABASE()

    """)

    rows = cursor.fetchall()


    schema = {}


    # ===================================
    # PROCESS COLUMNS
    # ===================================
    for row in rows:

        table_name = row["TABLE_NAME"]

        column_name = row["COLUMN_NAME"]

        data_type = row["DATA_TYPE"]

        column_key = row["COLUMN_KEY"]


        # ===================================
        # INIT TABLE
        # ===================================
        if table_name not in schema:

            schema[table_name] = {

                "columns": [],

                "relationships": []
            }


        # ===================================
        # PRIMARY KEY
        # ===================================
        is_primary_key = (

            column_key == "PRI"
        )


        # ===================================
        # SAMPLE VALUES
        # ===================================
        sample_values = []


        # Only extract for categorical/text columns
        if data_type.lower() in [

            "varchar",

            "text",

            "char",

            "enum"
        ]:

            try:

                sample_query = f"""
                    SELECT DISTINCT {column_name}
                    FROM {table_name}
                    WHERE {column_name} IS NOT NULL
                    LIMIT 5
                """

                cursor.execute(sample_query)

                samples = cursor.fetchall()


                # Convert dict rows → value list
                sample_values = [

                    str(
                        list(sample.values())[0]
                    )

                    for sample in samples
                ]


            except Exception as e:

                print(
                    f"⚠️ Failed sample extraction "
                    f"for {table_name}.{column_name}"
                )

                print(e)

                sample_values = []


        # ===================================
        # ADD COLUMN METADATA
        # ===================================
        schema[table_name]["columns"].append({

            "column": column_name,

            "type": data_type,

            "is_primary_key": is_primary_key,

            "is_foreign_key": False,

            "sample_values": sample_values
        })


    # ===================================
    # LOAD RELATIONSHIPS
    # ===================================
    cursor.execute("""

        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME

        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE

        WHERE
            REFERENCED_TABLE_NAME IS NOT NULL
            AND TABLE_SCHEMA = DATABASE()

    """)

    relationships = cursor.fetchall()


    # ===================================
    # PROCESS RELATIONSHIPS
    # ===================================
    for rel in relationships:

        table_name = rel["TABLE_NAME"]

        column_name = rel["COLUMN_NAME"]


        # ===================================
        # ADD RELATIONSHIP
        # ===================================
        schema[table_name]["relationships"].append({

            "column": column_name,

            "references_table":
            rel["REFERENCED_TABLE_NAME"],

            "references_column":
            rel["REFERENCED_COLUMN_NAME"]
        })


        # ===================================
        # MARK FOREIGN KEY
        # ===================================
        for col in schema[table_name]["columns"]:

            if col["column"] == column_name:

                col["is_foreign_key"] = True


    cursor.close()

    conn.close()


    return schema