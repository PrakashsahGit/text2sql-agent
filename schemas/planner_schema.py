from typing import Dict, List, Optional

from pydantic import BaseModel


# ===================================
# PLANNER OUTPUT
# ===================================
class PlannerOutput(BaseModel):

    intent: str

    metrics: List[str]
    # METRIC TYPES
    # ===================================
    metric_types: Dict[str, str]

    dimensions: List[str]

    filters: List[str]

    time_context: Optional[str] = None

    requires_grouping: bool

    requires_aggregation: bool