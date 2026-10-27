"""T003 / F3 User Logout: three scenarios."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import BASE, click, login


def perform_logout(driver):
    driver.get(BASE + "account/logout")
    WebDriverWait(driver, 20).until(EC.url_contains("route=account/logout"))
    assert "Account Logout" in driver.page_source or "logged off" in driver.page_source


def test_s1_successful_logout(browser):
    """Scenario 1: logged-in customer can log out."""
    login(browser)
    perform_logout(browser)
    assert "Account Logout" in browser.page_source or "logged off" in browser.page_source


def test_s2_login_available_after_logout(browser):
    """Scenario 2: logging out makes the login form available again."""
    login(browser)
    perform_logout(browser)
    browser.get(BASE + "account/login")
    assert WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.ID, "input-email"))
    ).is_displayed()


def test_s3_protected_page_redirects_after_logout(browser):
    """Scenario 3: account editing cannot be accessed after logout."""
    login(browser)
    perform_logout(browser)
    browser.get(BASE + "account/edit")
    WebDriverWait(browser, 20).until(EC.url_contains("route=account/login"))
    assert "route=account/login" in browser.current_url
