# from agent.state import AgentState

# from tools.sql_generator import (
#     generate_sql,
#     fix_sql
# )

# from tools.sql_executor import (
#     execute_sql
# )

# from tools.sql_validator import (
#     validate_sql
# )

# from tools.query_classifier import (
#     is_sql_query
# )


# # ===================================
# # SQL NODE
# # ===================================
# def sql_node(
#     state: AgentState
# ) -> AgentState:


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


#     # ===================================
#     # DEBUG LOGS
#     # ===================================
#     debug_logs = []


#     # ===================================
#     # PLANNER OUTPUT
#     # ===================================
#     planner_output = state.get(

#         "planner_output",

#         {}
#     )


#     # ===================================
#     # RETRIEVED CONTEXT
#     # ===================================
#     retrieved_entities = state.get(

#         "retrieved_entities",

#         []
#     )


#     joins = state.get(

#         "joins",

#         []
#     )


#     tables = state.get(

#         "graph_tables",

#         []
#     )


#     # ===================================
#     # PRINT PLANNER OUTPUT
#     # ===================================
#     print(
#         "\n🧠 Planner Output:\n"
#     )

#     print(
#         planner_output
#     )


#     debug_logs.append(

#         f"Planner Output:\n"
#         f"{planner_output}"
#     )


#     # ===================================
#     # QUERY CLASSIFICATION
#     # ===================================
#     if not is_sql_query(query):


#         return {

#             **state,

#             "sql": None,

#             "result": [],

#             "final_answer":
#             (
#                 "This question does not "
#                 "require database analysis."
#             )
#         }


#     # ===================================
#     # PRINT RETRIEVED ENTITIES
#     # ===================================
#     print(
#         "\n📚 Retrieved Entities:\n"
#     )


#     for entity in retrieved_entities:


#         print(
#             entity["text"]
#         )

#         print(
#             "-" * 50
#         )


#         debug_logs.append(

#             f"Retrieved Entity:\n"
#             f"{entity['text']}"
#         )


#     # ===================================
#     # PRINT GRAPH RELATIONSHIPS
#     # ===================================
#     print(
#         "\n🔗 Graph Join Paths:\n"
#     )


#     for join in joins:


#         print(
#             join["join_condition"]
#         )


#         debug_logs.append(

#             f"Join:\n"
#             f"{join['join_condition']}"
#         )


#     # ===================================
#     # BUILD SCHEMA CONTEXT
#     # ===================================
#     schema_context = "\n\n".join([

#         entity["text"]

#         for entity in retrieved_entities
#     ])


#     # ===================================
#     # BUILD JOIN CONTEXT
#     # ===================================
#     join_context = "\n\n".join([

#         (

#             f"Join Condition:\n"
#             f"{join['join_condition']}\n\n"

#             f"Relationship:\n"
#             f"{join['relationship_type']}\n\n"

#             f"Foreign Key:\n"
#             f"{join['source_table']}."
#             f"{join['source_column']}\n\n"

#             f"Primary Key:\n"
#             f"{join['target_table']}."
#             f"{join['target_column']}"
#         )

#         for join in joins
#     ])


#     # ===================================
#     # PLANNER CONTEXT
#     # ===================================
#     planner_context = f"""

# PLANNER OUTPUT:

# Intent:
# {planner_output.get("intent")}


# Metrics:
# {planner_output.get("metrics")}


# Metric Types:
# {planner_output.get("metric_types")}


# Dimensions:
# {planner_output.get("dimensions")}


# Filters:
# {planner_output.get("filters")}


# Time Context:
# {planner_output.get("time_context")}


# Requires Grouping:
# {planner_output.get("requires_grouping")}


# Requires Aggregation:
# {planner_output.get("requires_aggregation")}
# """


#     # ===================================
#     # FINAL CONTEXT
#     # ===================================
#     full_context = f"""

# {planner_context}


# SCHEMA:

# {schema_context}


# VALID TABLES:

# {tables}


# VALID RELATIONSHIPS:

# {join_context}
# """


#     debug_logs.append(

#         f"Full Context:\n"
#         f"{full_context}"
#     )


#     # ===================================
#     # PRINT AUTHORITATIVE METRICS
#     # ===================================
#     print(
#         "\n📊 Authoritative Planner Metrics:\n"
#     )

#     print(
#         planner_output.get(
#             "metrics",
#             []
#         )
#     )


#     print(
#         "\n📊 Authoritative Metric Types:\n"
#     )

#     print(
#         planner_output.get(
#             "metric_types",
#             {}
#         )
#     )


#     debug_logs.append(

#         "Authoritative Planner Metrics:\n"
#         f"{planner_output.get('metrics', [])}"
#     )

#     debug_logs.append(

#         "Authoritative Metric Types:\n"
#         f"{planner_output.get('metric_types', {})}"
#     )


#     # ===================================
#     # SQL GENERATION
#     # ===================================
#     sql = generate_sql(

#         query=query,

#         schema=full_context,

#         planner_output=planner_output
#     )


#     # ===================================
#     # CLEAN GENERATED SQL
#     # ===================================
#     sql = (

#         sql

#         .replace(
#             "```sql",
#             ""
#         )

#         .replace(
#             "```",
#             ""
#         )

#         .strip()
#     )


#     # ===================================
#     # PRINT GENERATED SQL
#     # ===================================
#     print(
#         "\n🧠 Generated SQL:\n"
#     )

#     print(
#         sql
#     )


#     debug_logs.append(

#         f"Generated SQL:\n"
#         f"{sql}"
#     )


#     # ===================================
#     # RETRY CONFIGURATION
#     # ===================================
#     max_retries = 5

#     retries = 0

#     error = None


#     # ===================================
#     # RETRY LOOP
#     # ===================================
#     while retries < max_retries:


#         attempt = retries + 1


#         print(

#             f"\n🚀 SQL Attempt "
#             f"{attempt}"
#         )


#         # ===================================
#         # SQL VALIDATION
#         # ===================================
#         print(
#             "\n🔎 SQL Validation:\n"
#         )


#         is_valid, validation_result = (

#             validate_sql(
#                 sql
#             )
#         )


#         # ===================================
#         # VALIDATION FAILURE
#         # ===================================
#         if not is_valid:


#             error = validation_result


#             print(
#                 "\n❌ SQL Validation Failed:\n"
#             )

#             print(
#                 error
#             )


#             debug_logs.append(

#                 f"SQL Validation Failed:\n"
#                 f"{error}"
#             )


#             # ===================================
#             # LAST ATTEMPT
#             # ===================================
#             if retries == max_retries - 1:

#                 break


#             # ===================================
#             # FIX SQL
#             # ===================================
#             sql = fix_sql(

#                 query=query,

#                 sql=sql,

#                 error=error,

#                 schema=full_context,

#                 planner_output=planner_output
#             )


#             # ===================================
#             # CLEAN FIXED SQL
#             # ===================================
#             sql = (

#                 sql

#                 .replace(
#                     "```sql",
#                     ""
#                 )

#                 .replace(
#                     "```",
#                     ""
#                 )

#                 .strip()
#             )


#             print(
#                 "\n🔁 Fixed SQL:\n"
#             )

#             print(
#                 sql
#             )


#             debug_logs.append(

#                 f"Fixed SQL:\n"
#                 f"{sql}"
#             )


#             retries += 1

#             continue


#         # ===================================
#         # VALIDATION SUCCESS
#         # ===================================
#         sql = validation_result


#         print(
#             "\n✅ SQL Validation Passed:\n"
#         )

#         print(
#             sql
#         )


#         debug_logs.append(

#             f"SQL Validation Passed:\n"
#             f"{sql}"
#         )


#         # ===================================
#         # SQL EXECUTION
#         # ===================================
#         print(

#             f"\n🚀 Database Execution Attempt "
#             f"{attempt}"
#         )


#         result, error = execute_sql(

#             sql
#         )


#         # ===================================
#         # EXECUTION SUCCESS
#         # ===================================
#         if error is None:


#             print(
#                 "\n✅ SQL Execution Success"
#             )


#             debug_logs.append(

#                 "SQL Execution Success"
#             )


#             return {

#                 **state,

#                 "schema":
#                 full_context,

#                 "sql":
#                 sql,

#                 "result":
#                 result,

#                 "error":
#                 None,

#                 "failed_sql":
#                 None,

#                 "debug_logs":
#                 debug_logs
#             }


#         # ===================================
#         # EXECUTION FAILURE
#         # ===================================
#         print(

#             f"\n❌ Database Execution "
#             f"Failed - Attempt {attempt}"
#         )


#         print(
#             error
#         )


#         debug_logs.append(

#             f"SQL Execution Error:\n"
#             f"{error}"
#         )


#         # ===================================
#         # LAST ATTEMPT
#         # ===================================
#         if retries == max_retries - 1:

#             break


#         # ===================================
#         # FIX SQL
#         # ===================================
#         sql = fix_sql(

#             query=query,

#             sql=sql,

#             error=error,

#             schema=full_context,

#             planner_output=planner_output
#         )


#         # ===================================
#         # CLEAN FIXED SQL
#         # ===================================
#         sql = (

#             sql

#             .replace(
#                 "```sql",
#                 ""
#             )

#             .replace(
#                 "```",
#                 ""
#             )

#             .strip()
#         )


#         print(
#             "\n🔁 Fixed SQL:\n"
#         )

#         print(
#             sql
#         )


#         debug_logs.append(

#             f"Fixed SQL:\n"
#             f"{sql}"
#         )


#         retries += 1


#     # ===================================
#     # FINAL FAILURE
#     # ===================================
#     print(
#         "\n❌ SQL Pipeline Failed"
#     )


#     return {

#         **state,

#         "sql":
#         sql,

#         "result":
#         [],

#         "error":
#         error,

#         "failed_sql":
#         sql,

#         "debug_logs":
#         debug_logs
#     }






from agent.state import AgentState

from tools.sql_generator import (
    generate_sql,
    fix_sql
)

from tools.sql_executor import (
    execute_sql
)

from tools.sql_validator import (
    validate_sql
)

from tools.query_classifier import (
    is_sql_query
)


# ===================================
# CLEAN LLM SQL OUTPUT
# ===================================
def clean_sql(sql: str) -> str:

    if not sql:
        return ""

    sql = sql.strip()

    # Remove markdown code fences
    sql = (
        sql
        .replace("```sql", "")
        .replace("```mysql", "")
        .replace("```SQL", "")
        .replace("```MySQL", "")
        .replace("```", "")
        .strip()
    )

    # Remove accidental language identifier returned by some LLMs
    lines = sql.splitlines()

    if lines:

        first_line = lines[0].strip().lower()

        if first_line in (
            "mysql",
            "sql",
            "mysql sql"
        ):

            sql = "\n".join(
                lines[1:]
            ).strip()

    return sql


# ===================================
# SQL NODE
# ===================================
def sql_node(
    state: AgentState
) -> AgentState:


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


    # ===================================
    # DEBUG LOGS
    # ===================================
    debug_logs = []


    # ===================================
    # PLANNER OUTPUT
    # ===================================
    planner_output = state.get(

        "planner_output",

        {}
    )


    # ===================================
    # RETRIEVED CONTEXT
    # ===================================
    retrieved_entities = state.get(

        "retrieved_entities",

        []
    )


    joins = state.get(

        "joins",

        []
    )


    tables = state.get(

        "graph_tables",

        []
    )


    # ===================================
    # PRINT PLANNER OUTPUT
    # ===================================
    print(
        "\n🧠 Planner Output:\n"
    )

    print(
        planner_output
    )


    debug_logs.append(

        f"Planner Output:\n"
        f"{planner_output}"
    )


    # ===================================
    # QUERY CLASSIFICATION
    # ===================================
    if not is_sql_query(query):


        return {

            **state,

            "sql": None,

            "result": [],

            "final_answer":
            (
                "This question does not "
                "require database analysis."
            )
        }


    # ===================================
    # PRINT RETRIEVED ENTITIES
    # ===================================
    print(
        "\n📚 Retrieved Entities:\n"
    )


    for entity in retrieved_entities:


        print(
            entity["text"]
        )

        print(
            "-" * 50
        )


        debug_logs.append(

            f"Retrieved Entity:\n"
            f"{entity['text']}"
        )


    # ===================================
    # PRINT GRAPH RELATIONSHIPS
    # ===================================
    print(
        "\n🔗 Graph Join Paths:\n"
    )


    for join in joins:


        print(
            join["join_condition"]
        )


        debug_logs.append(

            f"Join:\n"
            f"{join['join_condition']}"
        )


    # ===================================
    # BUILD SCHEMA CONTEXT
    # ===================================
    schema_context = "\n\n".join([

        entity["text"]

        for entity in retrieved_entities
    ])


    # ===================================
    # BUILD JOIN CONTEXT
    # ===================================
    join_context = "\n\n".join([

        (

            f"Join Condition:\n"
            f"{join['join_condition']}\n\n"

            f"Relationship:\n"
            f"{join['relationship_type']}\n\n"

            f"Foreign Key:\n"
            f"{join['source_table']}."
            f"{join['source_column']}\n\n"

            f"Primary Key:\n"
            f"{join['target_table']}."
            f"{join['target_column']}"
        )

        for join in joins
    ])


    # ===================================
    # PLANNER CONTEXT
    # ===================================
    planner_context = f"""

PLANNER OUTPUT:

Intent:
{planner_output.get("intent")}


Metrics:
{planner_output.get("metrics")}


Metric Types:
{planner_output.get("metric_types")}


Dimensions:
{planner_output.get("dimensions")}


Filters:
{planner_output.get("filters")}


Time Context:
{planner_output.get("time_context")}


Requires Grouping:
{planner_output.get("requires_grouping")}


Requires Aggregation:
{planner_output.get("requires_aggregation")}
"""


    # ===================================
    # FINAL CONTEXT
    # ===================================
    full_context = f"""

{planner_context}


SCHEMA:

{schema_context}


VALID TABLES:

{tables}


VALID RELATIONSHIPS:

{join_context}
"""


    debug_logs.append(

        f"Full Context:\n"
        f"{full_context}"
    )


    # ===================================
    # PRINT AUTHORITATIVE METRICS
    # ===================================
    print(
        "\n📊 Authoritative Planner Metrics:\n"
    )

    print(
        planner_output.get(
            "metrics",
            []
        )
    )


    print(
        "\n📊 Authoritative Metric Types:\n"
    )

    print(
        planner_output.get(
            "metric_types",
            {}
        )
    )


    debug_logs.append(

        "Authoritative Planner Metrics:\n"
        f"{planner_output.get('metrics', [])}"
    )

    debug_logs.append(

        "Authoritative Metric Types:\n"
        f"{planner_output.get('metric_types', {})}"
    )


    # ===================================
    # SQL GENERATION
    # ===================================
    sql = generate_sql(

        query=query,

        schema=full_context,

        planner_output=planner_output
    )


    # ===================================
    # CLEAN GENERATED SQL
    # ===================================
    sql = clean_sql(sql)


    # ===================================
    # PRINT GENERATED SQL
    # ===================================
    print(
        "\n🧠 Generated SQL:\n"
    )

    print(
        sql
    )


    debug_logs.append(

        f"Generated SQL:\n"
        f"{sql}"
    )


    # ===================================
    # RETRY CONFIGURATION
    # ===================================
    max_retries = 5

    retries = 0

    error = None


    # ===================================
    # RETRY LOOP
    # ===================================
    while retries < max_retries:


        attempt = retries + 1


        print(

            f"\n🚀 SQL Attempt "
            f"{attempt}"
        )


        # ===================================
        # SQL VALIDATION
        # ===================================
        print(
            "\n🔎 SQL Validation:\n"
        )


        is_valid, validation_result = (

            validate_sql(
                sql
            )
        )


        # ===================================
        # VALIDATION FAILURE
        # ===================================
        if not is_valid:


            error = validation_result


            print(
                "\n❌ SQL Validation Failed:\n"
            )

            print(
                error
            )


            debug_logs.append(

                f"SQL Validation Failed:\n"
                f"{error}"
            )


            # ===================================
            # LAST ATTEMPT
            # ===================================
            if retries == max_retries - 1:

                break


            # ===================================
            # FIX SQL
            # ===================================
            sql = fix_sql(

                query=query,

                sql=sql,

                error=error,

                schema=full_context,

                planner_output=planner_output
            )


            # ===================================
            # CLEAN FIXED SQL
            # ===================================
            sql = clean_sql(sql)


            print(
                "\n🔁 Fixed SQL:\n"
            )

            print(
                sql
            )


            debug_logs.append(

                f"Fixed SQL:\n"
                f"{sql}"
            )


            retries += 1

            continue


        # ===================================
        # VALIDATION SUCCESS
        # ===================================
        sql = validation_result


        print(
            "\n✅ SQL Validation Passed:\n"
        )

        print(
            sql
        )


        debug_logs.append(

            f"SQL Validation Passed:\n"
            f"{sql}"
        )


        # ===================================
        # SQL EXECUTION
        # ===================================
        print(

            f"\n🚀 Database Execution Attempt "
            f"{attempt}"
        )


        result, error = execute_sql(

            sql
        )


        # ===================================
        # EXECUTION SUCCESS
        # ===================================
        if error is None:


            print(
                "\n✅ SQL Execution Success"
            )


            debug_logs.append(

                "SQL Execution Success"
            )


            return {

                **state,

                "schema":
                full_context,

                "sql":
                sql,

                "result":
                result,

                "error":
                None,

                "failed_sql":
                None,

                "debug_logs":
                debug_logs
            }


        # ===================================
        # EXECUTION FAILURE
        # ===================================
        print(

            f"\n❌ Database Execution "
            f"Failed - Attempt {attempt}"
        )


        print(
            error
        )


        debug_logs.append(

            f"SQL Execution Error:\n"
            f"{error}"
        )


        # ===================================
        # LAST ATTEMPT
        # ===================================
        if retries == max_retries - 1:

            break


        # ===================================
        # FIX SQL
        # ===================================
        sql = fix_sql(

            query=query,

            sql=sql,

            error=error,

            schema=full_context,

            planner_output=planner_output
        )


        # ===================================
        # CLEAN FIXED SQL
        # ===================================
        sql = clean_sql(sql)


        print(
            "\n🔁 Fixed SQL:\n"
        )

        print(
            sql
        )


        debug_logs.append(

            f"Fixed SQL:\n"
            f"{sql}"
        )


        retries += 1


    # ===================================
    # FINAL FAILURE
    # ===================================
    print(
        "\n❌ SQL Pipeline Failed"
    )


    return {

        **state,

        "sql":
        sql,

        "result":
        [],

        "error":
        error,

        "failed_sql":
        sql,

        "debug_logs":
        debug_logs
    }