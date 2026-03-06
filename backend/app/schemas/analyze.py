from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    city: str = Field(default="ankara")
    radius_m: int = Field(default=800, ge=100, le=5000)
    h3_res: int = Field(default=7, ge=5, le=10)