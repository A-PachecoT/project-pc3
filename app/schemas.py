from datetime import date
from pydantic import BaseModel, Field


class PromotionSchema(BaseModel):
    """Pydantic schema for validating promotion creation form data."""

    name: str
    discount_percent: float = Field(
        ..., gt=0, lt=100, description="Discount must be between 0 and 100."
    )
    start_date: date
    end_date: date
