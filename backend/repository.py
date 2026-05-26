from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta, timezone
from .models import Calculation

class CalculationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_recent_calculation(
        self, 
        floor: int, 
        total_floors: int, 
        rooms: int, 
        total_area: float, 
        living_area: float
    ):
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        query = select(Calculation).where(
            and_(
                Calculation.floor == floor,
                Calculation.total_floors == total_floors,
                Calculation.rooms == rooms,
                Calculation.total_area == total_area,
                Calculation.living_area == living_area,
                Calculation.created_at >= thirty_days_ago
            )
        ).order_by(Calculation.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().first()

    async def save_calculation(self, calculation_data: dict):
        new_calc = Calculation(**calculation_data)
        self.session.add(new_calc)
        await self.session.commit()
        await self.session.refresh(new_calc)
        return new_calc
