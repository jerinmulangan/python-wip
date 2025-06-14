from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def scrape_menu(url):
    service = Service("C:/Users/jerin/chromedriver-win64/chromedriver.exe")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Enable this for production scraping
    driver = webdriver.Chrome(service=service, options=options)
    os.makedirs("errors", exist_ok=True)

    driver.get(url)

    # Wait for any part of menu to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
    except:
        driver.save_screenshot(f"errors/menu_timeout.png")
        with open("errors/menu_timeout.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[ERROR] Timeout loading menu page: {url}")
        driver.quit()
        return None

    # Header info
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text
    except:
        title = "Unknown Title"

    try:
        detail = driver.find_element(By.XPATH, "//div[contains(@class, 'details')]").text
    except:
        detail = ""

    try:
        rating = driver.find_element(By.XPATH, "//div[contains(text(), '★')]").text
    except:
        rating = "N/A"

    try:
        num_reviews = driver.find_element(By.XPATH, "//div[contains(text(), 'ratings')]").text
    except:
        num_reviews = "(0)"

    restaurant = {
        "title": title,
        "detail": detail,
        "rating": rating,
        "num_reviews": num_reviews,
        "menu": []
    }

    try:
        menu_container = driver.find_element(By.XPATH, "//main//ul")
        categories = menu_container.find_elements(By.XPATH, "./li")
    except:
        categories = []

    for cat in categories:
        try:
            category_title = cat.find_element(By.TAG_NAME, "h2").text
        except:
            continue

        items = []
        try:
            entries = cat.find_elements(By.XPATH, ".//ul/li")
        except:
            entries = []

        for entry in entries:
            try:
                name = entry.find_element(By.TAG_NAME, "h4").text
            except:
                name = ""

            try:
                description = entry.find_element(By.XPATH, ".//div[contains(@class, 'description')]").text
            except:
                description = ""

            try:
                price = entry.find_element(By.XPATH, ".//div[contains(text(), '$')]").text
                status = "Sold out" if "Sold" in price else "In stock"
                if "Sold" in price and "$" in price:
                    price = "$" + price.split("$", 1)[1]
            except:
                price = ""
                status = ""

            try:
                img = entry.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                img = ""

            items.append({
                "name": name,
                "description": description,
                "price": price,
                "status": status,
                "img_url": img
            })

        restaurant["menu"].append({category_title: items})

    driver.quit()
    return restaurant
