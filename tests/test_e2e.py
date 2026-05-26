import pytest
import allure
from playwright.sync_api import Page, expect
import os

@allure.feature("Расчет стоимости")
@allure.story("UI тесты")
class TestUi:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, page: Page):
        path = os.path.abspath("frontend/index.html")
        with allure.step("Открытие главной страницы"):
            page.goto(f"file://{path}")

    @allure.title("Позитивный сценарий: Успешный расчет")
    def test_frontend_calculation_success(self, page: Page):
        with allure.step("Заполнение формы валидными данными"):
            page.fill("#floor", "5")
            page.fill("#total_floors", "10")
            page.fill("#rooms", "2")
            page.fill("#total_area", "50")
            page.fill("#living_area", "30")
        
        with allure.step("Нажатие кнопки рассчитать"):
            page.click("button[type='submit']")
        
        with allure.step("Проверка отображения результата"):
            expect(page.locator("#result")).to_be_visible()
            expect(page.locator("#price-per-meter")).not_to_be_empty()

    @allure.title("Негативный сценарий: Ошибка валидации на этаж")
    def test_frontend_validation_error(self, page: Page):
        with allure.step("Ввод этажа превышающего этажность"):
            page.fill("#floor", "15")
            page.fill("#total_floors", "10")
            page.fill("#rooms", "2")
            page.fill("#total_area", "50")
            page.fill("#living_area", "30")
        
        with allure.step("Нажатие кнопки рассчитать"):
            page.click("button[type='submit']")
        
        with allure.step("Проверка сообщения об ошибке"):
            expect(page.locator("#error")).to_be_visible()
            expect(page.locator("#error")).to_contain_text("Total floors cannot be less than current floor")
