import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot
from dotenv import load_dotenv

# ---------------- Load environment variables ----------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USERNAME = os.getenv("ROYALCALL_USERNAME")
PASSWORD = os.getenv("ROYALCALL_PASSWORD")

bot = Bot(token=TOKEN)

# ---------------- Selenium setup ----------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=chrome_options)

# ---------------- URLs ----------------
LOGIN_URL = "https://royalcall.net/login"
LIVE_CALLS_URL = "https://royalcall.net/live/calls"

# ---------------- Functions ----------------
def login():
    driver.get(LOGIN_URL)
    time.sleep(5)  # allow JS to load

    try:
        # Email input
        email_input = None
        for locator in [
            (By.NAME, "email"), 
            (By.ID, "email"), 
            (By.CSS_SELECTOR, "input[placeholder='Your Email Address']")
        ]:
            try:
                email_input = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(locator)
                )
                break
            except:
                continue

        if not email_input:
            driver.save_screenshot("/tmp/login_error.png")
            raise Exception("Email input not found, screenshot saved: /tmp/login_error.png")

        email_input.send_keys(USERNAME)  # YOUR EMAIL HERE

        # Password input
        password_input = None
        for locator in [
            (By.NAME, "password"), 
            (By.ID, "password"), 
            (By.CSS_SELECTOR, "input[placeholder='Password']")
        ]:
            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(locator)
                )
                break
            except:
                continue

        if not password_input:
            driver.save_screenshot("/tmp/login_error.png")
            raise Exception("Password input not found, screenshot saved: /tmp/login_error.png")

        password_input.send_keys(PASSWORD)

        # Sign In button
        sign_in_button = None
        for locator in [
            (By.XPATH, "//button[text()='Sign In']"),
            (By.CSS_SELECTOR, "button[type='submit']")
        ]:
            try:
                sign_in_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except:
                continue

        if not sign_in_button:
            driver.save_screenshot("/tmp/login_error.png")
            raise Exception("Sign In button not found, screenshot saved: /tmp/login_error.png")

        sign_in_button.click()

        # Wait for login to complete (you can wait for a unique element after login)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#live-calls"))  # example selector
        )
        print("Logged in successfully!")

    except Exception as e:
        print("Login failed:", e)
        raise e
def get_live_calls():
    driver.get(LIVE_CALLS_URL)
    time.sleep(5)  # wait for JS
    try:
        WebDriverWait(driver, 15).until(
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
