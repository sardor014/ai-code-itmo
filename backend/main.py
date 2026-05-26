from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware
from typing import Any

app = FastAPI(title="Real Estate Evaluation Service")

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ApartmentParams(BaseModel):
    floor: int = Field(..., gt=0)
    total_floors: int = Field(..., gt=0)
    rooms: int = Field(..., gt=0)
    total_area: float = Field(..., gt=0)
    living_area: float = Field(..., gt=0)

    @field_validator("total_floors")
    @classmethod
    def validate_floors(cls, v: int, info: Any) -> int:
        if "floor" in info.data and v < info.data["floor"]:
            raise ValueError("Total floors cannot be less than current floor")
        return v

    @field_validator("living_area")
    @classmethod
    def validate_area(cls, v: float, info: Any) -> float:
        if "total_area" in info.data and v >= info.data["total_area"]:
            raise ValueError("Living area must be less than total area")
        return v

@app.post("/calculate")
async def calculate_price(params: ApartmentParams):
    # Mock heuristic formula
    base_rate = 50000
    price = (params.total_area * base_rate) + (params.rooms * 100000) - (params.floor * 2000)
    price_per_meter = price / params.total_area
    
    return {
        "price_per_meter": round(price_per_meter, 2),
        "total_price": round(price, 2)
    }
