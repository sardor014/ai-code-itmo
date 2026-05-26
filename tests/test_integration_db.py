import pytest
import allure
from httpx import AsyncClient
from backend.main import app
from backend.models import Calculation
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

@allure.feature("БД Интеграция")
@pytest.mark.asyncio
class TestDbIntegration:
    
    async def test_calculation_caching_logic(self, db_session):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            params = {
                "floor": 5,
                "total_floors": 10,
                "rooms": 2,
                "total_area": 50,
                "living_area": 30
            }

            # 1. First request - should NOT be cached
            with allure.step("Первый запрос: сохранение в БД"):
                response = await ac.post("/calculate", json=params)
                assert response.status_code == 200
                assert response.json()["cached"] is False
            
            # 2. Second request (immediate) - SHOULD be cached
            with allure.step("Второй запрос (сразу): получение из кэша"):
                response = await ac.post("/calculate", json=params)
                assert response.status_code == 200
                assert response.json()["cached"] is True

    async def test_recalculation_after_30_days(self, db_session):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            params = {
                "floor": 3,
                "total_floors": 5,
                "rooms": 1,
                "total_area": 40,
                "living_area": 20
            }

            # Pre-insert an old calculation (31 days ago)
            old_date = datetime.now(timezone.utc) - timedelta(days=31)
            old_calc = Calculation(
                **params,
                price_per_meter=100.0,
                total_price=4000.0,
                created_at=old_date
            )
            db_session.add(old_calc)
            await db_session.commit()

            with allure.step("Запрос через 31 день: должен быть пересчет"):
                response = await ac.post("/calculate", json=params)
                assert response.status_code == 200
                assert response.json()["cached"] is False
                # Verify it's a new price from our heuristic, not the 100.0 we manualy inserted
                assert response.json()["price_per_meter"] != 100.0
