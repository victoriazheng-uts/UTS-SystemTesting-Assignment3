"""T002 - F2 User Login (OpenCart demo store).
Tester: Alfonso Dolina
Before running, set the account created in T001 (or pass via environment):
  export TEST_EMAIL=...  export TEST_PASSWORD=Test1234
Run: pytest alfonso/test_f2_login.py -v
"""
import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://opencart.abstracta.us/index.php?route=account/login"
EMAIL = os.environ.get("TEST_EMAIL", "alf.test@example.com")
PASSWORD = os.environ.get("TEST_PASSWORD", "Test1234")
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)


# Fixture: opens a fresh Chrome window for every test and closes it afterwards,
# so scenarios cannot affect each other (no shared cookies or session).
@pytest.fixture
def driver():
    d = webdriver.Chrome()
    d.maximize_window()
    yield d
    d.quit()


# Explicit wait helper: polls for a condition up to t seconds instead of using fixed sleeps.
def wait(d, t=10):
    return WebDriverWait(d, t)


# Saves a screenshot into alfonso/screenshots/ as evidence for the report.
def shot(d, name):
    d.save_screenshot(str(SHOTS / f"{name}.png"))


# Opens the login page, enters the credentials and clicks Login.
def login(d, email, password):
    d.get(URL)
    wait(d).until(EC.visibility_of_element_located((By.ID, "input-email")))
    d.find_element(By.ID, "input-email").send_keys(email)
    d.find_element(By.ID, "input-password").send_keys(password)
    d.find_element(By.CSS_SELECTOR, "input[value='Login']").click()


# Scenario 1 (valid input): correct email and password.
# Expected: redirected to the My Account page.
def test_t002_s1_valid_login(driver):
    login(driver, EMAIL, PASSWORD)
    wait(driver).until(EC.text_to_be_present_in_element((By.ID, "content"), "My Account"))
    shot(driver, "T002-S1_valid_login")
    assert "route=account/account" in driver.current_url


# Scenario 2 (invalid input): correct email, wrong password.
# Expected: warning 'No match for E-Mail Address and/or Password.' and stay logged out.
def test_t002_s2_wrong_password(driver):
    login(driver, EMAIL, "WrongPass999")
    wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")))
    shot(driver, "T002-S2_wrong_password")
    assert "No match for E-Mail Address and/or Password" in driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
    assert "route=account/account" not in driver.current_url


# Scenario 3 (empty input): both fields left blank.
# Expected: the same 'No match' warning and stay logged out.
def test_t002_s3_empty_fields(driver):
    login(driver, "", "")
    wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger")))
    shot(driver, "T002-S3_empty_fields")
    assert "No match for E-Mail Address and/or Password" in driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
    assert "route=account/account" not in driver.current_url
