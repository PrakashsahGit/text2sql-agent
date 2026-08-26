# """Centralized, lazy Gemini LLM client used across the Text-to-SQL agent."""

# import os
# from typing import Any

# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()


# class LazyGeminiLLM:
#     """Lazily construct one shared Gemini chat model for the application.

#     Keeping model/provider construction here means the rest of the project can
#     continue importing ``llm`` without knowing which provider is used.
#     """

#     def __init__(self) -> None:
#         self._client: ChatGoogleGenerativeAI | None = None

#     def _get_client(self) -> ChatGoogleGenerativeAI:
#         if self._client is None:
#             api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
#             if not api_key:
#                 raise RuntimeError(
#                     "Missing Gemini API key. Set GOOGLE_API_KEY in .env."
#                 )

#             model = os.getenv("LLM_MODEL", "gemini-2.5-flash")

#             self._client = ChatGoogleGenerativeAI(
#                 model=model,
#                 google_api_key=api_key,
#                 temperature=0,
#             )

#         return self._client

#     def invoke(self, *args: Any, **kwargs: Any) -> Any:
#         return self._get_client().invoke(*args, **kwargs)

#     def with_structured_output(self, *args: Any, **kwargs: Any) -> Any:
#         return self._get_client().with_structured_output(*args, **kwargs)


# # Single shared LLM entry point used by planner, SQL generation, SQL repair,
# # query classification and analytics reasoning.
# llm = LazyGeminiLLM()




#GROQ LLM client

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set in the environment."
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=1,
    max_tokens=2048,
    reasoning_effort="medium",
)