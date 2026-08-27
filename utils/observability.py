"""
Request-level and LLM observability utilities.

Responsibilities:
    - Create request observability context
    - Track request start/end time
    - Calculate real end-to-end latency
    - Track request status
    - Track errors
    - Record individual LLM calls
    - Aggregate token usage
    - Provide request-level metadata

The module is intentionally provider-independent.

Expected request lifecycle:

    create_request_observability()
            ↓
    initialize_request_timer()
            ↓
        workflow
            ↓
    finalize_request_observability()
            ↓
        completed / error
"""

import time
import uuid

from datetime import datetime, timezone
from typing import Any


# ============================================================
# REQUEST OBSERVABILITY
# ============================================================


def create_request_observability() -> dict:
    """
    Create a fresh observability object for one user request.

    The request starts in the `running` state.

    Returns:
        dict: Request-level observability context.
    """

    now = datetime.now(
        timezone.utc
    )

    observability = {

        # ----------------------------------------------------
        # REQUEST IDENTIFIERS
        # ----------------------------------------------------

        "request_id": str(
            uuid.uuid4()
        ),

        "trace_id": str(
            uuid.uuid4()
        ),

        # ----------------------------------------------------
        # REQUEST TIMING
        # ----------------------------------------------------

        "timestamp": now.isoformat(),

        "started_at": None,

        "finished_at": None,

        "total_latency_ms": 0.0,

        # ----------------------------------------------------
        # REQUEST STATUS
        # ----------------------------------------------------

        "status": "running",

        "error": None,

        "errors": [],

        # ----------------------------------------------------
        # LLM OBSERVABILITY
        # ----------------------------------------------------

        "llm_calls": [],

        "total_llm_calls": 0,

        "total_input_tokens": 0,

        "total_output_tokens": 0,

        "total_tokens": 0,

        # ----------------------------------------------------
        # INTERNAL TIMER
        #
        # This is deliberately kept separate from the
        # human-readable timestamp.
        #
        # perf_counter() is appropriate for duration
        # measurement.
        # ----------------------------------------------------

        "_start_perf_counter": None
    }

    return observability


# ============================================================
# INITIALIZE REQUEST TIMER
# ============================================================


def initialize_request_timer(
    observability: dict
) -> dict:
    """
    Start the end-to-end request timer.

    This must be called immediately after creating the
    observability context.

    Args:
        observability: Request observability dictionary.

    Returns:
        The same observability dictionary.
    """

    # --------------------------------------------------------
    # HIGH-RESOLUTION TIMER
    # --------------------------------------------------------

    observability[
        "_start_perf_counter"
    ] = time.perf_counter()


    # --------------------------------------------------------
    # HUMAN-READABLE START TIME
    # --------------------------------------------------------

    observability[
        "started_at"
    ] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    # --------------------------------------------------------
    # RESET REQUEST STATE
    # --------------------------------------------------------

    observability[
        "finished_at"
    ] = None

    observability[
        "total_latency_ms"
    ] = 0.0

    observability[
        "status"
    ] = "running"

    observability[
        "error"
    ] = None

    return observability


# ============================================================
# FINALIZE REQUEST OBSERVABILITY
# ============================================================


def finalize_request_observability(
    observability: dict,
    status: str = "completed",
    error: str | None = None
) -> dict:
    """
    Finalize request-level observability.

    Calculates the actual end-to-end request latency and
    changes the request status from `running` to either
    `completed` or `error`.

    Args:
        observability:
            Request observability dictionary.

        status:
            Final request status.
            Normally:
                - completed
                - error

        error:
            Optional error message.

    Returns:
        The finalized observability dictionary.
    """

    # --------------------------------------------------------
    # FINISH TIME
    # --------------------------------------------------------

    finished_at = datetime.now(
        timezone.utc
    )

    observability[
        "finished_at"
    ] = finished_at.isoformat()


    # --------------------------------------------------------
    # ACTUAL END-TO-END LATENCY
    # --------------------------------------------------------

    start_perf_counter = (
        observability.get(
            "_start_perf_counter"
        )
    )

    if start_perf_counter is not None:

        elapsed_seconds = (
            time.perf_counter()
            -
            start_perf_counter
        )

        observability[
            "total_latency_ms"
        ] = round(
            elapsed_seconds * 1000,
            2
        )


    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    if status not in {
        "completed",
        "error"
    }:
        status = "error"


    observability[
        "status"
    ] = status


    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    observability[
        "error"
    ] = error


    # --------------------------------------------------------
    # CLEAN INTERNAL TIMER
    #
    # We don't need to expose perf_counter state in the
    # final observability object.
    # --------------------------------------------------------

    observability.pop(
        "_start_perf_counter",
        None
    )


    return observability


# ============================================================
# RECORD OBSERVABILITY ERROR
# ============================================================


def record_observability_error(
    observability: dict,
    error: str,
    error_type: str | None = None
) -> None:
    """
    Record an observability/workflow error.

    This does not automatically finalize the request.

    Args:
        observability: Request observability dictionary.
        error: Error description.
        error_type: Optional error class/type.
    """

    if observability is None:
        return


    error_record = {

        "error": error,

        "error_type": (
            error_type
            or "UnknownError"
        ),

        "timestamp": (
            datetime.now(
                timezone.utc
            ).isoformat()
        )
    }


    observability.setdefault(
        "errors",
        []
    ).append(
        error_record
    )


# ============================================================
# RECORD LLM CALL
# ============================================================


def record_llm_call(
    observability: dict | None,
    call: dict
) -> None:
    """
    Record one LLM call.

    Expected call fields may include:

        node
        purpose
        provider
        model
        operation
        latency_ms
        status
        input_tokens
        output_tokens
        total_tokens
        error
        caller
        caller_chain

    Token values are only recorded when available.

    Args:
        observability:
            Current request observability context.

        call:
            LLM call information.
    """

    # --------------------------------------------------------
    # NO ACTIVE REQUEST
    # --------------------------------------------------------

    if observability is None:
        return


    # --------------------------------------------------------
    # SAFE TOKEN VALUES
    # --------------------------------------------------------

    input_tokens = (
        call.get(
            "input_tokens"
        )
    )

    output_tokens = (
        call.get(
            "output_tokens"
        )
    )

    total_tokens = (
        call.get(
            "total_tokens"
        )
    )


    # --------------------------------------------------------
    # NORMALIZE MISSING TOKEN DATA
    #
    # Your current LLM implementation historically uses 0
    # when token information isn't available, so preserve
    # that behavior here.
    # --------------------------------------------------------

    if input_tokens is None:
        input_tokens = 0

    if output_tokens is None:
        output_tokens = 0

    if total_tokens is None:

        total_tokens = (
            input_tokens
            +
            output_tokens
        )


    # --------------------------------------------------------
    # CREATE CLEAN CALL RECORD
    # --------------------------------------------------------

    call_record = {

        "node": call.get(
            "node",
            "unknown"
        ),

        "purpose": call.get(
            "purpose",
            "unknown"
        ),

        "provider": call.get(
            "provider",
            "unknown"
        ),

        "model": call.get(
            "model",
            "unknown"
        ),

        "operation": call.get(
            "operation",
            "invoke"
        ),

        "latency_ms": call.get(
            "latency_ms",
            0.0
        ),

        "status": call.get(
            "status",
            "unknown"
        ),

        "input_tokens": input_tokens,

        "output_tokens": output_tokens,

        "total_tokens": total_tokens
    }


    # --------------------------------------------------------
    # OPTIONAL CALLER INFORMATION
    # --------------------------------------------------------

    if call.get(
        "caller"
    ) is not None:

        call_record[
            "caller"
        ] = call[
            "caller"
        ]


    if call.get(
        "caller_chain"
    ) is not None:

        call_record[
            "caller_chain"
        ] = call[
            "caller_chain"
        ]


    # --------------------------------------------------------
    # OPTIONAL ERROR
    # --------------------------------------------------------

    if call.get(
        "error"
    ):

        call_record[
            "error"
        ] = call[
            "error"
        ]


    # --------------------------------------------------------
    # APPEND CALL
    # --------------------------------------------------------

    observability.setdefault(
        "llm_calls",
        []
    ).append(
        call_record
    )


    # --------------------------------------------------------
    # UPDATE AGGREGATES
    # --------------------------------------------------------

    observability[
        "total_llm_calls"
    ] = len(
        observability[
            "llm_calls"
        ]
    )


    observability[
        "total_input_tokens"
    ] = (
        observability.get(
            "total_input_tokens",
            0
        )
        +
        input_tokens
    )


    observability[
        "total_output_tokens"
    ] = (
        observability.get(
            "total_output_tokens",
            0
        )
        +
        output_tokens
    )


    observability[
        "total_tokens"
    ] = (
        observability.get(
            "total_tokens",
            0
        )
        +
        total_tokens
    )


# ============================================================
# GET TOTAL LLM LATENCY
# ============================================================


def get_total_llm_latency(
    observability: dict | None
) -> float:
    """
    Calculate the sum of recorded LLM call latency.

    This is NOT the same as end-to-end request latency.

    Returns:
        Total recorded LLM latency in milliseconds.
    """

    if observability is None:
        return 0.0


    total = 0.0


    for call in observability.get(
        "llm_calls",
        []
    ):

        latency = call.get(
            "latency_ms",
            0.0
        )


        if isinstance(
            latency,
            (int, float)
        ):

            total += latency


    return round(
        total,
        2
    )


# ============================================================
# GET REQUEST LATENCY
# ============================================================


def get_request_latency_ms(
    observability: dict | None
) -> float:
    """
    Return the finalized end-to-end request latency.

    Returns:
        Request latency in milliseconds.
    """

    if observability is None:
        return 0.0


    latency = observability.get(
        "total_latency_ms",
        0.0
    )


    if not isinstance(
        latency,
        (int, float)
    ):
        return 0.0


    return round(
        latency,
        2
    )


# ============================================================
# GET REQUEST STATUS
# ============================================================


def get_request_status(
    observability: dict | None
) -> str:
    """
    Return the current request status.
    """

    if observability is None:
        return "unknown"


    return observability.get(
        "status",
        "unknown"
    )


# ============================================================
# FINALIZE SUCCESS
# ============================================================


def finalize_request_success(
    observability: dict
) -> dict:
    """
    Convenience helper for successful requests.
    """

    return finalize_request_observability(
        observability,
        status="completed"
    )


# ============================================================
# FINALIZE ERROR
# ============================================================


def finalize_request_error(
    observability: dict,
    error: Exception | str
) -> dict:
    """
    Convenience helper for failed requests.
    """

    error_message = str(
        error
    )


    record_observability_error(
        observability,
        error_message,
        type(error).__name__
        if isinstance(
            error,
            Exception
        )
        else "Error"
    )


    return finalize_request_observability(
        observability,
        status="error",
        error=error_message
    )