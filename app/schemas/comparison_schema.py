from pydantic import BaseModel


class ComparisonRequest(BaseModel):
    document1_id: int
    document2_id: int