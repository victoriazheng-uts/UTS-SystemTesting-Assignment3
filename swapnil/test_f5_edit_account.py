"""T005 / F5 Edit Account Information: valid and invalid input tests."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from conftest import BASE, click, fill, login, wait_for


def open_edit(driver):
    driver.get(BASE + "account/edit")
    wait_for(driver, (By.ID, "input-firstname"))


def save(driver):
    click(driver, (By.CSS_SELECTOR, "input[type='submit'][value='Continue']"))


def test_s1_valid_firstname_update(browser):
    """Scenario 1: valid first name is saved and persists on re-open."""
    login(browser)
    open_edit(browser)
    original = browser.find_element(By.ID, "input-firstname").get_attribute("value")
    updated = "TestingName" if original != "TestingName" else "AlternateName"
    try:
        fill(browser, "input-firstname", updated)
        save(browser)
        WebDriverWait(browser, 20).until(lambda d: "route=account/account" in d.current_url)
        open_edit(browser)
        assert browser.find_element(By.ID, "input-firstname").get_attribute("value") == updated
    finally:
        # Restore original value so the real account is not left with test data.
        open_edit(browser)
        fill(browser, "input-firstname", original)
        save(browser)


def test_s2_empty_firstname_is_rejected(browser):
    """Scenario 2: empty mandatory first name is rejected."""
    login(browser)
    open_edit(browser)
    fill(browser, "input-firstname", "")
    save(browser)
    WebDriverWait(browser, 20).until(
        lambda d: "First Name must be" in d.page_source or "text-danger" in d.page_source
    )
    assert "route=account/edit" in browser.current_url
    assert "First Name" in browser.page_source


def test_s3_invalid_email_is_rejected(browser):
    """Scenario 3: malformed email cannot replace the registered email."""
    login(browser)
    open_edit(browser)
    fill(browser, "input-email", "not-an-email")
    save(browser)
    WebDriverWait(browser, 20).until(
        lambda d: "E-Mail Address does not appear to be valid" in d.page_source
        or "E-Mail address does not appear to be valid" in d.page_source
        or "text-danger" in d.page_source
    )
    assert "route=account/edit" in browser.current_url
    assert "valid" in browser.page_source.lower() or "text-danger" in browser.page_source
