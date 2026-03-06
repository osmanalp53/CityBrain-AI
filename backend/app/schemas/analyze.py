from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    city: str = Field(default="ankara")
    radius_m: int = Field(default=800, ge=100, le=5000)
    h3_res: int = Field(default=7, ge=5, le=10)


class WorstCell(BaseModel):
    h3: str
    score: float | int | None = None
    park_score: float | int | None = None
    metro_score: float | int | None = None
    hospital_score: float | int | None = None
    d_park: float | int | None = None
    d_metro: float | int | None = None
    d_hospital: float | int | None = None


class ParkRecommendation(BaseModel):
    h3: str
    lat: float
    lon: float
    score: float | int | None = None
    d_park: float | int | None = None
    d_metro: float | int | None = None
    d_hospital: float | int | None = None
    park_score: float | int | None = None
    metro_score: float | int | None = None
    hospital_score: float | int | None = None
    reason: str


class SummaryMetrics(BaseModel):
    avg_d_park: float | int | None = None
    avg_d_metro: float | int | None = None
    avg_d_hospital: float | int | None = None

    avg_park_score: float | int | None = None
    avg_metro_score: float | int | None = None
    avg_hospital_score: float | int | None = None
    avg_urban_score: float | int | None = None

    bad_access_cell_count: int


class AnalyzeResponse(BaseModel):
    city: str
    radius_m: int
    h3_res: int
    cell_count: int

    summary: SummaryMetrics

    worst_cells: list[WorstCell]
    park_recommendations: list[ParkRecommendation]


class RecommendationsResponse(BaseModel):
    recommendation_type: str
    city: str
    radius_m: int
    h3_res: int
    top_k: int
    items: list[ParkRecommendation]