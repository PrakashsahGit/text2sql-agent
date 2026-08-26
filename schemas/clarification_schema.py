from pydantic import BaseModel
from typing import Optional


class ClarificationDecision(
    BaseModel
):

    # ==========================
    # current status
    # ==========================
    status: str


    # ==========================
    # original query
    # ==========================
    query: str


    # ==========================
    # clarification prompt
    # ==========================
    clarification_question: Optional[
        str
    ] = None


    # ==========================
    # user answer to clarification
    # ==========================
    clarification_response: Optional[
        str
    ] = None


    # ==========================
    # merged query after HITL
    # ==========================
    resolved_query: Optional[
        str
    ] = None