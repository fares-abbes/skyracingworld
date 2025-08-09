import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clean_time(raw):
    match = re.search(r"(\d{1,2}):(\d{2})", raw)
    if not match:
        return ""
    hh, mm = int(match.group(1)), match.group(2)
    if ("PM" in raw.upper() or "ET" in raw.upper()) and hh != 12:
        hh = (hh % 12) + 12
    return f"{hh:02d}:{mm}"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://www.skyracingworld.com/")
driver.maximize_window()

# Accept cookies
try:
    cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
    cookie_btn.click()
except:
    pass

# Open CALENDAR menu
calendar_li = wait.until(EC.presence_of_element_located((By.XPATH, "//li[a[text()='CALENDAR']]")))
driver.execute_script("arguments[0].classList.add('open');", calendar_li)
time.sleep(1)

# Get submenu links
submenu_items = calendar_li.find_elements(By.CSS_SELECTOR, ".v2_navbar_list_item_submenu-item")
submenu_links = [(item.text.strip(), item.get_attribute("href")) for item in submenu_items]

results = []

for country, url in submenu_links:
    if not url or url.strip() == "#":
        continue

    driver.get(url)
    time.sleep(2)

    # Step 1: collect only valid event links (no href="#")
    event_links = []
    events = driver.find_elements(By.CSS_SELECTOR, "div.event-contianer a.event")
    for ev in events:
        raw_href = ev.get_attribute("href")
        if not raw_href or raw_href.strip() == "#":
            continue  # skip placeholders
        event_links.append(raw_href)

    # Step 2: visit each event link separately
    for raw_href in event_links:
        driver.get(raw_href)
        time.sleep(1)

        # Track name
        try:
            track_name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
        except:
            track_name = ""

        # Race date from URL
        match_date = re.search(r"\d{4}-\d{2}-\d{2}", raw_href)
        race_date = match_date.group(0) if match_date else ""

        # Table rows
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table.rns-table tbody tr")
        except:
            rows = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 7:
                race_no = re.sub(r"\D", "", cols[0].text.strip())
                post_time = clean_time(cols[1].text.strip())
                distance = cols[3].text.strip()
                race_class = cols[4].text.strip()
                prize_money = cols[5].text.strip()
                starters = cols[6].text.strip()

                # Only append if race_no and post_time exist (avoid blank lines)
                if race_no and post_time:
                    results.append([
                        country,      # Sub-menu name
                        track_name,   # Track name
                        race_date,    # Race date
                        race_no,      # Race number
                        starters,     # Number of starters
                        post_time,    # Post time HH:MM
                        distance,     # Distance
                        race_class,   # Class
                        prize_money   # Prize money
                    ])

# Save to CSV
with open("race_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Sub-menu name",
        "Track name",
        "Race date",
        "Race number",
        "Number of Starters",
        "Post Time",
        "Distance",
        "Class",
        "Prize Money"
    ])
    writer.writerows(results)

driver.quit()
print("Saved race_data.csv")
