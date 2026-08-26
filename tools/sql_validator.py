def validate_sql(sql: str):

    sql = sql.strip()

    sql_lower = sql.lower().strip()


    # -----------------------------------
    # 1. Allow ONLY SELECT queries
    # -----------------------------------
    allowed = (
        "select",
        "with"
    )

    if not sql_lower.startswith(allowed):

        return False, (
            "Only SELECT queries are allowed"
        )


    # -----------------------------------
    # 2. Block dangerous SQL
    # -----------------------------------
    forbidden = [
        "drop",
        "delete",
        "truncate",
        "alter",
        "create",
        "insert",
        "update"
    ]

    for word in forbidden:

        if word in sql_lower:

            return False, (
                f"Unsafe SQL keyword detected: {word}"
            )


    # -----------------------------------
    # 3. Normalize trailing semicolon
    # -----------------------------------
    sql = sql.rstrip(";").strip()

    sql_lower = sql.lower()


    # -----------------------------------
    # 4. LIMIT protection
    # -----------------------------------
    if (
        "limit" not in sql_lower
        and "count(" not in sql_lower
    ):

        sql += " LIMIT 100"


    # -----------------------------------
    # 5. Restore semicolon
    # -----------------------------------
    sql += ";"


    # -----------------------------------
    # 6. Validation success
    # -----------------------------------
    return True, sql