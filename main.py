import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot
from dotenv import load_dotenv

# ---------------- Load .env ----------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USERNAME = os.getenv("ROYALCALL_USERNAME")
PASSWORD = os.getenv("ROYALCALL_PASSWORD")

bot = Bot(token=TOKEN)

# ---------------- Selenium Setup ----------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

# ---------------- URLs ----------------
LOGIN_URL = "https://www.orangecarrier.com/login"
LIVE_CALLS_URL = "https://www.orangecarrier.com/live/calls/test"

# ---------------- Functions ----------------
def login():
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='Sign In']").click()
    WebDriverWait(driver, 10).until(EC.url_changes(LOGIN_URL))
    print("Logged in successfully!")

def get_live_calls():
    driver.get(LIVE_CALLS_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

    rows = driver.find_elements(By.TAG_NAME, "tr")
    calls = []

    for row in rows:
        text = row.text.strip()
        if text and "No calls" not in text:
            calls.append(text)
    
    return calls

def send_to_telegram(calls):
    for call in calls:
        bot.send_message(chat_id=CHAT_ID, text=f"New call: {call}")

def main_loop():
    seen_calls = set()
    while True:
        try:
            calls = get_live_calls()
            new_calls = [c for c in calls if c not in seen_calls]

            if new_calls:
                send_to_telegram(new_calls)
                seen_calls.update(new_calls)

            time.sleep(60)
        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# ---------------- Main ----------------
if __name__ == "__main__":
    login()
    main_loop()
