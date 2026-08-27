from pydantic import BaseModel
from typing import Optional


class ClarificationDecision(
    BaseModel
):

    # ==========================
    # INTENT
    # ==========================
    # Determines what type of
    # request the user made.
    #
    # analytics:
    #   Database / analytical request
    #
    # conversation:
    #   Normal chat / non-database request
    # ==========================
    intent: str


    # ==========================
    # CURRENT STATUS
    # ==========================
    status: str


    # ==========================
    # ORIGINAL QUERY
    # ==========================
    query: str


    # ==========================
    # CLARIFICATION PROMPT
    # ==========================
    clarification_question: Optional[
        str
    ] = None


    # ==========================
    # USER ANSWER TO CLARIFICATION
    # ==========================
    clarification_response: Optional[
        str
    ] = None


    # ==========================
    # MERGED QUERY AFTER HITL
    # ==========================
    resolved_query: Optional[
        str
    ] = None