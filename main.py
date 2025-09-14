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
chrome_options.add_argument("--headless=new")  # new headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=chrome_options)

# ---------------- URLs ----------------
LOGIN_URL = "https://www.orangecarrier.com/login"
LIVE_CALLS_URL = "https://www.orangecarrier.com/live/calls/test"

# ---------------- Functions ----------------
def login():
    driver.get(LOGIN_URL)
    
    try:
        # wait until username field is visible (handles AJAX)
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # wait until URL changes (login success)
        WebDriverWait(driver, 20).until(EC.url_changes(LOGIN_URL))
        print("Logged in successfully!")
    except Exception as e:
        # save screenshot for debugging
        driver.save_screenshot("/tmp/login_error.png")
        print("Login failed, screenshot saved: /tmp/login_error.png")
        raise e

def get_live_calls():
    driver.get(LIVE_CALLS_URL)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        )
    except Exception as e:
        driver.save_screenshot("/tmp/calls_error.png")
        print("Failed to load calls page, screenshot saved: /tmp/calls_error.png")
        return []

    rows = driver.find_elements(By.TAG_NAME, "tr")
    calls = []

    for row in rows:
        text = row.text.strip()
        if text and "No calls" not in text:
            calls.append(text)
    
    return calls

def send_to_telegram(calls):
    for call in calls:
        try:
            bot.send_message(chat_id=CHAT_ID, text=f"New call: {call}")
        except Exception as e:
            print("Failed to send Telegram message:", e)

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
            print("Error in main loop:", e)
            time.sleep(60)

# ---------------- Main ----------------
if __name__ == "__main__":
    login()
    main_loop()
