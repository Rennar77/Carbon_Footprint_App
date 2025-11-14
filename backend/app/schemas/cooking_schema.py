from pydantic import BaseModel, Field

class CookingLog(BaseModel):
    type: str = Field(..., description="Fuel type: charcoal or lpg")
    kg_used: float = Field(..., gt=0, description="Amount used in kg")
