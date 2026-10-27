"""T004 - F4 Forgotten Password (OpenCart demo store).
Tester: Alfonso Dolina
Set TEST_EMAIL to the account registered in T001.
Run: pytest alfonso/test_f4_forgotten_password.py -v
"""
import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://opencart.abstracta.us/index.php?route=account/forgotten"
EMAIL = os.environ.get("TEST_EMAIL", "alf.test@example.com")
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


# Opens the Forgotten Password page, enters the email and clicks Continue.
def submit(d, email):
    d.get(URL)
    wait(d).until(EC.visibility_of_element_located((By.ID, "input-email")))
    d.find_element(By.ID, "input-email").send_keys(email)
    d.find_element(By.CSS_SELECTOR, "input[value='Continue']").click()


# Waits for the alert banner of the given kind (success/danger) and returns its text.
def alert_text(d, kind):
    el = wait(d).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f".alert-{kind}")))
    return el.text


# Scenario 1 (valid input): email of the registered test account.
# Expected: success banner saying a confirmation link has been sent.
def test_t004_s1_registered_email(driver):
    submit(driver, EMAIL)
    msg = alert_text(driver, "success")
    shot(driver, "T004-S1_registered_email")
    assert "confirmation link has been sent" in msg


# Scenario 2 (invalid input): well-formed email that is not registered.
# Expected: warning that the E-Mail Address was not found.
def test_t004_s2_unregistered_email(driver):
    submit(driver, "nobody.here.12345@example.com")
    msg = alert_text(driver, "danger")
    shot(driver, "T004-S2_unregistered_email")
    assert "E-Mail Address was not found" in msg


# Scenario 3 (empty input): field left blank.
# Expected: a warning banner and no success message.
def test_t004_s3_empty_email(driver):
    submit(driver, "")
    msg = alert_text(driver, "danger")
    shot(driver, "T004-S3_empty_email")
    assert "not found" in msg or "valid" in msg
