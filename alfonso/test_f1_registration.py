"""T001 - F1 User Registration (OpenCart demo store).
Tester: Alfonso Dolina
Run: pytest alfonso/test_f1_registration.py -v
"""
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://opencart.abstracta.us/index.php?route=account/register"
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


# Opens the registration page, types into each field, optionally ticks the Privacy Policy box, then clicks Continue.
def fill(d, first="", last="", email="", phone="", pw="", confirm="", agree=False):
    d.get(URL)
    wait(d).until(EC.visibility_of_element_located((By.ID, "input-firstname")))
    for fid, val in [("input-firstname", first), ("input-lastname", last),
                     ("input-email", email), ("input-telephone", phone),
                     ("input-password", pw), ("input-confirm", confirm)]:
        d.find_element(By.ID, fid).send_keys(val)
    if agree:
        d.find_element(By.NAME, "agree").click()
    d.find_element(By.CSS_SELECTOR, "input[value='Continue']").click()


# Returns all visible text on the page, used for checking validation messages.
def page_text(d):
    return d.find_element(By.TAG_NAME, "body").text


# Scenario 1 (valid input): a unique email is generated so the account does not already exist.
# Expected: redirect to the 'Account Success' page with a congratulations message.
def test_t001_s1_valid_registration(driver):
    email = f"alf.test{int(time.time())}@example.com"
    print("Registered email:", email)
    fill(driver, "Alfonso", "Tester", email, "0400000000", "Test1234", "Test1234", agree=True)
    # Wait until the site redirects to the registration-success page (max 20s).
    wait(driver, 20).until(EC.url_contains("route=account/success"))
    shot(driver, "T001-S1_valid_registration")  # evidence screenshot
    # The success page shows the heading 'Account Success' and a congratulations message.
    text = page_text(driver)
    assert "Account Success" in text
    assert "Your new account has been successfully created" in text


# Scenario 2 (empty input): submit the blank form without agreeing to the Privacy Policy.
# Expected: validation errors on each required field and no account created.
def test_t001_s2_empty_form_rejected(driver):
    fill(driver, agree=False)
    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".text-danger, .alert-danger")))
    shot(driver, "T001-S2_empty_form")
    text = page_text(driver)
    assert "Privacy Policy" in text
    assert "First Name must be between 1 and 32 characters" in text
    assert "E-Mail Address does not appear to be valid" in text
    assert "Your new account has been successfully created" not in text


# Scenario 3 (invalid input): password and confirmation differ.
# Expected: 'Password confirmation does not match password!' and no account created.
def test_t001_s3_password_mismatch(driver):
    email = f"alf.mismatch{int(time.time())}@example.com"
    fill(driver, "Alfonso", "Tester", email, "0400000000", "Test1234", "Different99", agree=True)
    wait(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".text-danger")))
    shot(driver, "T001-S3_password_mismatch")
    text = page_text(driver)
    assert "Password confirmation does not match password" in text
    assert "Your new account has been successfully created" not in text
