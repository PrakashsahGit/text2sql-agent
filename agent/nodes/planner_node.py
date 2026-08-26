# from schemas.planner_schema import (
#     PlannerOutput
# )

# from utils.llm import llm


# # ===================================
# # PLANNER NODE
# # ===================================
# def planner_node(state):

#     query = (

#     state.get(
#         "resolved_query"
#     )

#     or

#     state["query"])

#     # ===================================
#     # RETRIEVED ENTITIES
#     # ===================================
#     retrieved_entities = state.get(

#         "retrieved_entities",

#         []
#     )


#     # ===================================
#     # GRAPH JOINS
#     # ===================================
#     joins = state.get(

#         "joins",

#         []
#     )


#     # ===================================
#     # GRAPH TABLES
#     # ===================================
#     tables = state.get(

#         "graph_tables",

#         []
#     )


#     # ===================================
#     # BUILD SCHEMA CONTEXT
#     # ===================================
#     schema_context = "\n\n".join([

#         entity["text"]

#         for entity in retrieved_entities
#     ])


#     # ===================================
#     # BUILD RELATIONSHIP CONTEXT
#     # ===================================
#     join_context = "\n\n".join([

#         (
#             f"Join Condition:\n"
#             f"{join['join_condition']}\n\n"

#             f"Relationship Type:\n"
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
#     # PROMPT
#     # ===================================
#     prompt = f"""
# You are an analytical query planner
# for an advanced Graph-RAG Text2SQL system.

# Your job is to extract the analytical
# intent of the user query.

# IMPORTANT:

# You MUST use ONLY the available
# schema entities and graph relationships.

# Do NOT invent:
# - tables
# - columns
# - dimensions
# - metrics

# Use ONLY what exists in the schema context.


# AVAILABLE TABLES:
# {tables}


# AVAILABLE SCHEMA:
# {schema_context}


# VALID RELATIONSHIPS:
# {join_context}


# Extract:

# 1. intent
# Possible values:
# - comparison
# - trend_analysis
# - ranking
# - aggregation
# - filtering
# - distribution
# - contribution

# 2. metrics
# Examples:
# - revenue
# - sales
# - profit
# - quantity
# - discount

# 3. dimensions
# Examples:
# - brand
# - region
# - customer_segment
# - category

# 4. filters
# Examples:
# - Nike
# - Samsung
# - Returned Orders
# - customer_name = XYZABC123

# 5. time_context
# Examples:
# - last 12 months
# - this year
# - last quarter

# 6. requires_grouping
# true if query compares/groups data

# 7. requires_aggregation
# true if totals/averages/counts required


# PLANNING RULES:

# 1. If planner intent is comparison,
# you MUST group by comparison dimensions.

# 2. For comparison intent:
# return separate rows
# for each comparison entity.

# 3. NEVER aggregate comparison queries
# into a single row.

# 4. If dimensions exist,
# GROUP BY is likely required.

# 5. Use ONLY dimensions
# available in schema context.

# 6. Use ONLY metrics inferable
# from schema context.

# 7. Respect graph relationships.

# 8. If no valid relational path exists
# between required entities,
# still infer intent normally.

# 9. Do NOT generate SQL.

# 10. Return ONLY one JSON OBJECT containing
# the planning result.

# 11. Do NOT return the JSON schema.
# Do NOT return properties, required,
# title, type, or description.

# 12. Do NOT explain anything.

# 13. The output must be an INSTANCE of
# PlannerOutput, not the schema definition.

# 14. Even if a filter value does not exist
# in the database, preserve the user's value
# as a filter. Do not validate database values.


# VALID OUTPUT FORMAT:

# {{
#     "intent": "aggregation",
#     "metrics": ["revenue"],
#     "dimensions": ["customer_name"],
#     "filters": ["XYZABC123"],
#     "time_context": null,
#     "requires_grouping": false,
#     "requires_aggregation": true
# }}


# EXAMPLES:

# Query:
# Compare Samsung and Nike sales

# Output:
# {{
#     "intent": "comparison",
#     "metrics": ["sales"],
#     "dimensions": ["brand"],
#     "filters": ["Samsung", "Nike"],
#     "time_context": null,
#     "requires_grouping": true,
#     "requires_aggregation": true
# }}


# Query:
# Top 5 regions by revenue

# Output:
# {{
#     "intent": "ranking",
#     "metrics": ["revenue"],
#     "dimensions": ["region"],
#     "filters": [],
#     "time_context": null,
#     "requires_grouping": true,
#     "requires_aggregation": true
# }}


# Query:
# Show me revenue for customer XYZABC123

# Output:
# {{
#     "intent": "aggregation",
#     "metrics": ["revenue"],
#     "dimensions": [],
#     "filters": ["XYZABC123"],
#     "time_context": null,
#     "requires_grouping": false,
#     "requires_aggregation": true
# }}


# USER QUERY:
# {query}
# """


#     # ===================================
#     # STRUCTURED OUTPUT
#     # ===================================
#     structured_llm = (

#         llm.with_structured_output(
#             PlannerOutput,method="json_schema" 
#         )
#     )


#     # ===================================
#     # INVOKE LLM
#     # ===================================
#     response = structured_llm.invoke(
#         prompt
#     )


#     # ===================================
#     # DEBUG OUTPUT
#     # ===================================
#     print("\n🧠 Planner Output:\n")

#     print(response)


#     # ===================================
#     # RETURN STATE
#     # ===================================
#     return {

#         **state,

#         "planner_output":
#         response.model_dump()
#     }



from schemas.planner_schema import (
    PlannerOutput
)

from utils.llm import llm

from tools.metrics import (
    METRICS,
    DERIVED_METRICS
)


# ===================================
# PLANNER NODE
# ===================================
def planner_node(state):


    # ===================================
    # USER QUERY
    # ===================================
    query = (

        state.get(
            "resolved_query"
        )

        or

        state["query"]
    )


    # ===================================
    # RETRIEVED ENTITIES
    # ===================================
    retrieved_entities = state.get(
        "retrieved_entities",
        []
    )


    # ===================================
    # GRAPH JOINS
    # ===================================
    joins = state.get(
        "joins",
        []
    )


    # ===================================
    # GRAPH TABLES
    # ===================================
    tables = state.get(
        "graph_tables",
        []
    )


    # ===================================
    # BUILD SCHEMA CONTEXT
    # ===================================
    schema_context = "\n\n".join([

        entity["text"]

        for entity in retrieved_entities
    ])


    # ===================================
    # BUILD RELATIONSHIP CONTEXT
    # ===================================
    join_context = "\n\n".join([

        (
            f"Join Condition:\n"
            f"{join['join_condition']}\n\n"

            f"Relationship Type:\n"
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
    # CANONICAL METRIC DEFINITIONS
    # ===================================
    canonical_metrics = """
CANONICAL METRIC NAMES

You MUST use these exact names in the
metrics array.

SEMANTIC METRICS:

- revenue
- profit

PHYSICAL METRICS:

- quantity
- discount_percent

DERIVED METRICS:

- revenue_contribution
- revenue_contribution_percentage
"""


    # ===================================
    # PROMPT
    # ===================================
    prompt = f"""
You are an analytical query planner
for an advanced Graph-RAG Text2SQL system.

Your job is to extract the analytical
intent of the user query.

You are NOT generating SQL.

You MUST return an instance of
PlannerOutput.


==================================================
IMPORTANT SCHEMA RULES
==================================================

You MUST use ONLY the available
schema entities and graph relationships.

Do NOT invent:

- tables
- columns
- dimensions
- physical metrics

Use ONLY what exists in the schema context
when identifying physical database fields.


==================================================
AVAILABLE TABLES
==================================================

{tables}


==================================================
AVAILABLE SCHEMA
==================================================

{schema_context}


==================================================
VALID RELATIONSHIPS
==================================================

{join_context}


==================================================
CANONICAL METRICS
==================================================

{canonical_metrics}


==================================================
METRIC EXTRACTION RULES
==================================================

Identify EVERY metric requested by the user.

NEVER omit a requested metric.

NEVER create a new metric name.

NEVER shorten a canonical metric name.

NEVER paraphrase a canonical metric name.

The metrics array MUST contain the exact
canonical names listed above.


==================================================
SEMANTIC METRIC MAPPING
==================================================

User phrases such as:

"revenue"
"total revenue"
"sales revenue"

MUST map to:

"revenue"


User phrases such as:

"profit"
"total profit"
"total profits"

MUST map to:

"profit"


==================================================
QUANTITY MAPPING
==================================================

User phrases such as:

"quantity"
"total quantity"
"quantity sold"
"total quantity sold"
"units"
"units sold"
"total units"
"total units sold"
"total units purchased"

MUST map to:

"quantity"


==================================================
DISCOUNT MAPPING
==================================================

User phrases such as:

"discount"
"discount percent"
"discount percentage"
"average discount"
"average discount percent"
"average discount percentage"
"avg discount"

MUST map to:

"discount_percent"


IMPORTANT:

NEVER return:

"discount"

when the canonical metric is:

"discount_percent"

NEVER return:

"average_discount"

The canonical metric is:

"discount_percent".


==================================================
REVENUE CONTRIBUTION MAPPING
==================================================

User phrases such as:

"revenue contribution"
"revenue share"
"contribution to revenue"
"share of revenue"

MUST map to:

"revenue_contribution"


User phrases such as:

"percentage contribution"
"percentage contribution to revenue"
"percentage contribution to sales"
"revenue contribution percentage"
"percentage share of revenue"
"product's percentage contribution to revenue"
"each product's percentage contribution to revenue"

MUST map to:

"revenue_contribution_percentage"


IMPORTANT:

NEVER return:

"contribution"

by itself.

NEVER return:

"percentage_contribution"

unless that is explicitly a canonical metric.

Use:

"revenue_contribution"

or:

"revenue_contribution_percentage"

according to the user's wording.


==================================================
METRIC TYPE RULES
==================================================

For EVERY metric in the metrics array,
identify its type.

Allowed values:

- physical_column
- semantic_metric
- derived_metric


Use the following authoritative mapping:

revenue
    -> semantic_metric

profit
    -> semantic_metric

quantity
    -> physical_column

discount_percent
    -> physical_column

revenue_contribution
    -> derived_metric

revenue_contribution_percentage
    -> derived_metric


The downstream Python code will
recalculate metric types authoritatively.

Therefore your metric_types output
must still use the canonical names.


==================================================
PHYSICAL COLUMN RULES
==================================================

Use "physical_column" ONLY when the
canonical metric corresponds to an actual
column in the available schema.

For example:

quantity
discount_percent


Do NOT create:

average_discount

total_quantity

discount

units_sold

These are user-language expressions,
not physical column names.


==================================================
SEMANTIC METRIC RULES
==================================================

Use "semantic_metric" for business metrics
with a known definition.

Available semantic metrics are:

- revenue
- profit


==================================================
DERIVED METRIC RULES
==================================================

Use "derived_metric" for:

- revenue_contribution
- revenue_contribution_percentage

Do NOT invent a mathematical definition
inside the planner.

Only identify the canonical metric name
and its type.


==================================================
IMPORTANT: AGGREGATION LANGUAGE
==================================================

Words such as:

- total
- sum
- average
- avg
- highest
- top
- lowest
- ranking

describe HOW a metric should be calculated.

They do NOT create new metric names.

Examples:

"total revenue"
    -> revenue

"total profit"
    -> profit

"total quantity sold"
    -> quantity

"average discount"
    -> discount_percent


The SQL generation stage determines the
appropriate aggregation function.


==================================================
DIMENSIONS
==================================================

Identify dimensions requested by the user.

Examples:

- brand
- region
- customer_segment
- category
- customer_name
- product_name


Use ONLY dimensions available in the
schema context.


==================================================
FILTERS
==================================================

Extract explicit filters from the user.

Examples:

- Nike
- Samsung
- Returned Orders
- customer_name = XYZABC123
- quantity >= 30


IMPORTANT:

Preserve explicit user filter values.

Do NOT validate database values.


==================================================
TIME CONTEXT
==================================================

Examples:

- last 12 months
- this year
- last quarter
- previous month

Use null when no time context exists.


==================================================
REQUIRES GROUPING
==================================================

Set requires_grouping to true when:

- the query groups by a dimension
- the query compares entities
- the query ranks entities
- the query breaks data down by a dimension
- the query requests top/bottom entities


Otherwise use false.


==================================================
REQUIRES AGGREGATION
==================================================

Set requires_aggregation to true when:

- totals are requested
- averages are requested
- sums are requested
- counts are requested
- rankings are requested
- semantic metrics are requested
- derived metrics require aggregation


==================================================
PLANNING RULES
==================================================

1. If intent is comparison,
   group by comparison dimensions.

2. For comparison queries,
   return separate rows for each
   comparison entity.

3. NEVER collapse comparison queries
   into one row.

4. If dimensions exist,
   grouping is usually required.

5. Use ONLY dimensions available
   in the schema.

6. Use ONLY physical columns available
   in the schema.

7. Semantic metrics may be used when
   supported by the canonical metric list.

8. Derived metrics must be identified
   as derived_metric.

9. NEVER silently convert one requested
   metric into another metric.

10. NEVER invent physical columns.

11. NEVER invent metric names.

12. NEVER shorten canonical metric names.

13. Respect graph relationships.

14. Do NOT generate SQL.

15. Return ONLY one JSON object.

16. Do NOT return the JSON schema.

17. Do NOT return:

- properties
- required
- title
- type
- description

18. Do NOT explain anything.

19. The output must be an INSTANCE
    of PlannerOutput.


==================================================
VALID OUTPUT FORMAT
==================================================

{{
    "intent": "aggregation",

    "metrics": [
        "revenue"
    ],

    "metric_types": {{
        "revenue": "semantic_metric"
    }},

    "dimensions": [
        "customer_name"
    ],

    "filters": [],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 1
==================================================

Query:

Compare Samsung and Nike sales


Output:

{{
    "intent": "comparison",

    "metrics": [
        "revenue"
    ],

    "metric_types": {{
        "revenue": "semantic_metric"
    }},

    "dimensions": [
        "brand"
    ],

    "filters": [
        "Samsung",
        "Nike"
    ],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 2
==================================================

Query:

Top 5 regions by revenue


Output:

{{
    "intent": "ranking",

    "metrics": [
        "revenue"
    ],

    "metric_types": {{
        "revenue": "semantic_metric"
    }},

    "dimensions": [
        "region"
    ],

    "filters": [],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 3
==================================================

Query:

Show me revenue for customer XYZABC123


Output:

{{
    "intent": "aggregation",

    "metrics": [
        "revenue"
    ],

    "metric_types": {{
        "revenue": "semantic_metric"
    }},

    "dimensions": [],

    "filters": [
        "XYZABC123"
    ],

    "time_context": null,

    "requires_grouping": false,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 4
==================================================

Query:

Show me customer lifetime value


Output:

{{
    "intent": "aggregation",

    "metrics": [
        "customer_lifetime_value"
    ],

    "metric_types": {{
        "customer_lifetime_value": "derived_metric"
    }},

    "dimensions": [],

    "filters": [],

    "time_context": null,

    "requires_grouping": false,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 5
==================================================

Query:

Show me customer segment


Output:

{{
    "intent": "aggregation",

    "metrics": [],

    "metric_types": {{}},

    "dimensions": [
        "customer_segment"
    ],

    "filters": [],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": false
}}


==================================================
EXAMPLE 6
==================================================

Query:

For each customer segment, show the top
3 products by revenue. Include customer
segment, product name, total revenue,
total quantity sold, average discount,
and each product's percentage contribution
to revenue within its customer segment.
Only include products with at least
30 units sold.


Output:

{{
    "intent": "ranking",

    "metrics": [
        "revenue",
        "quantity",
        "discount_percent",
        "revenue_contribution_percentage"
    ],

    "metric_types": {{
        "revenue": "semantic_metric",
        "quantity": "physical_column",
        "discount_percent": "physical_column",
        "revenue_contribution_percentage": "derived_metric"
    }},

    "dimensions": [
        "customer_segment",
        "product_name"
    ],

    "filters": [
        "quantity >= 30"
    ],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 7
==================================================

Query:

Show me total profit by customer name.


Output:

{{
    "intent": "aggregation",

    "metrics": [
        "profit"
    ],

    "metric_types": {{
        "profit": "semantic_metric"
    }},

    "dimensions": [
        "customer_name"
    ],

    "filters": [],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": true
}}


==================================================
EXAMPLE 8
==================================================

Query:

Show me the top 10 customers by profit.
Include customer name, total profit,
total revenue, total quantity purchased,
and average discount.


Output:

{{
    "intent": "ranking",

    "metrics": [
        "profit",
        "revenue",
        "quantity",
        "discount_percent"
    ],

    "metric_types": {{
        "profit": "semantic_metric",
        "revenue": "semantic_metric",
        "quantity": "physical_column",
        "discount_percent": "physical_column"
    }},

    "dimensions": [
        "customer_name"
    ],

    "filters": [],

    "time_context": null,

    "requires_grouping": true,

    "requires_aggregation": true
}}


==================================================
USER QUERY
==================================================

{query}
"""


    # ===================================
    # STRUCTURED OUTPUT
    # ===================================
    structured_llm = (

        llm.with_structured_output(
            PlannerOutput,
            method="json_schema"
        )
    )


    # ===================================
    # INVOKE LLM
    # ===================================
    response = structured_llm.invoke(
        prompt
    )


    # ===================================
    # HANDLE EMPTY RESPONSE
    # ===================================
    if response is None:

        print(
            "\n❌ Planner returned no structured response"
        )

        return {

            **state,

            "planner_output": {},

            "error":
            "Planner failed to return a structured response"
        }


    # ===================================
    # CANONICAL METRIC ALIASES
    # ===================================
    METRIC_ALIASES = {

        # -------------------------------
        # REVENUE
        # -------------------------------

        "revenue":
            "revenue",

        "total_revenue":
            "revenue",

        "sales_revenue":
            "revenue",


        # -------------------------------
        # PROFIT
        # -------------------------------

        "profit":
            "profit",

        "total_profit":
            "profit",


        # -------------------------------
        # QUANTITY
        # -------------------------------

        "quantity":
            "quantity",

        "total_quantity":
            "quantity",

        "quantity_sold":
            "quantity",

        "total_quantity_sold":
            "quantity",

        "units":
            "quantity",

        "units_sold":
            "quantity",

        "total_units":
            "quantity",

        "total_units_sold":
            "quantity",

        "total_units_purchased":
            "quantity",


        # -------------------------------
        # DISCOUNT
        # -------------------------------

        "discount":
            "discount_percent",

        "discount_percent":
            "discount_percent",

        "discount_percentage":
            "discount_percent",

        "average_discount":
            "discount_percent",

        "avg_discount":
            "discount_percent",

        "average_discount_percent":
            "discount_percent",

        "average_discount_percentage":
            "discount_percent",


        # -------------------------------
        # REVENUE CONTRIBUTION
        # -------------------------------

        "contribution":
            "revenue_contribution",

        "revenue_contribution":
            "revenue_contribution",

        "revenue_share":
            "revenue_contribution",

        "contribution_to_revenue":
            "revenue_contribution",


        # -------------------------------
        # REVENUE CONTRIBUTION %
        # -------------------------------

        "percentage_contribution":
            "revenue_contribution_percentage",

        "contribution_percentage":
            "revenue_contribution_percentage",

        "revenue_contribution_percentage":
            "revenue_contribution_percentage",

        "percentage_contribution_to_revenue":
            "revenue_contribution_percentage",

        "revenue_percentage_contribution":
            "revenue_contribution_percentage"
    }


    # ===================================
    # NORMALIZE METRICS
    # ===================================
    normalized_metrics = []


    for metric in response.metrics:

        metric_key = (

            metric
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )


        canonical_metric = (

            METRIC_ALIASES.get(

                metric_key,

                metric_key
            )
        )


        if canonical_metric not in normalized_metrics:

            normalized_metrics.append(
                canonical_metric
            )


    response.metrics = normalized_metrics


    # ===================================
    # AUTHORITATIVE METRIC TYPES
    # ===================================
    # The LLM identifies WHICH metrics
    # the user wants.
    #
    # Python determines WHAT TYPE each
    # metric is.
    #
    # This prevents model-specific
    # structured-output classification
    # errors.
    # ===================================

    metric_types = {}


    # ===================================
    # AVAILABLE PHYSICAL COLUMNS
    # ===================================
    physical_columns = {

        entity["column"]

        for entity in retrieved_entities
    }


    # ===================================
    # CLASSIFY EVERY METRIC
    # ===================================
    for metric in response.metrics:

        # -------------------------------
        # SEMANTIC METRIC
        # -------------------------------
        if metric in METRICS:

            metric_types[metric] = (
                "semantic_metric"
            )


        # -------------------------------
        # DERIVED METRIC
        # -------------------------------
        elif metric in DERIVED_METRICS:

            metric_types[metric] = (
                "derived_metric"
            )


        # -------------------------------
        # PHYSICAL COLUMN
        # -------------------------------
        elif metric in physical_columns:

            metric_types[metric] = (
                "physical_column"
            )


        # -------------------------------
        # UNKNOWN
        # -------------------------------
        else:

            metric_types[metric] = (
                "unknown_metric"
            )

            print(
                f"\n⚠️ Unknown metric returned "
                f"by planner: {metric}"
            )


    # ===================================
    # OVERRIDE LLM METRIC TYPES
    # ===================================
    response.metric_types = metric_types


    # ===================================
    # DEBUG OUTPUT
    # ===================================
    print(
        "\n🧠 Planner Output:\n"
    )

    print(response)


    # ===================================
    # RETURN STATE
    # ===================================
    return {

        **state,

        "planner_output":
        response.model_dump()
    }