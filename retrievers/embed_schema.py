from database.schema_loader import (
    load_schema
)


# ===================================
# SCHEMA → ENTITY DOCUMENTS
# ===================================
def schema_to_documents():

    schema = load_schema()

    documents = []


    # ===================================
    # LOOP TABLES
    # ===================================
    for table_name, table_data in (

        schema.items()
    ):


        # ===================================
        # LOOP COLUMNS
        # ===================================
        for column_data in (

            table_data["columns"]
        ):

            column_name = (
                column_data["column"]
            )

            data_type = (
                column_data["type"]
            )

            sample_values = (
                column_data[
                    "sample_values"
                ]
            )

            is_primary_key = (
                column_data[
                    "is_primary_key"
                ]
            )

            is_foreign_key = (
                column_data[
                    "is_foreign_key"
                ]
            )


            # ===================================
            # SAMPLE VALUE TEXT
            # ===================================
            sample_text = ""

            if sample_values:

                sample_text = (
                    "\n".join(sample_values)
                )


            # ===================================
            # SEMANTIC DOCUMENT
            # ===================================
            text = f"""
table: {table_name}

column: {column_name}

type: {data_type}

primary key: {is_primary_key}

foreign key: {is_foreign_key}

sample values:
{sample_text}
"""


            # ===================================
            # DOCUMENT
            # ===================================
            documents.append({

                "entity":
                f"{table_name}.{column_name}",

                "table": table_name,

                "column": column_name,

                "type": data_type,

                "text": text.strip()
            })


    return documents