"""T008 - F8 Product Comparison (OpenCart demo store).
Tester: Sona Dheep Raja Balaji
Run: pytest sona/test_f8_product_comparison.py -v
"""
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PRODUCT_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id={}"
COMPARE_URL = "https://opencart.abstracta.us/index.php?route=product/compare"
IPHONE = "40"    # product_id of the iPhone ($123.20)
MACBOOK = "43"   # product_id of the MacBook ($602.00)
WAIT = 30        # the shared demo site (and an older Intel Mac) can be slow, so allow up to 30 seconds

# Locators used by every scenario
COMPARE_NAMES = (By.CSS_SELECTOR, "#content table td a strong")   # product names in the comparison table
EMPTY_TEXT = "You have not chosen any products to compare."

# Evidence screenshots are saved in sona/screenshots/
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)


# Fixture: opens a fresh Chrome window for every test and closes it afterwards.
# The comparison list is stored in the browser session, so every test starts with an empty list.
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


# Opens a product page, clicks its "Compare this Product" button and returns the green message text.
def add_to_compare(d, product_id):
    d.get(PRODUCT_URL.format(product_id))                                 # open the product page
    button = (By.CSS_SELECTOR, f"button[onclick*=\"compare.add('{product_id}')\"]")  # the compare (two arrows) button
    WebDriverWait(d, WAIT).until(EC.element_to_be_clickable(button)).click()
    alert = WebDriverWait(d, WAIT).until(                                 # wait for the site to confirm,
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success")))  # so the list is saved before moving on
    return tidy(alert.text)


# Opens the Product Comparison page and returns the product names shown in the table.
def open_compare(d):
    d.get(COMPARE_URL)
    WebDriverWait(d, WAIT).until(EC.visibility_of_element_located((By.ID, "content")))
    return [e.text for e in d.find_elements(*COMPARE_NAMES)]


# Scenario 1 (valid input): add two different products, then open the comparison page.
# Expected: a success message for each, and both products are shown side by side.
def test_t008_s1_compare_two_products(driver):
    msg1 = add_to_compare(driver, IPHONE)
    assert "Success: You have added iPhone to your product comparison" in msg1, f"Message: {msg1}"
    msg2 = add_to_compare(driver, MACBOOK)
    assert "Success: You have added MacBook to your product comparison" in msg2, f"Message: {msg2}"
    names = open_compare(driver)
    print("Products compared:", names)
    shot(driver, "T008-S1_compare_two_products")                       # evidence screenshot
    assert sorted(names) == ["MacBook", "iPhone"], f"Comparison table shows: {names}"  # exactly these two
    assert "Product Details" in tidy(driver.find_element(By.ID, "content").text)  # the details table is shown


# Scenario 2 (duplicate input): add the same product twice.
# Expected: the product appears only once in the comparison table.
def test_t008_s2_same_product_twice(driver):
    add_to_compare(driver, IPHONE)                                     # first time
    add_to_compare(driver, IPHONE)                                     # second time, same product
    names = open_compare(driver)
    shot(driver, "T008-S2_same_product_twice")
    assert names.count("iPhone") == 1, f"Comparison table shows: {names}"  # no duplicate column


# Scenario 3 (remove): add one product, then remove it on the comparison page.
# Expected: the list becomes empty and the 'not chosen any products' message is shown.
def test_t008_s3_remove_product(driver):
    add_to_compare(driver, IPHONE)
    assert open_compare(driver) == ["iPhone"]                          # it is in the list before removing
    remove = driver.find_element(By.CSS_SELECTOR, f"#content a[href*='remove={IPHONE}']")  # red Remove button
    remove.click()
    try:
        WebDriverWait(driver, WAIT).until(EC.staleness_of(remove))     # wait for the page to reload
    except TimeoutException:
        pass                                                           # the asserts below report what happened
    WebDriverWait(driver, WAIT).until(EC.visibility_of_element_located((By.ID, "content")))
    names = [e.text for e in driver.find_elements(*COMPARE_NAMES)]
    page = tidy(driver.find_element(By.ID, "content").text)
    print("Page after Remove:", page)                                  # recorded for the report
    shot(driver, "T008-S3_remove_product")                             # evidence, taken before any check can fail
    assert names == [], f"Defect: product still listed after Remove: {names}"  # main outcome: list is empty
    assert EMPTY_TEXT in page, f"Defect: wrong or missing empty-list message. Page shows: {page[-120:]}"
