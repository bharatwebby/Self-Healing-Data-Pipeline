from pydantic import BaseModel

class TargetRecord(BaseModel):
    """
    This is the ONE shape our internal system ever wants to see,
    no matter what shape the source is currently sending.
    """
    external_id: int
    display_name: str
    amount_cents: int