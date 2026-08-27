"""
Centralized, lazy, provider-independent LLM client.

Supported providers:
    - Gemini
    - Groq

Provider and model are controlled through .env:

    LLM_PROVIDER=gemini
    LLM_MODEL=gemini-2.5-flash

or:

    LLM_PROVIDER=groq
    LLM_MODEL=openai/gpt-oss-120b

Observability records:

    - provider
    - model
    - node
    - purpose
    - operation
    - latency
    - input tokens
    - output tokens
    - total tokens
    - success / error
    - caller
    - caller chain
"""


# ===================================
# IMPORTS
# ===================================

import inspect
import os
import time

from contextvars import ContextVar
from typing import Any

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from langchain_groq import (
    ChatGroq
)

from utils.observability import (
    record_llm_call
)


# ===================================
# LOAD ENVIRONMENT
# ===================================

load_dotenv()


# ===================================
# REQUEST-SCOPED OBSERVABILITY
# ===================================

_observability_context: ContextVar[
    dict | None
] = ContextVar(

    "observability_context",

    default=None
)


# ===================================
# SET OBSERVABILITY CONTEXT
# ===================================

def set_observability_context(
    observability: dict | None
):

    return _observability_context.set(
        observability
    )


# ===================================
# GET OBSERVABILITY CONTEXT
# ===================================

def get_observability_context():

    return _observability_context.get()


# ===================================
# RESET OBSERVABILITY CONTEXT
# ===================================

def reset_observability_context(
    token
):

    _observability_context.reset(
        token
    )


# ===================================
# OBSERVABLE LLM
# ===================================

class ObservableLLM:
    """
    Central LLM gateway.

    The rest of the application uses:

        llm.invoke(...)

    or:

        llm.with_structured_output(...)
    """


    # ===================================
    # INITIALIZE
    # ===================================

    def __init__(self):

        # -----------------------------------
        # Provider
        # -----------------------------------

        self.provider = (

            os.getenv(
                "LLM_PROVIDER",
                "gemini"
            )
            .lower()
            .strip()
        )


        # -----------------------------------
        # Model
        # -----------------------------------

        self.model = os.getenv(
            "LLM_MODEL"
        )


        # -----------------------------------
        # Lazy client
        # -----------------------------------

        self._client = None


    # ===================================
    # LAZY CLIENT CREATION
    # ===================================

    def _get_client(self):

        if self._client is not None:

            return self._client


        # ===================================
        # GEMINI
        # ===================================

        if self.provider == "gemini":

            api_key = (

                os.getenv(
                    "GOOGLE_API_KEY"
                )

                or

                os.getenv(
                    "GEMINI_API_KEY"
                )
            )


            if not api_key:

                raise RuntimeError(

                    "Missing Gemini API key. "

                    "Set GOOGLE_API_KEY or "
                    "GEMINI_API_KEY in .env."
                )


            if not self.model:

                self.model = (
                    "gemini-2.5-flash"
                )


            self._client = (

                ChatGoogleGenerativeAI(

                    model=self.model,

                    google_api_key=api_key,

                    temperature=0
                )
            )


        # ===================================
        # GROQ
        # ===================================

        elif self.provider == "groq":

            api_key = os.getenv(
                "GROQ_API_KEY"
            )


            if not api_key:

                raise RuntimeError(

                    "Missing Groq API key. "

                    "Set GROQ_API_KEY in .env."
                )


            if not self.model:

                self.model = (
                    "openai/gpt-oss-120b"
                )


            self._client = (

                ChatGroq(

                    model=self.model,

                    api_key=api_key,

                    temperature=1,

                    max_tokens=2048,

                    reasoning_effort="medium"
                )
            )


        # ===================================
        # INVALID PROVIDER
        # ===================================

        else:

            raise ValueError(

                "Unsupported LLM_PROVIDER: "

                f"{self.provider}. "

                "Supported providers are: "
                "gemini, groq."
            )


        return self._client


    # ===================================
    # DETECT LLM PURPOSE + CALLER
    # ===================================

    def _detect_purpose(self) -> dict:
        """
        Inspect the runtime call stack.

        This is temporarily used to identify
        exactly which application function
        triggered an LLM call.

        It records:

            node
            purpose
            caller
            caller_chain
        """

        caller_chain = []


        try:

            stack = inspect.stack()


            for frame_info in stack:

                filename = os.path.basename(
                    frame_info.filename
                )

                function = (
                    frame_info.function
                )

                line_number = (
                    frame_info.lineno
                )


                # -----------------------------------
                # Ignore this LLM wrapper
                # -----------------------------------

                if filename == "llm.py":

                    continue


                caller_chain.append({

                    "file":
                    filename,

                    "function":
                    function,

                    "line":
                    line_number
                })


            # ===================================
            # CLARIFICATION
            # ===================================

            for caller in caller_chain:

                filename = (
                    caller["file"]
                    .lower()
                )


                if (
                    "clarification_loop"
                    in filename
                ):

                    return {

                        "node":
                        "clarification",

                        "purpose":
                        "query_clarification",

                        "caller":
                        caller,

                        "caller_chain":
                        caller_chain[:10]
                    }


            # ===================================
            # PLANNER
            # ===================================

            for caller in caller_chain:

                filename = (
                    caller["file"]
                    .lower()
                )


                if (
                    "planner_node"
                    in filename
                ):

                    return {

                        "node":
                        "planner",

                        "purpose":
                        "query_planning",

                        "caller":
                        caller,

                        "caller_chain":
                        caller_chain[:10]
                    }


            # ===================================
            # SQL GENERATOR
            # ===================================

            for caller in caller_chain:

                filename = (
                    caller["file"]
                    .lower()
                )


                if (
                    "sql_generator"
                    in filename
                ):

                    return {

                        "node":
                        "sql",

                        "purpose":
                        "sql_generation",

                        "caller":
                        caller,

                        "caller_chain":
                        caller_chain[:10]
                    }


            # ===================================
            # ANALYZER
            # ===================================

            for caller in caller_chain:

                filename = (
                    caller["file"]
                    .lower()
                )


                if (
                    "analyzer"
                    in filename
                ):

                    return {

                        "node":
                        "reasoning",

                        "purpose":
                        "analytics_reasoning",

                        "caller":
                        caller,

                        "caller_chain":
                        caller_chain[:10]
                    }


            # ===================================
            # SQL NODE
            # ===================================

            for caller in caller_chain:

                filename = (
                    caller["file"]
                    .lower()
                )


                if (
                    "sql_node"
                    in filename
                ):

                    return {

                        "node":
                        "sql",

                        "purpose":
                        "unidentified_sql_call",

                        "caller":
                        caller,

                        "caller_chain":
                        caller_chain[:10]
                    }


            # ===================================
            # RETRIEVAL NODE
            # ===================================

            for caller in caller_chain:

                filename = (
                    caller["file"]
                    .lower()
                )


                if (
                    "retrieval_node"
                    in filename
                ):

                    return {

                        "node":
                        "retrieval",

                        "purpose":
                        "semantic_retrieval",

                        "caller":
                        caller,

                        "caller_chain":
                        caller_chain[:10]
                    }


        except Exception:

            pass


        # ===================================
        # UNKNOWN
        # ===================================

        return {

            "node":
            "unknown",

            "purpose":
            "unknown",

            "caller":
            caller_chain[0]
            if caller_chain
            else None,

            "caller_chain":
            caller_chain[:10]
        }


    # ===================================
    # NORMAL INVOKE
    # ===================================

    def invoke(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:

        start_time = (
            time.perf_counter()
        )


        try:

            response = (

                self._get_client().invoke(

                    *args,

                    **kwargs
                )
            )


            latency_ms = round(

                (
                    time.perf_counter()
                    -
                    start_time
                )
                * 1000,

                2
            )


            # -----------------------------------
            # Extract usage
            # -----------------------------------

            usage = (

                self._extract_usage(
                    response
                )
            )


            # -----------------------------------
            # Record successful call
            # -----------------------------------

            self._record(

                operation=
                "invoke",

                latency_ms=
                latency_ms,

                status=
                "success",

                usage=
                usage
            )


            return response


        except Exception as e:

            latency_ms = round(

                (
                    time.perf_counter()
                    -
                    start_time
                )
                * 1000,

                2
            )


            self._record(

                operation=
                "invoke",

                latency_ms=
                latency_ms,

                status=
                "error",

                usage={

                    "input_tokens":
                    0,

                    "output_tokens":
                    0,

                    "total_tokens":
                    0
                },

                error=
                str(e)
            )


            raise


    # ===================================
    # STRUCTURED OUTPUT
    # ===================================

    def with_structured_output(
        self,
        *args: Any,
        **kwargs: Any
    ):

        # -----------------------------------
        # IMPORTANT
        # -----------------------------------
        # Ask LangChain to preserve the
        # original AIMessage.
        #
        # This allows us to extract:
        #
        #   usage_metadata
        #   response_metadata
        #
        # while still returning the parsed
        # Pydantic object to the application.
        # -----------------------------------

        kwargs["include_raw"] = True


        structured_client = (

            self._get_client()
            .with_structured_output(

                *args,

                **kwargs
            )
        )


        return ObservableStructuredLLM(

            client=
            structured_client,

            parent=
            self
        )


    # ===================================
    # RECORD LLM CALL
    # ===================================

    def _record(
        self,
        operation: str,
        latency_ms: float,
        status: str,
        usage: dict,
        error: str | None = None
    ):

        observability = (

            get_observability_context()
        )


        # ===================================
        # NO ACTIVE REQUEST
        # ===================================

        if observability is None:

            return


        # ===================================
        # DETECT PURPOSE
        # ===================================

        purpose_info = (

            self._detect_purpose()
        )


        # ===================================
        # BUILD CALL RECORD
        # ===================================

        call = {

            "node":
            purpose_info.get(
                "node",
                "unknown"
            ),

            "purpose":
            purpose_info.get(
                "purpose",
                "unknown"
            ),

            "provider":
            self.provider,

            "model":
            self.model,

            "operation":
            operation,

            "latency_ms":
            latency_ms,

            "status":
            status,

            "input_tokens":
            usage.get(
                "input_tokens",
                0
            ),

            "output_tokens":
            usage.get(
                "output_tokens",
                0
            ),

            "total_tokens":
            usage.get(
                "total_tokens",
                0
            )
        }


        # ===================================
        # CALLER DEBUGGING
        # ===================================

        caller = purpose_info.get(
            "caller"
        )


        caller_chain = (
            purpose_info.get(
                "caller_chain"
            )
        )


        if caller:

            call["caller"] = caller


        if caller_chain:

            call[
                "caller_chain"
            ] = caller_chain


        # ===================================
        # ERROR
        # ===================================

        if error:

            call["error"] = error


        # ===================================
        # SAVE OBSERVABILITY
        # ===================================

        record_llm_call(

            observability,

            call
        )


    # ===================================
    # EXTRACT TOKEN USAGE
    # ===================================

    def _extract_usage(
        self,
        response: Any
    ) -> dict:

        input_tokens = 0

        output_tokens = 0

        total_tokens = 0


        # ===================================
        # LANGCHAIN USAGE METADATA
        # ===================================

        usage_metadata = getattr(

            response,

            "usage_metadata",

            None
        )


        if isinstance(
            usage_metadata,
            dict
        ):

            input_tokens = (

                usage_metadata.get(
                    "input_tokens"
                )

                or

                usage_metadata.get(
                    "prompt_tokens"
                )

                or

                0
            )


            output_tokens = (

                usage_metadata.get(
                    "output_tokens"
                )

                or

                usage_metadata.get(
                    "completion_tokens"
                )

                or

                0
            )


            total_tokens = (

                usage_metadata.get(
                    "total_tokens"
                )

                or

                0
            )


        # ===================================
        # RESPONSE METADATA
        # ===================================

        response_metadata = getattr(

            response,

            "response_metadata",

            None
        )


        if isinstance(
            response_metadata,
            dict
        ):

            token_usage = (

                response_metadata.get(
                    "token_usage"
                )

                or

                response_metadata.get(
                    "usage"
                )
            )


            if isinstance(
                token_usage,
                dict
            ):

                input_tokens = (

                    token_usage.get(
                        "prompt_tokens"
                    )

                    or

                    token_usage.get(
                        "input_tokens"
                    )

                    or

                    input_tokens
                )


                output_tokens = (

                    token_usage.get(
                        "completion_tokens"
                    )

                    or

                    token_usage.get(
                        "output_tokens"
                    )

                    or

                    output_tokens
                )


                total_tokens = (

                    token_usage.get(
                        "total_tokens"
                    )

                    or

                    total_tokens
                )


        # ===================================
        # CALCULATE TOTAL
        # ===================================

        if not total_tokens:

            total_tokens = (

                input_tokens
                +
                output_tokens
            )


        return {

            "input_tokens":
            int(
                input_tokens or 0
            ),

            "output_tokens":
            int(
                output_tokens or 0
            ),

            "total_tokens":
            int(
                total_tokens or 0
            )
        }


# ===================================
# STRUCTURED OUTPUT WRAPPER
# ===================================

class ObservableStructuredLLM:
    """
    Wrapper around structured-output calls.

    Supports:

        llm.with_structured_output(
            SomeSchema
        ).invoke(...)
    """


    # ===================================
    # INITIALIZE
    # ===================================

    def __init__(
        self,
        client: Any,
        parent: ObservableLLM
    ):

        self.client = client

        self.parent = parent


    # ===================================
    # INVOKE
    # ===================================

    def invoke(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:

        start_time = (
            time.perf_counter()
        )


        try:

            response = (

                self.client.invoke(

                    *args,

                    **kwargs
                )
            )


            latency_ms = round(

                (
                    time.perf_counter()
                    -
                    start_time
                )
                * 1000,

                2
            )


            # ===================================
            # EXTRACT RAW AI MESSAGE
            # ===================================

            raw_response = response


            if isinstance(
                response,
                dict
            ):

                raw_response = (
                    response.get(
                        "raw"
                    )
                )


            # ===================================
            # EXTRACT TOKEN USAGE
            # ===================================

            usage = (

                self.parent._extract_usage(
                    raw_response
                )
            )


            # ===================================
            # RECORD SUCCESSFUL CALL
            # ===================================

            self.parent._record(

                operation=
                "structured_invoke",

                latency_ms=
                latency_ms,

                status=
                "success",

                usage=
                usage
            )


            # ===================================
            # RETURN PARSED OBJECT
            # ===================================

            if isinstance(
                response,
                dict
            ):

                parsed_response = (
                    response.get(
                        "parsed"
                    )
                )

                # -----------------------------------
                # If parsing failed, don't silently
                # return None.
                # -----------------------------------

                if parsed_response is None:

                    parsing_error = (
                        response.get(
                            "parsing_error"
                        )
                    )

                    if parsing_error:

                        raise parsing_error


                return parsed_response


            return response


        except Exception as e:

            latency_ms = round(

                (
                    time.perf_counter()
                    -
                    start_time
                )
                * 1000,

                2
            )


            self.parent._record(

                operation=
                "structured_invoke",

                latency_ms=
                latency_ms,

                status=
                "error",

                usage={

                    "input_tokens":
                    0,

                    "output_tokens":
                    0,

                    "total_tokens":
                    0
                },

                error=
                str(e)
            )


            raise


# ===================================
# SINGLE SHARED LLM ENTRY POINT
# ===================================

llm = ObservableLLM()