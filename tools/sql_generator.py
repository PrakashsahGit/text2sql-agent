from utils.llm import llm

from tools.metrics import (
    METRICS,
    DERIVED_METRICS
)


# ===================================
# SHARED SQL RULES
# ===================================
SQL_RULES = """
You are an expert MySQL analytics engineer.

Your task is to generate accurate,
analytical, production-grade
MySQL SQL queries.


==================================================
CORE SQL RULES
==================================================

1. Use ONLY tables and columns
provided in the schema context.

2. NEVER invent tables.

3. NEVER invent columns.

4. NEVER hallucinate joins.

5. NEVER hallucinate bridge tables.

6. ONLY use joins from:
VALID RELATIONSHIPS section.

7. ALWAYS use exact table-column mappings.

8. Before generating SQL,
verify every physical column exists
exactly as written in the schema.

9. Use valid MySQL syntax only.

10. Return ONLY SQL.

11. NEVER explain anything.

12. ONLY use joins explicitly provided
in the VALID RELATIONSHIPS section.

13. If no graph join path exists between
tables, you MUST NOT join those tables.

14. NEVER infer joins using:
- similar column names
- numeric values
- semantic assumptions

15. If two tables are unrelated,
do NOT connect them.


==================================================
AUTHORITATIVE PLANNER METRICS
==================================================

The planner output is authoritative.

The planner provides:

Metrics:
[
    metric_name_1,
    metric_name_2
]

Metric Types:
{
    "metric_name": "metric_type"
}

You MUST preserve the exact metric names
provided by the planner.

NEVER rename a planner metric.

For example, if the planner provides:

revenue_contribution_percentage

you MUST use:

AS revenue_contribution_percentage

NEVER use:

AS percentage_contribution

NEVER use:

AS contribution_percentage

NEVER invent another alias.

The final SELECT MUST contain every
metric requested by the planner.

The final SELECT alias MUST exactly match
the planner metric name.


==================================================
METRIC ALIAS RULES
==================================================

1. Every requested planner metric MUST
appear in the final SELECT.

2. The final SQL alias MUST exactly match
the planner metric name.

3. NEVER rename planner metrics.

4. NEVER abbreviate planner metrics.

5. NEVER create alternative metric names.

6. NEVER use NULL for a metric that can
be calculated.

7. NEVER use a text placeholder for a metric
that can be calculated.

Example:

Correct:

(
    customer_revenue
    / NULLIF(overall_revenue, 0)
) * 100 AS revenue_contribution_percentage

Incorrect:

NULL AS revenue_contribution_percentage

Incorrect:

'metric not defined'
    AS revenue_contribution_percentage

Incorrect:

percentage_contribution

Incorrect:

contribution_percentage


==================================================
METRIC TYPE RULES
==================================================

Allowed metric types:

- physical_column
- semantic_metric
- derived_metric


--------------------------------------------------
PHYSICAL COLUMN
--------------------------------------------------

If metric_types says:

metric_name = physical_column

then the metric MUST be a real physical
column in the available schema.

Example:

customers.customer_lifetime_value

If the requested physical column does NOT
exist in the schema:

DO NOT:

- replace it with revenue
- replace it with customer revenue
- calculate an alternative metric
- assume customer_id represents it
- invent a formula
- silently substitute another metric

Instead return a safe SQL result indicating
that the requested physical column does
not exist.


--------------------------------------------------
SEMANTIC METRIC
--------------------------------------------------

If metric_types says:

metric_name = semantic_metric

then use the corresponding definition
from AVAILABLE BUSINESS METRICS.

Example:

revenue

must use:

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

IMPORTANT:

Do NOT assume semantic metrics are physical
database columns.

NEVER generate:

SUM(s.revenue)

unless revenue physically exists.


--------------------------------------------------
DERIVED METRIC
--------------------------------------------------

If metric_types says:

metric_name = derived_metric

then check AVAILABLE DERIVED METRICS.

If a definition exists:

1. MUST calculate the metric.

2. NEVER return NULL.

3. NEVER return a string saying
   the metric is undefined.

4. NEVER omit the metric.

5. NEVER substitute another metric.

6. Use CTEs, subqueries, window functions,
   CROSS JOINs, or other valid SQL techniques
   when required.

7. Derived metrics may depend on
   previously calculated aggregates.


==================================================
UNDEFINED DERIVED METRIC
==================================================

If metric_types says:

derived_metric

but there is NO definition in:

AVAILABLE DERIVED METRICS

and the user has not explicitly defined
the calculation:

DO NOT invent the calculation.

Return a safe SQL result explaining that
the requested derived metric cannot be
calculated from the available definitions.


==================================================
METRIC CONSISTENCY
==================================================

The metric type provided by the planner
MUST be respected.

Never change:

physical_column

into:

semantic_metric

Never change:

derived_metric

into:

semantic_metric

Never silently substitute one metric
for another.


==================================================
PLANNER OBEYING RULES
==================================================

16. ALWAYS obey planner intent.

17. If planner requires grouping,
you MUST use GROUP BY.

18. If planner intent is:

- comparison
- ranking
- distribution

then grouped aggregation is REQUIRED.

19. For comparison intent:
return separate rows
for each comparison dimension.

20. NEVER collapse comparison queries
into a single aggregated row.

21. If planner dimensions exist,
GROUP BY those dimensions.

22. If planner intent is ranking:
use:

ORDER BY ... DESC

23. If query asks:

- top
- highest
- best

use:

ORDER BY ... DESC


==================================================
BUSINESS METRIC RULES
==================================================

24. Business metrics such as:

- revenue
- profit
- margin
- average_order_value
- sales

may be semantic metrics,
NOT physical DB columns.

25. NEVER generate columns like:

- revenue
- profit
- margin

unless explicitly present in schema
OR they are being derived using a provided
business metric definition.

26. ALWAYS use provided business metric
definitions.

27. Revenue is usually derived.

28. Profit is usually derived.

29. Margin is usually derived.

30. NEVER assume semantic metrics exist
physically.


==================================================
RELATIONSHIP RULES
==================================================

VALID RELATIONSHIPS include:

- foreign key direction
- primary key side
- relationship cardinality

Always respect relationship direction
when generating joins.

Only use joins explicitly provided
in VALID RELATIONSHIPS.


==================================================
AGGREGATION RULES
==================================================

31. Use proper aggregations:

- SUM()
- COUNT()
- AVG()
- MAX()
- MIN()

32. Use readable aliases.

33. Add LIMIT where appropriate.

34. Use analytical SQL best practices.

35. Avoid unnecessary joins.

36. ONLY use joins explicitly provided
in VALID RELATIONSHIPS.

37. If no graph join path exists between
tables, you MUST NOT join those tables.

38. NEVER infer joins using:

- similar column names
- numeric values
- semantic assumptions

39. If two tables are unrelated,
do NOT connect them.


==================================================
MULTI-STAGE AGGREGATION RULES
==================================================

40. When a query requires calculations at
multiple aggregation levels, use multiple
CTEs or subqueries.

41. Always calculate the lowest required
aggregation level first.

Example:

product revenue by customer segment:

GROUP BY
    customer_segment,
    product_name


42. If a metric requires a higher-level
total, calculate that total in a separate
CTE or subquery.

Example:

segment revenue:

SELECT
    customer_segment,
    SUM(revenue) AS segment_revenue
FROM product_sales
GROUP BY customer_segment


43. Join the lower-level aggregation to
the higher-level aggregation using the
available grouping key.

Example:

product_sales.customer_segment
=
segment_totals.customer_segment


44. Derived contribution metrics must be
calculated AFTER both aggregation levels
exist.

Example:

product revenue contribution within segment:

product_revenue
/
segment_revenue
* 100


45. Ranking must occur AFTER all required
metrics have been calculated.

Example:

ROW_NUMBER() OVER (
    PARTITION BY customer_segment
    ORDER BY revenue DESC
)


46. Top-N filtering must occur AFTER
ROW_NUMBER() has been calculated.

Example:

WHERE rn <= 3


47. If a physical metric such as
discount_percent is requested, calculate
it at the appropriate base aggregation
level.

Example:

AVG(s.discount_percent) AS average_discount


48. NEVER replace a requested metric with:

NULL


49. NEVER create:

NULL AS metric_name

when the requested metric can be calculated
from the available schema.


50. NEVER create a placeholder such as:

'metric not defined'

for a metric whose definition exists.


51. Preserve every requested metric through
all CTE levels until the final SELECT.


52. Before returning SQL, verify that every
planner metric has a real expression in
the final SELECT.


53. For top-N-per-group queries, the normal
execution pattern should be:

base aggregation
        ↓
higher-level aggregation if required
        ↓
derived metrics
        ↓
ROW_NUMBER()
        ↓
WHERE rn <= N
        ↓
final SELECT


==================================================
DERIVED METRIC CALCULATION EXAMPLES
==================================================

Example 1:

Requested:

revenue_contribution_percentage

If customer revenue has already been
calculated:

customer_revenue
/
overall_revenue
* 100

Example SQL:

WITH customer_revenue AS (
    ...
),
overall AS (
    SELECT
        SUM(customer_revenue) AS overall_revenue
    FROM customer_revenue
)
SELECT
    customer_revenue,
    (
        customer_revenue
        / NULLIF(overall_revenue, 0)
    ) * 100 AS revenue_contribution_percentage
FROM customer_revenue
CROSS JOIN overall;


Example 2:

Requested:

average_revenue

First calculate revenue at the
customer level.

Then:

AVG(customer_revenue)

Do NOT calculate:

AVG(unit_price * quantity)

when the requested metric is
average revenue per customer.

The aggregation level matters.


Example 3:

Requested:

revenue_contribution_percentage
for products within each customer segment.

First calculate:

product revenue
GROUP BY customer_segment, product_name

Then calculate:

segment revenue
GROUP BY customer_segment

Then calculate:

product revenue
/
segment revenue
* 100

Then calculate ranking:

ROW_NUMBER() OVER (
    PARTITION BY customer_segment
    ORDER BY revenue DESC
)

Then filter:

WHERE rn <= 3


==================================================
PHYSICAL METRIC PRESERVATION
==================================================

If a physical metric is requested and the
query already has the required source rows,
calculate it before moving to another
aggregation level.

Example:

AVG(s.discount_percent)
AS average_discount

Do NOT replace it with:

NULL AS average_discount

If the metric is needed after a CTE,
calculate it inside the CTE and expose it
as an alias.


==================================================
IMPORTANT FINAL CHECK
==================================================

Before finalizing SQL:

- verify joins
- verify grouping
- verify metrics
- verify metric_types
- verify dimensions
- verify physical column existence
- verify business metric definitions
- verify derived metric definitions
- verify aggregation levels
- verify ranking logic
- verify top-N filtering
- verify planner intent
- verify SQL syntax

For EVERY metric in planner_output.metrics:

1. Find the metric in the final SELECT.

2. Verify it has a real SQL expression.

3. Verify it is not NULL.

4. Verify it is not a string placeholder.

5. Verify it is not silently replaced
   by another metric.

6. Verify its alias exactly matches
   the planner metric name.

For derived metrics:

- verify all required lower-level
  aggregates exist
- verify all required higher-level
  aggregates exist
- verify the final formula is present

For top-N-per-group queries:

- verify ROW_NUMBER() or equivalent
  partitioned ranking exists
- verify ORDER BY uses the requested
  ranking metric
- verify the final query filters
  to the requested N

MOST IMPORTANT:

Every metric requested by the planner
MUST be represented by a real SQL
expression in the final SELECT.

NEVER silently replace a requested metric
with:

NULL

or:

'metric not defined'

or another metric.
"""


# ===================================
# CLEAN SQL
# ===================================
def clean_sql(sql: str):

    sql = sql.strip()

    sql = (
        sql
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    return sql


# ===================================
# BUILD PLANNER CONTEXT
# ===================================
def build_planner_metric_context(
    planner_output: dict
):

    metrics = planner_output.get(
        "metrics",
        []
    )

    metric_types = planner_output.get(
        "metric_types",
        {}
    )

    return f"""
==================================================
AUTHORITATIVE PLANNER OUTPUT
==================================================

Metrics:
{metrics}

Metric Types:
{metric_types}

==================================================
STRICT METRIC REQUIREMENT
==================================================

The above metric names are authoritative.

Every metric listed above MUST appear
in the final SELECT.

Every final SELECT alias MUST exactly
match the corresponding planner metric.

NEVER rename them.

Example:

Planner:
revenue_contribution_percentage

Correct:
AS revenue_contribution_percentage

Incorrect:
AS percentage_contribution

Incorrect:
AS contribution_percentage

Incorrect:
AS contribution

NEVER invent a metric name.
"""


# ===================================
# GENERATE SQL
# ===================================
def generate_sql(
    query: str,
    schema: str,
    planner_output: dict
):

    planner_context = (
        build_planner_metric_context(
            planner_output
        )
    )

    prompt = f"""
{SQL_RULES}


{planner_context}


==================================================
AVAILABLE BUSINESS METRICS
==================================================

{METRICS}


==================================================
AVAILABLE DERIVED METRICS
==================================================

{DERIVED_METRICS}


==================================================
SCHEMA + GRAPH CONTEXT
==================================================

{schema}


==================================================
USER QUESTION
==================================================

{query}


==================================================
FINAL GENERATION REQUIREMENTS
==================================================

Before returning SQL:

1. Check every planner metric.

2. Check every metric type.

3. Check every physical column.

4. Check every semantic metric definition.

5. Check every derived metric definition.

6. Check every requested dimension.

7. Check every required aggregation level.

8. Check ranking and top-N logic.

9. Ensure every planner metric appears
   in the final SELECT.

10. Ensure every final SELECT alias
    exactly matches the planner metric.

11. Never output NULL for a calculable metric.

12. Never output a text placeholder for
    a calculable metric.

13. Never rename a planner metric.

Return ONLY MySQL SQL.

==================================================
MYSQL SQL
==================================================
"""

    response = llm.invoke(
        prompt
    )

    sql = response.content.strip()

    return clean_sql(sql)


# ===================================
# FIX SQL
# ===================================
def fix_sql(
    query: str,
    sql: str,
    error: str,
    schema: str,
    planner_output: dict
):

    planner_context = (
        build_planner_metric_context(
            planner_output
        )
    )

    prompt = f"""
{SQL_RULES}


{planner_context}


==================================================
SQL FIXING RULES
==================================================

The SQL query below failed or produced
an invalid analytical result.

Your task is to fix the SQL while
preserving the original analytical intent.


1. Preserve the original analytical intent.

2. Use ONLY valid schema columns.

3. Use ONLY valid joins.

4. NEVER repeat the same failed SQL.

5. Fix:

- invalid columns
- invalid joins
- invalid tables
- grouping
- aggregations
- aliases
- syntax
- metric derivation
- derived metric calculations
- missing CTE stages
- incorrect aggregation levels
- incorrect ranking logic


6. Use graph joins when available.


7. If planner intent is comparison:
ensure GROUP BY exists.


8. If business metrics are semantic:
derive them using the provided definition.


9. If metric type is physical_column:
the column MUST exist in the schema.


10. Do NOT replace a missing physical
column with another metric.


11. If metric type is derived_metric:
check AVAILABLE DERIVED METRICS.


12. If a derived metric definition exists,
you MUST calculate it.


13. NEVER replace a derived metric with:

NULL

or:

'metric not defined'

or another metric.


14. If the derived metric requires
multiple aggregation levels, use CTEs
or subqueries.


15. Preserve requested metric aliases.


16. If the failed SQL contains:

NULL AS <requested_metric>

replace it with the real calculation
when the metric can be calculated.


17. If the failed SQL contains:

'<metric not defined>' AS <requested_metric>

and the metric exists in AVAILABLE
DERIVED METRICS, calculate the metric
instead.


18. If a requested physical metric such as
discount_percent was lost inside a CTE,
add the required aggregation to the
appropriate CTE.


19. For contribution metrics requiring
a group-level total:

- calculate the lower-level metric
- calculate the group total
- calculate the contribution percentage
- preserve the result for ranking
- preserve the result for the final SELECT


20. For top-N-per-group queries:

- calculate the requested metrics first
- calculate higher-level totals if required
- calculate derived metrics
- calculate ROW_NUMBER()
- partition by the grouping dimension
- order by the requested ranking metric
- filter using rn <= N


21. NEVER solve a missing metric by
replacing it with NULL.


22. NEVER solve a missing metric by
replacing it with a text explanation.


23. The corrected SQL MUST contain every
requested planner metric.


24. Every requested metric alias MUST
match the planner metric name exactly.


25. NEVER rename:

revenue_contribution_percentage

to:

percentage_contribution

or:

contribution_percentage


26. If a derived metric exists in
AVAILABLE DERIVED METRICS, calculate it
even if the previous SQL used a placeholder.


27. If a derived metric requires another
aggregation level, create the required
CTE/subquery instead of using NULL.


28. The final SELECT must contain a
real expression for every requested metric.


29. Verify the final SQL against the
planner_output before returning it.


30. Return ONLY corrected SQL.


==================================================
AVAILABLE BUSINESS METRICS
==================================================

{METRICS}


==================================================
AVAILABLE DERIVED METRICS
==================================================

{DERIVED_METRICS}


==================================================
SCHEMA + GRAPH CONTEXT
==================================================

{schema}


==================================================
USER QUESTION
==================================================

{query}


==================================================
FAILED SQL
==================================================

{sql}


==================================================
ERROR
==================================================

{error}


==================================================
FINAL CORRECTION CHECK
==================================================

Planner metrics:

{planner_output.get("metrics", [])}

Planner metric types:

{planner_output.get("metric_types", {})}

Before returning:

- Every planner metric must exist
  in final SELECT.

- Every alias must exactly match
  planner metric name.

- Every derived metric must have
  a real formula if defined.

- No NULL placeholder.

- No text placeholder.

- No alternative metric name.

- No invented physical column.

- No invented join.

- Correct aggregation level.

- Correct ranking.

- Correct top-N filtering.

Return ONLY corrected MySQL SQL.


==================================================
FIXED MYSQL SQL
==================================================
"""

    response = llm.invoke(
        prompt
    )

    fixed_sql = response.content.strip()

    return clean_sql(fixed_sql)