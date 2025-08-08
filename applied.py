from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Selenium
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.skyracingworld.com/")
time.sleep(5)  # wait for full page load

# Find all the racing sections
race_sections = driver.find_elements(By.CSS_SELECTOR, ".v2_todays-racing-list-item")

all_links = []

for i, section in enumerate(race_sections):
    try:
        print(f"\nProcessing section {i+1}/{len(race_sections)}")

        # Scroll to the section so it's in view
        driver.execute_script("arguments[0].scrollIntoView(true);", section)
        time.sleep(1)

        # Check if the <ul> is already expanded
        ul = section.find_element(By.CSS_SELECTOR, ".list-body")
        is_open = "list-body-opened" in ul.get_attribute("class")

        if not is_open:
            # Find toggle button and click it
            toggle = section.find_element(By.CSS_SELECTOR, ".list-head-icon-container")
            try:
                toggle.click()
            except:
                # JS click fallback
                driver.execute_script("arguments[0].click();", toggle)

            time.sleep(1)  # wait for animation

        # Wait until the ul has the "list-body-opened" class
        WebDriverWait(section, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".list-body.list-body-opened"))
        )

        # Now get all the links inside the expanded ul
        items = section.find_elements(By.CSS_SELECTOR, ".list-body-item")
        for item in items:
            try:
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                print(f" ➤ {link}")
                all_links.append(link)
            except Exception as e:
                print("   Failed to get link from item:", e)

    except Exception as e:
        print(f"Error expanding section {i+1}: {e}")

driver.quit()

print(f"\nTotal links collected: {len(all_links)}")
