# Gemini LLM Migration

The Text-to-SQL project now uses Google Gemini through LangChain's
`ChatGoogleGenerativeAI` integration.

## Runtime model

The default model is:

`gemini-2.5-flash`

It can be changed without modifying Python code:

```env
LLM_MODEL=gemini-2.5-flash
```

## Environment

Create `.env` from `.env.example` and set:

```env
GOOGLE_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.5-flash
```

`GEMINI_API_KEY` is also accepted as a fallback by `utils/llm.py`, but
`GOOGLE_API_KEY` is the preferred variable for this LangChain integration.

## Architecture

All runtime modules continue importing the shared object:

```python
from utils.llm import llm
```

The provider is centralized in `utils/llm.py`, so these modules do not need
provider-specific code:

- planner
- SQL generation
- SQL repair
- query classification
- analytics reasoning

This preserves the existing project architecture and makes a future provider
change localized to the LLM client layer.

## Test Gemini independently

```bash
python test_gemini.py
```

Expected output:

```text
Gemini connection successful.
```

## Packages

The project keeps:

- `langchain-google-genai`
- `google-genai`

and removes the runtime Groq dependencies:

- `groq`
- `langchain-groq`

## Security

The original `.env` containing API keys is intentionally not included in the
Gemini project package. Use `.env.example` as the template and never commit
`.env` to Git.
