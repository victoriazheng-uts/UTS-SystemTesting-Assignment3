
"""T006 / F6 - Change Password Testing.

UTS Assignment 3
Website: https://opencart.abstracta.us/
Test cases:
    Scenario 1 - Valid password change and restoration
    Scenario 2 - Mismatched passwords
    Scenario 3 - Empty password
"""

import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from conftest import BASE, click, fill, login, password, wait_for


def open_password(driver):
    """Open the Change Password page."""
    driver.get(BASE + "account/password")
    wait_for(driver, (By.ID, "input-password"))


def submit_password(driver, new, confirm):
    """Enter and submit a new password."""
    fill(driver, "input-password", new)
    fill(driver, "input-confirm", confirm)

    click(
        driver,
        (By.CSS_SELECTOR, "input[type='submit'][value='Continue']")
    )


def test_s1_valid_change_and_restore(browser):
    """Scenario 1: Change password and restore original password."""

    original = password()
    temporary = os.getenv("OC_TEMP_PASSWORD", "")

    if not temporary or temporary == original:
        pytest.fail(
            "Set OC_TEMP_PASSWORD to a DIFFERENT test password"
        )

    login(browser)
    open_password(browser)

    change_attempted = False

    try:
        change_attempted = True
        submit_password(browser, temporary, temporary)

        WebDriverWait(browser, 20).until(
            lambda d: "route=account/account" in d.current_url
        )

        # Log out and verify the new password works.
        browser.get(BASE + "account/logout")
        login(browser, temporary)

        assert "route=account/account" in browser.current_url

        print("PASS: Temporary password works.")

    finally:
        if change_attempted:
            try:
                # Attempt to restore the original password.
                browser.get(BASE + "account/account")

                if "route=account/login" in browser.current_url:
                    login(browser, temporary)

                open_password(browser)
                submit_password(browser, original, original)

                WebDriverWait(browser, 20).until(
                    lambda d: "route=account/account" in d.current_url
                )

                # Verify original password works again.
                browser.get(BASE + "account/logout")
                login(browser, original)

                assert "route=account/account" in browser.current_url

                print("PASS: Original password restored.")

            except Exception as error:
                print(
                    "WARNING: Password restoration could not "
                    "be verified."
                )
                print(error)
                print(
                    "Check the original and temporary passwords "
                    "manually. Do not rerun Scenario 1 yet."
                )
                raise


def test_s2_mismatched_confirmation_rejected(browser):
    """Scenario 2: Mismatched passwords must be rejected."""

    login(browser)
    open_password(browser)

    submit_password(
        browser,
        "DifferentTest987!",
        "NotMatching987!"
    )

    WebDriverWait(browser, 20).until(
        lambda d: "text-danger" in d.page_source
    )

    assert "route=account/password" in browser.current_url

    errors = browser.find_elements(
        By.CSS_SELECTOR, ".text-danger"
    )

    error_text = " ".join(
        element.text for element in errors
    ).lower()

    assert "confirm" in error_text or "match" in error_text

    print("PASS: Mismatched passwords rejected.")


def test_s3_blank_password_rejected(browser):
    """Scenario 3: Empty password must be rejected."""

    login(browser)
    open_password(browser)

    submit_password(browser, "", "")

    WebDriverWait(browser, 20).until(
        lambda d: "text-danger" in d.page_source
    )

    assert "route=account/password" in browser.current_url

    errors = browser.find_elements(
        By.CSS_SELECTOR, ".text-danger"
    )

    error_text = " ".join(
        element.text for element in errors
    ).lower()

    assert "password" in error_text

    print("PASS: Empty password rejected.")
