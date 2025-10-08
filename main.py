from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import time, random

SURVEY_URL = "https://www.surveymonkey.com/r/Draeger-VN-Medical-Maintenance"
NUM_SUBMISSIONS = 2
MIN_DELAY = 10
MAX_DELAY = 15

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
]

def prepare_chrome_options(ua=None, headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    if ua:
        opts.add_argument(f"--user-agent={ua}")
    # Tạo user-data-dir riêng biệt để tránh xung đột session
    opts.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    return opts

def run_single_submit(ua=None, verbose=True):
    opts = prepare_chrome_options(ua=ua, headless=True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    wait = WebDriverWait(driver, 20)
    success = False
    try:
        driver.get(SURVEY_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        # Q1 - Q14 (giữ nguyên như trước)
        driver.find_element(By.CSS_SELECTOR, "input[value='2964384505']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341760_2964384511'][value='2964384515']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341761_2964384516'][value='2964384520']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341762_2964384521'][value='2964384525']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341763_2964384526'][value='2964384530']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341764_2964384531'][value='2964384535']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341765_2964384536'][value='2964384540']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='451601467_2991507241'][value='2991507245']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341770_2964384555'][value='2964384559']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='451601498_2991507409'][value='2991507413']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341771'][value='2964384560']").click()
        driver.find_element(By.CSS_SELECTOR, "input[name='447341766_2964384541'][value='2964384509']").click()
        # driver.find_element(By.CSS_SELECTOR, "input[name='447341769_2964384551']").send_keys(f"{random.randint(1000,9999)}@gmail.com")
        driver.find_element(By.CSS_SELECTOR, "textarea[name='472992789']").send_keys("Tôi rất hài lòng về dịch vụ của Dräger Việt Nam.")

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"Waiting {delay:.1f}s before submitting...")
        time.sleep(delay)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        if verbose: print("✅ Đã gửi khảo sát thành công!")
        success = True
        time.sleep(3)
    except Exception as e:
        if verbose: print("Error:", e)
        success = False
    finally:
        driver.quit()
    return success

# Main loop
success_count = 0
for i in range(NUM_SUBMISSIONS):
    ua = random.choice(USER_AGENTS)
    print(f"\n=== Submission {i+1}/{NUM_SUBMISSIONS} (ua={ua}) ===")
    ok = run_single_submit(ua=ua, verbose=True)
    if ok:
        success_count += 1
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Waiting {delay:.1f}s before next run...")
    time.sleep(delay)

print(f"\nDone. Success: {success_count}/{NUM_SUBMISSIONS}")

