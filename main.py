from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Set up driver
driver = webdriver.Chrome()
driver.get("https://trends.builtwith.com/websitelist/Magento/Germany")

# Optional: scroll to load all content
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Wait for the table to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.bg-table"))
)

# Locate the table rows (all rows after the header)
rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

data = []

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) >= 8:
        website = cells[1].text
        location = cells[2].text
        sales_revenue = cells[3].text
        tech_spend = cells[4].text
        social = cells[5].text
        employees = cells[6].text
        traffic = cells[7].text

        data.append([website, location, sales_revenue, tech_spend, social, employees, traffic])

# Save to CSV
with open("scraped_table.csv", "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Website", "Location", "Sales Revenue", "Tech Spend", "Social", "Employees", "Traffic"])
    writer.writerows(data)

# Close the driver
driver.quit()
