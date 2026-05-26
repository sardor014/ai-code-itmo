import pytest
import allure
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@allure.feature("Расчет стоимости")
@allure.story("API тесты")
class TestApi:
    
    @allure.title("Позитивный сценарий: Стандартная квартира")
    def test_calculate_standard(self):
        with allure.step("Отправка запроса с валидными данными"):
            response = client.post("/calculate", json={
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
    def test_boundary_floors(self, floor, total):
        response = client.post("/calculate", json={
            "floor": floor,
            "total_floors": total,
            "rooms": 1,
            "total_area": 30,
            "living_area": 15
        })
        assert response.status_code == 200

    @allure.title("Негативный сценарий: Этаж больше этажности дома")
    def test_invalid_floor_logic(self):
        response = client.post("/calculate", json={
            "floor": 11,
            "total_floors": 10,
            "rooms": 2,
            "total_area": 50,
            "living_area": 30
        })
        assert response.status_code == 422
        assert "Total floors cannot be less than current floor" in response.text

    @allure.title("Негативный сценарий: Отрицательные значения")
    def test_negative_values(self):
        response = client.post("/calculate", json={
            "floor": 5,
            "total_floors": 10,
            "rooms": 2,
            "total_area": -50,
            "living_area": 30
        })
        assert response.status_code == 422

    @allure.title("Негативный сценарий: Жилая площадь больше общей")
    def test_living_area_logic(self):
        response = client.post("/calculate", json={
            "floor": 5,
            "total_floors": 10,
            "rooms": 2,
            "total_area": 50,
            "living_area": 60
        })
        assert response.status_code == 422
        assert "Living area must be less than total area" in response.text
