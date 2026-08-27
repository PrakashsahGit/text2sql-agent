# ===================================
# SEMANTIC BUSINESS METRICS
# ===================================

METRICS = {

    "revenue": """
    (
        unit_price * quantity
    )
    -
    (
        unit_price * quantity
        * discount_percent / 100
    )
    +
    shipping_cost
    """,


    "profit": """
    (
        (
            unit_price * quantity
        )
        -
        (
            unit_price * quantity
            * discount_percent / 100
        )
        -
        (
            cost_price * quantity
        )
    )
    """
}


# ===================================
# DERIVED METRICS
# ===================================

DERIVED_METRICS = {

    # ---------------------------------
    # Revenue contribution
    # ---------------------------------
    "revenue_contribution": """
    Revenue contribution percentage.

    Definition:

    entity_revenue
    /
    parent_group_revenue
    *
    100

    For grouped queries:

    1. Calculate revenue for each entity
       at the requested grouping level.

    2. Calculate the total revenue for the
       parent grouping.

    3. Divide entity revenue by parent-group
       revenue.

    4. Multiply by 100.

    Example:

    Product revenue within customer segment:

    product_revenue
    /
    segment_revenue
    *
    100

    Required SQL pattern:

    product_agg AS (
        ...
        GROUP BY customer_segment, product_name
    ),

    segment_totals AS (
        SELECT
            customer_segment,
            SUM(revenue) AS segment_revenue
        FROM product_agg
        GROUP BY customer_segment
    )

    Then:

    (
        product_agg.revenue
        /
        NULLIF(segment_totals.segment_revenue, 0)
    ) * 100

    The final alias MUST be:

    revenue_contribution
    """,


    # ---------------------------------
    # Revenue contribution percentage
    # ---------------------------------
    "revenue_contribution_percentage": """
    Revenue contribution percentage.

    Definition:

    entity_revenue
    /
    parent_group_revenue
    *
    100

    For grouped queries:

    1. Calculate revenue for each entity.

    2. Calculate the total revenue for the
       parent grouping.

    3. Divide entity revenue by parent-group
       revenue.

    4. Multiply by 100.

    Example:

    Product revenue within customer segment:

    product_revenue
    /
    segment_revenue
    *
    100

    Required SQL pattern:

    product_agg AS (
        ...
        GROUP BY customer_segment, product_name
    ),

    segment_totals AS (
        SELECT
            customer_segment,
            SUM(revenue) AS segment_revenue
        FROM product_agg
        GROUP BY customer_segment
    )

    Then:

    (
        product_agg.revenue
        /
        NULLIF(segment_totals.segment_revenue, 0)
    ) * 100

    The final alias MUST be:

    revenue_contribution_percentage
    """
}