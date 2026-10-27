"""Shared browser, authentication and screenshots for OpenCart account tests."""
import os
import re
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE = "https://opencart.abstracta.us/index.php?route="
SCREENSHOTS = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)
EMAIL = os.getenv("OC_TEST_EMAIL", "swapniltirpude33@gmail.com")


def password():
    value = os.getenv("OC_TEST_PASSWORD")
    if not value:
        pytest.fail("Set OC_TEST_PASSWORD to your test account password in Terminal")
    return value


def wait_for(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


def click(driver, locator):
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(locator))
    element.click()


def fill(driver, field_id, value):
    field = wait_for(driver, (By.ID, field_id))
    field.clear()
    field.send_keys(value)


def login(driver, pwd=None):
    driver.get(BASE + "account/login")
    fill(driver, "input-email", EMAIL)
    fill(driver, "input-password", pwd if pwd is not None else password())
    click(driver, (By.CSS_SELECTOR, "input[type='submit'][value='Login']"))
    WebDriverWait(driver, 20).until(lambda d: "route=account/account" in d.current_url or "alert-danger" in d.page_source)
    assert "route=account/account" in driver.current_url, "Login failed; verify account credentials"


def screenshot(driver, label):
    filename = re.sub(r"[^a-zA-Z0-9_-]", "_", label) + ".png"
    path = SCREENSHOTS / filename
    driver.save_screenshot(str(path))
    print(f"Screenshot: {path}")


@pytest.fixture
def browser(request):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1000")
    driver = webdriver.Chrome(options=options)  # Selenium Manager handles ChromeDriver
    try:
        yield driver
    finally:
        screenshot(driver, request.node.name)
        driver.quit()
