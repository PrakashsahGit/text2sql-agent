from utils.llm import llm




# -----------------------------------
# ANALYZE DATA
# -----------------------------------
def analyze_data(query: str, data: list):

    prompt = f"""
You are an expert AI data analyst.

Your task:
Generate concise, data-driven insights
from SQL query results.

IMPORTANT RULES:

1. ONLY use information present in data

2. NEVER hallucinate business reasons

3. NEVER invent market explanations

4. Focus on:
- rankings
- trends
- comparisons
- totals
- averages
- patterns

5. If one row exists:
briefly explain the result

6. If multiple rows exist:
compare values and highlight trends

7. Mention numerical values whenever possible

8. Keep response concise

9. Use professional analytics language

10. Use bullet points


USER QUESTION:
{query}


QUERY RESULT:
{data}


PROFESSIONAL ANALYTICS INSIGHTS:
"""

    response = llm.invoke(prompt)

    return response.content.strip()