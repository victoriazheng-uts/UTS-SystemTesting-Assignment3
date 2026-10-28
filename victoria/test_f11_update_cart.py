import os
import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# iPhone product page (product_id=40), unit price $123.20, and the shopping cart page
PRODUCT_URL = (
    "https://opencart.abstracta.us/index.php"
    "?route=product/product&product_id=40"
)
CART_URL = "https://opencart.abstracta.us/index.php?route=checkout/cart"
WAIT = 30        # normal wait for pages to load
ADD_WAIT = 60    # adding to the cart can be very slow on this shared demo site

# Elements in the iPhone row of the cart table.
# The quantity box name includes a cart ID that changes every session
# (for example quantity[459601]), so we match names that START with "quantity".
QTY_BOX = (By.CSS_SELECTOR, "#content input[name^='quantity']")
UPDATE_BTN = (By.CSS_SELECTOR, "#content .input-group-btn button[type='submit']")
REMOVE_BTN = (By.CSS_SELECTOR, "#content .input-group-btn button.btn-danger")
ROW_TOTAL = (By.CSS_SELECTOR, "#content form table tbody tr td:nth-child(6)")

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


def open_cart_with_one_iphone(driver):
    """Step 1 and 2: add 1 iPhone on the product page, then open the cart page."""
    driver.get(PRODUCT_URL)
    WebDriverWait(driver, WAIT).until(                      # wait for the product page
        EC.visibility_of_element_located((By.ID, "button-cart"))).click()
    WebDriverWait(driver, ADD_WAIT).until(                  # wait until the cart really has 1 item
        EC.text_to_be_present_in_element((By.ID, "cart-total"), "1 item(s)"))
    driver.get(CART_URL)
    return WebDriverWait(driver, WAIT).until(               # wait for the cart table
        EC.visibility_of_element_located(QTY_BOX))


def update_quantity(driver, qty_box, value):
    """Step 3 and 4: type a new value in the quantity box and click Update."""
    qty_box.clear()
    qty_box.send_keys(value)
    driver.find_element(*UPDATE_BTN).click()
    WebDriverWait(driver, WAIT).until(EC.staleness_of(qty_box))   # wait for the page to reload


def cart_is_empty(driver):
    """Return True if the cart page shows the empty-cart message."""
    content = tidy(driver.find_element(By.ID, "content").text)
    return "Your shopping cart is empty!" in content


def test_s1_update_quantity_to_two(driver):
    """Scenario 1: changing the quantity from 1 to 2 should double the row total."""
    qty_box = open_cart_with_one_iphone(driver)
    update_quantity(driver, qty_box, "2")
    qty_box = WebDriverWait(driver, WAIT).until(            # the page reloaded, so find it again
        EC.visibility_of_element_located(QTY_BOX))
    row_total = tidy(driver.find_element(*ROW_TOTAL).text)
    shot(driver, "t011_s1_result.png")                      # evidence: cart after updating
    assert qty_box.get_attribute("value") == "2"
    assert row_total == "$246.40", f"Row total shows: {row_total}"   # 2 x $123.20


def test_s2_remove_item(driver):
    """Scenario 2: clicking Remove should empty the cart."""
    open_cart_with_one_iphone(driver)
    driver.find_element(*REMOVE_BTN).click()                # click the red Remove button
    try:
        WebDriverWait(driver, WAIT).until(                  # wait for the empty-cart message
            EC.text_to_be_present_in_element((By.ID, "content"), "Your shopping cart is empty!"))
    except TimeoutException:
        pass                                                # the assert below reports it
    shot(driver, "t011_s2_result.png")                      # evidence: cart after removing
    assert cart_is_empty(driver), "The iPhone is still in the cart after clicking Remove"


def test_s3_non_numeric_quantity_is_rejected(driver):
    """Scenario 3: "abc" is not a valid quantity, so the iPhone should stay with quantity 1."""
    qty_box = open_cart_with_one_iphone(driver)
    update_quantity(driver, qty_box, "abc")
    WebDriverWait(driver, WAIT).until(                      # wait for the reloaded page
        EC.visibility_of_element_located((By.ID, "content")))
    shot(driver, "t011_s3_result.png")                      # evidence: what the site showed
    assert not cart_is_empty(driver), \
        "Defect: entering 'abc' and clicking Update removed the iPhone from the cart"
    value = driver.find_element(*QTY_BOX).get_attribute("value")
    assert value == "1", f"Quantity box shows '{value}' instead of 1"