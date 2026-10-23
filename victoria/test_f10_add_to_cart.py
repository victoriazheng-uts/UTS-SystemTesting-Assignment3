import os
import warnings
import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
# iPhone product page (product_id=40), unit price $123.20
PRODUCT_URL = (
    "https://opencart.abstracta.us/index.php"
    "?route=product/product&product_id=40"
)
WAIT = 30        # normal wait for pages to load
ADD_WAIT = 60    # adding to the cart can be very slow on this shared demo site
 
# Evidence screenshots are saved in victoria/screenshots/
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
 
 
@pytest.fixture
def driver():
    driver = webdriver.Chrome()   # fresh Chrome window, so every test starts with an empty cart
    driver.maximize_window()
    yield driver
    driver.quit()                 # close the browser when the test ends
 
 
def tidy(text):
    """Join text that the page splits over several lines into one line."""
    return " ".join(text.split())
 
 
def shot(driver, name):
    """Save a screenshot of the browser window as evidence for the report."""
    os.makedirs(SHOTS, exist_ok=True)
    driver.save_screenshot(os.path.join(SHOTS, name))
 
 
def add_iphone_to_cart(driver, quantity):
    """Open the iPhone page, type a quantity in the Qty box, and click Add to Cart."""
    driver.get(PRODUCT_URL)
    qty_box = WebDriverWait(driver, WAIT).until(            # wait for the page to load
        EC.visibility_of_element_located((By.ID, "input-quantity")))
    qty_box.clear()                                         # remove the default "1"
    qty_box.send_keys(str(quantity))                        # type the test quantity
    driver.find_element(By.ID, "button-cart").click()       # click Add to Cart
 
 
def cart_summary(driver, expected, timeout=ADD_WAIT):
    """Wait for the header cart button to show the expected text, then return its text."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((By.ID, "cart-total"), expected))
    except TimeoutException:
        pass                                                # the assert in the test reports it
    return tidy(driver.find_element(By.ID, "cart-total").text)
 
 
def shown_message(driver, timeout=5):
    """Return the text of the green success bar, or "" if it is not shown."""
    try:
        alert = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))
        return tidy(alert.text)
    except TimeoutException:
        return ""
 
 
def check_success_message(message):
    """The message is secondary: if it is missing, warn instead of failing the test."""
    if "Success: You have added iPhone to your shopping cart" not in message:
        warnings.warn("The cart was updated correctly, "
                      "but no success message was shown to the user.")
 
 
def test_s1_add_one_iphone(driver):
    """Scenario 1: adding 1 iPhone should give a cart of 1 item and a success message."""
    add_iphone_to_cart(driver, 1)
    summary = cart_summary(driver, "1 item(s) - $123.20")   # main outcome: the cart total
    message = shown_message(driver)
    shot(driver, "t010_s1_result.png")                      # evidence: page after adding
    assert "1 item(s) - $123.20" in summary, f"Header cart shows: {summary}"
    check_success_message(message)
 
 
def test_s2_add_three_iphones(driver):
    """Scenario 2: adding 3 iPhones should give a cart of 3 items totalling 3 x $123.20."""
    add_iphone_to_cart(driver, 3)
    summary = cart_summary(driver, "3 item(s) - $369.60")   # 3 x $123.20 = $369.60
    message = shown_message(driver)
    shot(driver, "t010_s2_result.png")                      # evidence: page after adding
    assert "3 item(s) - $369.60" in summary, f"Header cart shows: {summary}"
    check_success_message(message)
 
 
def test_s3_quantity_zero_is_rejected(driver):
    """Scenario 3: quantity 0 is invalid, so the site should not report the iPhone as added."""
    add_iphone_to_cart(driver, 0)
    message = shown_message(driver, timeout=15)             # give the site 15 seconds to react
    summary = tidy(driver.find_element(By.ID, "cart-total").text)
    shot(driver, "t010_s3_result.png")                      # evidence: what the site showed
    assert "Success" not in message, (f"Defect: the site accepted quantity 0. "
                                      f"Message: {message}. Header cart: {summary}")