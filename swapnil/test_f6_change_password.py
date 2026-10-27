"""T006 / F6 Change Password. Run AFTER logout and edit tests."""
import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from conftest import BASE, click, fill, login, password, wait_for


def open_password(driver):
    driver.get(BASE + "account/password")
    wait_for(driver, (By.ID, "input-password"))


def submit_password(driver, new, confirm):
    fill(driver, "input-password", new)
    fill(driver, "input-confirm", confirm)
    click(driver, (By.CSS_SELECTOR, "input[type='submit'][value='Continue']"))


def test_s1_valid_change_and_restore(browser):
    """Scenario 1: new password works; old password restored before exit."""
    original = password()
    temporary = os.getenv("OC_TEMP_PASSWORD", "")
    if not temporary or temporary == original:
        pytest.fail("Set OC_TEMP_PASSWORD to a DIFFERENT test-only password")
    login(browser)
    open_password(browser)
    submit_password(browser, temporary, temporary)
    WebDriverWait(browser, 20).until(lambda d: "route=account/account" in d.current_url)

    # Verify fresh login with newly changed password.
    browser.get(BASE + "account/logout")
    login(browser, temporary)
    assert "route=account/account" in browser.current_url

    # Restore initial password; if this fails, manually reset it at the site.
    open_password(browser)
    submit_password(browser, original, original)
    WebDriverWait(browser, 20).until(lambda d: "route=account/account" in d.current_url)
    browser.get(BASE + "account/logout")
    login(browser, original)


def test_s2_mismatched_confirmation_rejected(browser):
    """Scenario 2: different password and confirmation are rejected."""
    login(browser)
    open_password(browser)
    submit_password(browser, "DifferentTest987!", "NotMatching987!")
    WebDriverWait(browser, 20).until(lambda d: "text-danger" in d.page_source)
    assert "route=account/password" in browser.current_url
    assert "confirm" in browser.page_source.lower()


def test_s3_blank_password_rejected(browser):
    """Scenario 3: empty password is rejected."""
    login(browser)
    open_password(browser)
    submit_password(browser, "", "")
    WebDriverWait(browser, 20).until(lambda d: "text-danger" in d.page_source)
    assert "route=account/password" in browser.current_url
    assert "password" in browser.page_source.lower()
