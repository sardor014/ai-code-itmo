from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from .database import init_db, get_db
from .repository import CalculationRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    await init_db()
    yield

app = FastAPI(title="Real Estate Evaluation Service", lifespan=lifespan)

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

def calculate_heuristic(params: ApartmentParams):
    # Mock heuristic formula
    base_rate = 50000
    total_price = (params.total_area * base_rate) + (params.rooms * 100000) - (params.floor * 2000)
    price_per_meter = total_price / params.total_area
    return round(price_per_meter, 2), round(total_price, 2)

@app.post("/calculate")
async def calculate_price(params: ApartmentParams, db: AsyncSession = Depends(get_db)):
    repo = CalculationRepository(db)
    
    # 1. Check for recent calculation in DB
    existing_calc = await repo.find_recent_calculation(
        floor=params.floor,
        total_floors=params.total_floors,
        rooms=params.rooms,
        total_area=params.total_area,
        living_area=params.living_area
    )
    
    if existing_calc:
        return {
            "price_per_meter": existing_calc.price_per_meter,
            "total_price": existing_calc.total_price,
            "cached": True,
            "cached_at": existing_calc.created_at
        }
    
    # 2. If not found or older than 30 days, calculate new
    price_per_meter, total_price = calculate_heuristic(params)
    
    # 3. Save to DB
    calc_data = params.model_dump()
    calc_data.update({
        "price_per_meter": price_per_meter,
        "total_price": total_price
    })
    
    await repo.save_calculation(calc_data)
    
    return {
        "price_per_meter": price_per_meter,
        "total_price": total_price,
        "cached": False
    }
