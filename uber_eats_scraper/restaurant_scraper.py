from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


def scrape_restaurants(base_url, location):
    # Setup ChromeDriver
    service = Service("C:/Users/jerin/chromedriver-win64/chromedriver.exe")
    options = webdriver.ChromeOptions()

    # 🔍 For debugging, keep headless off
    # options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    os.makedirs("errors", exist_ok=True)

    # Optional: set location cookie if needed
    driver.get("https://www.ubereats.com/")
    driver.add_cookie({
        'name': 'uev2.loc',
        'value': '{"locationId":"ebfb0006-5ba1-4f2c-81b0-98e8d43ffb20","locationType":"city"}',
        'domain': '.ubereats.com',
        'path': '/',
    })
    driver.get(base_url + location)

    # STEP 1: Get all category links
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/main/div[2]"))
        )
        categories_block = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/main/div[2]")
        category_links = categories_block.find_elements(By.TAG_NAME, "a")

        print(f"[{location}] Found {len(category_links)} category links")

        category_map = {}
        for link in category_links:
            name = link.text.strip()
            href = link.get_attribute("href")
            if name and href:
                category_map[name] = href

    except Exception as e:
        print(f"Could not find categories on page: {base_url + location}")
        print(e)
        return

    # STEP 2: Scrape each category for restaurant links
    for name, url in category_map.items():
        try:
            print(f"Fetching: {url}")
            time.sleep(1)  # Wait between requests
            driver.get(url)

            # Wait until restaurant cards are present (anchor tags to /store/)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/store/')]"))
            )

            # Additional wait to allow JavaScript to finish rendering
            time.sleep(1)

            anchors = driver.find_elements(By.XPATH, "//a[contains(@href, '/store/')]")
            valid_urls = [a.get_attribute("href") for a in anchors if a.get_attribute("href")]

            if not valid_urls:
                raise Exception("Found anchor tags, but none with /store/")

            with open("temp_urls.txt", "a", encoding='utf-8') as out_file:
                for link in valid_urls:
                    out_file.write(link + "\n")

        except Exception as e:
            print(f"No valid restaurant links found in: {name}")
            driver.save_screenshot(f"errors/{location}_{name.replace(' ', '_')}_empty.png")
            with open(f"errors/{location}_{name.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            continue

    # STEP 3: Deduplicate and write output
    lines_seen = set()
    with open(location + "_restaurant_urls.txt", "w+", encoding='utf-8') as out_file:
        for line in open("temp_urls.txt", "r", encoding='utf-8'):
            if line not in lines_seen:
                out_file.write(line)
                lines_seen.add(line)

    os.remove("temp_urls.txt")
    driver.quit()
