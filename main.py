# submit_many.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, random, datetime

# ----------------- CẤU HÌNH -----------------
FORM_URL = "https://forms.office.com/Pages/ResponsePage.aspx?id=qJfY6AD0JUaFim865idUK4WNzlqwLltJn-0vMv0IEfFUMzZTQVEwT1JEQ1JYVERKUFg4Tk01VU9UTS4u&origin=Invitation&channel=0"

num_submissions = 2       # số lần muốn submit
min_delay = 5             # delay tối thiểu giữa 2 lượt (giây)
max_delay = 12            # delay tối đa giữa 2 lượt (giây)

PROXIES = []  # ví dụ: ["1.2.3.4:8080"]

TEXT_SAMPLE = "AutoTest"
FORM_DATE = None
# --------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
]

def get_date_string():
    if FORM_DATE:
        return FORM_DATE
    d = datetime.date.today()
    return f"{d.month}/{d.day}/{d.year}"

def click_element(driver, el):
    try:
        el.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            return False

def prepare_chrome_options(proxy=None, ua=None, headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    if ua:
        opts.add_argument(f"--user-agent={ua}")
    if proxy:
        opts.add_argument(f"--proxy-server=http://{proxy}")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    return opts

def run_single_submit(proxy=None, ua=None, verbose=True):
    opts = prepare_chrome_options(proxy=proxy, ua=ua, headless=True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    wait = WebDriverWait(driver, 20)
    success = False
    try:
        driver.get(FORM_URL)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-automation-id='questionItem']")))
        time.sleep(0.7)

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='questionItem']")
        if verbose: print(f"Found {len(items)} questions")

        for idx, item in enumerate(items, start=1):
            filled = False
            # Date
            try:
                date_el = item.find_element(By.CSS_SELECTOR, "input[aria-label='Date picker'], input[id^='DatePicker']")
                date_str = get_date_string()
                date_el.clear()
                date_el.send_keys(date_str)
                if verbose: print(f"Q{idx}: filled date {date_str}")
                filled = True
            except Exception:
                pass

            # Text
            if not filled:
                try:
                    t = item.find_element(By.CSS_SELECTOR, "input[data-automation-id='textInput'], textarea, input[type='text']:not([aria-label='Date picker'])")
                    aria = (t.get_attribute("aria-label") or "").lower()
                    if "email" in aria:
                        t.send_keys("test@example.com")
                    else:
                        t.send_keys(f"{TEXT_SAMPLE} #{idx}")
                    if verbose: print(f"Q{idx}: filled text")
                    filled = True
                except Exception:
                    pass

            # Choice input
            if not filled:
                try:
                    choice_input = item.find_element(By.CSS_SELECTOR, "div[data-automation-id='choiceItem'] input[type='radio'], div[data-automation-id='choiceItem'] input[type='checkbox']")
                    ok = click_element(driver, choice_input)
                    if verbose: print(f"Q{idx}: clicked first input choice (ok={ok})")
                    filled = True
                except Exception:
                    pass

            # Choice div
            if not filled:
                try:
                    choice_div = item.find_element(By.CSS_SELECTOR, "div[data-automation-id='choiceItem']")
                    ok = click_element(driver, choice_div)
                    if verbose: print(f"Q{idx}: clicked choice div (ok={ok})")
                    filled = True
                except Exception:
                    pass

            # Fallback role radio
            if not filled:
                try:
                    r = item.find_element(By.CSS_SELECTOR, "div[role='radio'], div[role='option'], label[role='radio']")
                    ok = click_element(driver, r)
                    if verbose: print(f"Q{idx}: clicked role-radio (ok={ok})")
                    filled = True
                except Exception:
                    pass

            if not filled and verbose:
                print(f"Q{idx}: nothing filled (skipped)")

        # Submit
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-automation-id='submitButton'], button[type='submit']")))
        click_element(driver, submit_btn)
        if verbose: print("Clicked submit")

        # Confirm
        try:
            thank = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation-id='thankYouMessage'], div[data-automation-id='thankYouPage']")))
            if verbose: print("Submission confirmed:", thank.text.strip())
            success = True
        except Exception:
            body = driver.find_element(By.TAG_NAME, "body").text
            if any(k in body for k in ["submitted", "Thank", "Thanks", "đã gửi", "cảm ơn"]):
                if verbose: print("Submission likely successful (body text).")
                success = True
            else:
                if verbose: print("Submission uncertain.")
                success = False

    except Exception as e_main:
        if verbose: print("Error in run_single_submit:", e_main)
        success = False
    finally:
        try:
            driver.quit()
        except:
            pass
    return success

# ----------------- Main loop -----------------
success_count = 0
for i in range(num_submissions):
    proxy = random.choice(PROXIES) if PROXIES else None
    ua = random.choice(USER_AGENTS)
    print(f"\n=== Submission {i+1}/{num_submissions} (proxy={proxy}, ua chosen) ===")
    ok = run_single_submit(proxy=proxy, ua=ua, verbose=True)
    if ok:
        success_count += 1
    if i < num_submissions - 1:  # không delay sau lần cuối
        delay = random.uniform(min_delay, max_delay)
        print(f"Waiting {delay:.1f}s before next run...")
        time.sleep(delay)

print(f"\nDone. Success: {success_count}/{num_submissions}")
