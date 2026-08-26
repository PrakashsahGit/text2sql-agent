from utils.llm import llm




# ===================================
# SQL QUERY CLASSIFIER
# ===================================
def is_sql_query(query: str):

    prompt = f"""
You are a query intent classifier.

Your task:
Determine whether the user query
requires database retrieval / SQL analysis.


RETURN:
ONLY one word:

YES
or
NO


CLASSIFY AS YES IF QUERY INVOLVES:
- sales
- revenue
- products
- customers
- regions
- quantity
- orders
- profit
- discounts
- analytics
- trends
- counts
- totals
- aggregations
- comparisons
- metrics
- database information


CLASSIFY AS YES EVEN IF:
- grammar is poor
- wording is incomplete
- query is short


EXAMPLES:

Query:
"what is nike sales"

Output:
YES


Query:
"top customers"

Output:
YES


Query:
"how many tables are there"

Output:
YES


Query:
"compare adidas and nike revenue"

Output:
YES


CLASSIFY AS NO ONLY IF:
- greeting
- casual conversation
- jokes
- opinions
- non-database chat


EXAMPLES:

Query:
"hello"

Output:
NO


Query:
"how are you"

Output:
NO


USER QUERY:
{query}
"""


    response = llm.invoke(prompt)

    answer = (
        response.content
        .strip()
        .upper()
    )


    return answer == "YES"