import pytest
import allure
from httpx import AsyncClient
from backend.main import app

@allure.feature("Расчет стоимости")
@allure.story("API тесты")
@pytest.mark.asyncio
class TestApi:
    
    @allure.title("Позитивный сценарий: Стандартная квартира")
    async def test_calculate_standard(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with allure.step("Отправка запроса с валидными данными"):
                response = await ac.post("/calculate", json={
                    "floor": 5,
                    "total_floors": 10,
                    "rooms": 2,
                    "total_area": 50,
                    "living_area": 30
                })
            assert response.status_code == 200
            data = response.json()
            assert data["price_per_meter"] > 0

    @allure.title("Граничные значения: Первый и последний этаж")
    @pytest.mark.parametrize("floor,total", [(1, 10), (10, 10)])
    async def test_boundary_floors(self, floor, total):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/calculate", json={
                "floor": floor,
                "total_floors": total,
                "rooms": 1,
                "total_area": 30,
                "living_area": 15
            })
            assert response.status_code == 200

    @allure.title("Негативный сценарий: Этаж больше этажности дома")
    async def test_invalid_floor_logic(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/calculate", json={
                "floor": 11,
                "total_floors": 10,
                "rooms": 2,
                "total_area": 50,
                "living_area": 30
            })
            assert response.status_code == 422
            assert "Total floors cannot be less than current floor" in response.text

    @allure.title("Негативный сценарий: Отрицательные значения")
    async def test_negative_values(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/calculate", json={
                "floor": 5,
                "total_floors": 10,
                "rooms": 2,
                "total_area": -50,
                "living_area": 30
            })
            assert response.status_code == 422

    @allure.title("Негативный сценарий: Жилая площадь больше общей")
    async def test_living_area_logic(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/calculate", json={
                "floor": 5,
                "total_floors": 10,
                "rooms": 2,
                "total_area": 50,
                "living_area": 60
            })
            assert response.status_code == 422
            assert "Living area must be less than total area" in response.text
