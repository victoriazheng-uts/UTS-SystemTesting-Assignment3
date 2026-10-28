"""T009 - F9 Wishlist (OpenCart demo store).
Tester: Sona Dheep Raja Balaji
The wish list needs a logged-in user, so Scenarios 1 and 2 first register a brand-new
account (registration logs the user in automatically). This gives every run an empty
wish list and needs no password to be set up beforehand.
Run: pytest sona/test_f9_wishlist.py -v
"""
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

REGISTER_URL = "https://opencart.abstracta.us/index.php?route=account/register"
PRODUCT_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id={}"
WISHLIST_URL = "https://opencart.abstracta.us/index.php?route=account/wishlist"
IPHONE = "40"    # product_id of the iPhone ($123.20)
WAIT = 30        # normal wait for pages to load
SLOW_WAIT = 60   # registering an account can be very slow on this shared demo site

EMPTY_TEXT = "Your wish list is empty."
REMOVE_LINK = (By.CSS_SELECTOR, f"#content a[href*='remove={IPHONE}']")  # red X button in the iPhone row

# Evidence screenshots are saved in sona/screenshots/
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)


# Fixture: opens a fresh Chrome window for every test and closes it afterwards,
# so scenarios cannot affect each other (no shared cookies, login or wish list).
@pytest.fixture
def driver():
    d = webdriver.Chrome()   # Selenium Manager downloads the matching ChromeDriver automatically
    d.maximize_window()      # full size so all buttons are visible
    yield d                  # hand the browser to the test
    d.quit()                 # always close the browser, even if the test fails


# Saves a screenshot into sona/screenshots/ as evidence for the report.
def shot(d, name):
    d.save_screenshot(str(SHOTS / f"{name}.png"))


# Joins text that the page splits over several lines into one line.
def tidy(text):
    return " ".join(text.split())


# Registers a new account with a unique email; OpenCart logs the new user in straight away.
def register_and_login(d):
    email = f"sona.test{int(time.time() * 1000)}@example.com"            # unique every run, so never "already registered"
    print("Test account:", email)
    d.get(REGISTER_URL)
    WebDriverWait(d, WAIT).until(EC.visibility_of_element_located((By.ID, "input-firstname")))
    for field, value in [("input-firstname", "Sona"), ("input-lastname", "Tester"),
                         ("input-email", email), ("input-telephone", "0400000000"),
                         ("input-password", "Test1234"), ("input-confirm", "Test1234")]:
        d.find_element(By.ID, field).send_keys(value)                    # fill every required field
    d.find_element(By.NAME, "agree").click()                             # tick the Privacy Policy box
    d.find_element(By.CSS_SELECTOR, "input[value='Continue']").click()   # submit the form
    WebDriverWait(d, SLOW_WAIT).until(EC.url_contains("route=account/success"))  # registered and logged in


# Opens the iPhone page, clicks "Add to Wish List" (heart button) and returns the message text.
def add_to_wishlist(d, product_id):
    d.get(PRODUCT_URL.format(product_id))
    button = (By.CSS_SELECTOR, f"button[onclick*=\"wishlist.add('{product_id}')\"]")
    WebDriverWait(d, WAIT).until(EC.element_to_be_clickable(button)).click()
    alert = WebDriverWait(d, WAIT).until(                                # wait for the site's reply message
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert")))
    return tidy(alert.text)


# Opens the My Wish List page and returns its main text.
def open_wishlist(d):
    d.get(WISHLIST_URL)
    WebDriverWait(d, WAIT).until(EC.visibility_of_element_located((By.ID, "content")))
    return tidy(d.find_element(By.ID, "content").text)


# Scenario 1 (valid input): a logged-in user adds the iPhone to the wish list.
# Expected: a success message, and the iPhone is listed on the My Wish List page.
def test_t009_s1_add_product_logged_in(driver):
    register_and_login(driver)
    message = add_to_wishlist(driver, IPHONE)
    shot(driver, "T009-S1_added_message")                                # evidence: message on the product page
    assert "Success: You have added iPhone to your wish list" in message, f"Message: {message}"
    print("Header link shows:", driver.find_element(By.ID, "wishlist-total").text)  # recorded for the report
    content = open_wishlist(driver)
    shot(driver, "T009-S1_wishlist_page")                                # evidence: the wish list itself
    assert "iPhone" in content, f"Wish list page shows: {content}"
    assert driver.find_elements(*REMOVE_LINK), "The iPhone row has no Remove button"


# Scenario 2 (remove): a logged-in user removes the iPhone from the wish list.
# Expected: 'Success: You have modified your wish list!' and the list becomes empty.
def test_t009_s2_remove_product(driver):
    register_and_login(driver)
    add_to_wishlist(driver, IPHONE)
    open_wishlist(driver)
    remove = driver.find_element(*REMOVE_LINK)
    remove.click()                                                       # click the red X in the iPhone row
    try:
        WebDriverWait(driver, WAIT).until(EC.staleness_of(remove))       # wait for the page to reload
    except TimeoutException:
        pass                                                             # the asserts below report what happened
    WebDriverWait(driver, WAIT).until(EC.visibility_of_element_located((By.ID, "content")))
    content = tidy(driver.find_element(By.ID, "content").text)
    page = tidy(driver.find_element(By.TAG_NAME, "body").text)          # the success bar sits above the content
    print("Wish list after Remove:", content)                            # recorded for the report
    shot(driver, "T009-S2_removed")                                      # evidence, taken before any check can fail
    assert not driver.find_elements(*REMOVE_LINK), "Defect: the iPhone is still in the wish list"  # main outcome
    assert EMPTY_TEXT in content, f"Defect: wrong or missing empty-list message. Page shows: {content[-120:]}"
    assert "Success: You have modified your wish list" in page, "No confirmation message was shown"


# Scenario 3 (invalid: not logged in): a guest tries to add the iPhone to the wish list.
# Expected: the site asks the user to log in or create an account, and the
# My Wish List page sends the guest to the login page instead of showing a list.
def test_t009_s3_guest_cannot_use_wishlist(driver):
    message = add_to_wishlist(driver, IPHONE)                            # fresh browser, so not logged in
    shot(driver, "T009-S3_guest_message")
    assert "You must login or create an account" in message, f"Message: {message}"
    driver.get(WISHLIST_URL)                                             # try to open the wish list directly
    WebDriverWait(driver, WAIT).until(EC.url_contains("route=account/login"))
    shot(driver, "T009-S3_redirect_to_login")
    assert "route=account/login" in driver.current_url                   # guest is sent to the login page
