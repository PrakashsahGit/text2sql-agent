"""Minimal Gemini connectivity test.

Run after creating .env and setting GOOGLE_API_KEY:
    python test_gemini.py
"""

from utils.llm import llm


if __name__ == "__main__":
    response = llm.invoke(
        "Reply with exactly: Gemini connection successful."
    )
    print(response.content.strip())
