import os
import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
# iPhone product page (product_id=40), unit price $123.20, and the checkout page
PRODUCT_URL = (
    "https://opencart.abstracta.us/index.php"
    "?route=product/product&product_id=40"
)
CHECKOUT_URL = "https://opencart.abstracta.us/index.php?route=checkout/checkout"
WAIT = 30        # normal wait for pages and checkout steps to load
ADD_WAIT = 60    # adding to the cart can be very slow on this shared demo site
 
# Test data for Step 2 (Billing Details). Every field id starts with "input-payment-".
VALID_DETAILS = {
    "firstname": "Victoria",
    "lastname": "Tester",
    "email": "victoria.test@example.com",
    "telephone": "0412345678",
    "address-1": "15 Broadway",
    "city": "Sydney",
    "postcode": "2007",
}
COUNTRY = "Australia"
REGION = "New South Wales"
 
# Error messages are shown in red under each field, inside the Step 2 panel
STEP2_ERRORS = (By.CSS_SELECTOR, "#collapse-payment-address .text-danger")
 
# Evidence screenshots are saved in victoria/screenshots/
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
 
 
@pytest.fixture
def driver():
    driver = webdriver.Chrome()   # fresh Chrome window, so every test starts with an empty cart
    driver.maximize_window()
    yield driver
    driver.quit()                 # close the browser when the test ends
 
 
def shot(driver, name):
    """Save a screenshot of the browser window as evidence for the report."""
    os.makedirs(SHOTS, exist_ok=True)
    driver.save_screenshot(os.path.join(SHOTS, name))
 
 
def click(driver, by, value):
    """Wait until an element can be clicked, then click it."""
    WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((by, value))).click()
 
 
def start_guest_checkout(driver):
    """Steps 1 to 3: add 1 iPhone, open checkout, and choose Guest Checkout."""
    driver.get(PRODUCT_URL)
    click(driver, By.ID, "button-cart")                     # Add to Cart
    WebDriverWait(driver, ADD_WAIT).until(                  # wait until the cart really has 1 item
        EC.text_to_be_present_in_element((By.ID, "cart-total"), "1 item(s)"))
    driver.get(CHECKOUT_URL)
    click(driver, By.CSS_SELECTOR, "input[name='account'][value='guest']")   # Guest Checkout
    click(driver, By.ID, "button-account")                  # Step 1 Continue
    WebDriverWait(driver, WAIT).until(                      # wait for the Step 2 form
        EC.visibility_of_element_located((By.ID, "input-payment-firstname")))
 
 
def fill_billing_details(driver, details):
    """Step 4: type each value into its Step 2 field, then choose country and region."""
    for field, value in details.items():
        box = driver.find_element(By.ID, f"input-payment-{field}")
        box.clear()
        box.send_keys(value)
    country_option = (By.XPATH, f"//select[@id='input-payment-country']/option[text()='{COUNTRY}']")
    WebDriverWait(driver, WAIT).until(                      # the dropdown is locked while it loads
        lambda d: d.find_element(*country_option).is_enabled())
    Select(driver.find_element(By.ID, "input-payment-country")).select_by_visible_text(COUNTRY)
    WebDriverWait(driver, WAIT).until(                      # regions reload for the new country
        EC.presence_of_element_located(
            (By.XPATH, f"//select[@id='input-payment-zone']/option[text()='{REGION}']")))
    Select(driver.find_element(By.ID, "input-payment-zone")).select_by_visible_text(REGION)
 
 
def step2_errors(driver, timeout=WAIT):
    """Wait for red error messages in Step 2 and return their text ([] if none appear)."""
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(STEP2_ERRORS))
    except TimeoutException:
        return []
    return [e.text for e in driver.find_elements(*STEP2_ERRORS) if e.text]
 
 
def reached_delivery_method(driver, timeout=10):
    """Return True if checkout moved on to Step 4 (Delivery Method)."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "button-shipping-method")))
        return True
    except TimeoutException:
        return False
 
 
def checkout_messages(driver):
    """Return the text of any warning or error messages shown on the checkout page."""
    found = driver.find_elements(By.CSS_SELECTOR, "#content .alert, #content .text-danger")
    return [" ".join(e.text.split()) for e in found if e.text]
 
 
def test_s1_valid_guest_checkout(driver):
    """Scenario 1: valid details should let a guest place the order."""
    start_guest_checkout(driver)
    fill_billing_details(driver, VALID_DETAILS)
    click(driver, By.ID, "button-guest")                    # Step 2 Continue
    click(driver, By.ID, "button-shipping-method")          # Step 4: keep Flat Shipping Rate
    agree = WebDriverWait(driver, WAIT).until(              # Step 5: Terms & Conditions box
        EC.element_to_be_clickable((By.NAME, "agree")))
    if not agree.is_selected():                             # tick it only if it is not ticked yet
        agree.click()
    click(driver, By.ID, "button-payment-method")           # Step 5 Continue
    try:
        WebDriverWait(driver, ADD_WAIT).until(              # Step 6: order summary is shown
            EC.visibility_of_element_located((By.ID, "button-confirm")))
    except TimeoutException:
        shot(driver, "t012_s1_stuck.png")                   # evidence: where checkout stopped
        pytest.fail(f"Checkout did not reach Step 6. Messages: {checkout_messages(driver)}")
    summary = driver.find_element(By.ID, "collapse-checkout-confirm").text
    shot(driver, "t012_s1_confirm.png")                     # evidence: order summary
    assert "iPhone" in summary, f"Order summary shows: {summary}"
    click(driver, By.ID, "button-confirm")                  # Confirm Order
    try:
        WebDriverWait(driver, ADD_WAIT).until(              # wait to leave the checkout page
            EC.url_contains("checkout/success"))
    except TimeoutException:
        pass                                                # the assert below reports it
    heading = WebDriverWait(driver, WAIT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#content h1"))).text
    shot(driver, "t012_s1_result.png")                      # evidence: order placed page
    assert heading == "Your order has been placed!", f"Page heading shows: {heading}"
 
 
def test_s2_empty_billing_details(driver):
    """Scenario 2: leaving every field empty should show an error under each required field."""
    start_guest_checkout(driver)
    click(driver, By.ID, "button-guest")                    # Step 2 Continue with nothing filled in
    errors = step2_errors(driver)
    shot(driver, "t012_s2_result.png")                      # evidence: error messages
    assert "First Name must be between 1 and 32 characters!" in errors, f"Errors: {errors}"
    assert len(errors) >= 6, f"Only {len(errors)} error messages: {errors}"
    assert not reached_delivery_method(driver), "Defect: checkout moved on with empty fields"
 
 
def test_s3_invalid_email(driver):
    """Scenario 3: an e-mail without a domain should be rejected."""
    start_guest_checkout(driver)
    details = dict(VALID_DETAILS, email="victoria.test@")  # same details, invalid e-mail
    fill_billing_details(driver, details)
    click(driver, By.ID, "button-guest")                    # Step 2 Continue
    errors = step2_errors(driver, timeout=15)
    shot(driver, "t012_s3_result.png")                      # evidence: what the site showed
    email_error = any("does not appear to be valid" in e for e in errors)
    assert email_error, f"Defect: no e-mail error was shown. Errors: {errors}"
    assert not reached_delivery_method(driver), "Defect: checkout moved on with an invalid e-mail"