from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, random
import requests

SURVEY_URL = "https://www.surveymonkey.com/r/Draeger-VN-Medical-Maintenance"
NUM_SUBMISSIONS = 2
MIN_DELAY = 10
MAX_DELAY = 15

PROXIES = [
    "23.227.39.77:8080",
    "47.243.181.85:8080",
    "188.42.88.238:8080"    # ... thêm proxy khác ...
]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
]

def prepare_chrome_options(proxy=None, ua=None, headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    if ua:
        opts.add_argument(f"--user-agent={ua}")
    if proxy:
        opts.add_argument(f"--proxy-server=http://{proxy}")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    return opts

def run_single_submit(proxy=None, ua=None, verbose=True):
    opts = prepare_chrome_options(proxy=proxy, ua=ua, headless=False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    wait = WebDriverWait(driver, 20)
    success = False
    try:
        driver.get(SURVEY_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        # Q1. Mức độ hài lòng của bạn về Bảo trì, Bảo dưỡng của Dräger
        driver.find_element(By.CSS_SELECTOR, "input[value='2964384505']").click()

        # Q2. Dịch vụ trả lời qua điện thoại của Dräger
        driver.find_element(By.CSS_SELECTOR, "input[name='447341760_2964384511'][value='2964384515']").click()

        # Q3. Kỹ sư của Dräger có thái độ làm việc chuyên nghiệp tại nơi làm việc không?
        driver.find_element(By.CSS_SELECTOR, "input[name='447341761_2964384516'][value='2964384520']").click()

        # Q4. Chất lượng chuyên môn kỹ thuật của kỹ sư Dräger
        driver.find_element(By.CSS_SELECTOR, "input[name='447341762_2964384521'][value='2964384525']").click()

        # Q5. Kỹ sư của Dräger có giữ gìn vệ sinh cẩn thận và tuân thủ các quy định an toàn khi làm việc hay không?
        driver.find_element(By.CSS_SELECTOR, "input[name='447341763_2964384526'][value='2964384530']").click()

        # Q6. Sự đáp ứng linh phụ kiện
        driver.find_element(By.CSS_SELECTOR, "input[name='447341764_2964384531'][value='2964384535']").click()

        # Q7. Tần suất bảo trì thiết bị hoặc thời gian thực hiện bảo trì
        driver.find_element(By.CSS_SELECTOR, "input[name='447341765_2964384536'][value='2964384540']").click()

        # Q8. Cách báo cáo về tình hình bảo trì và cách giao tiếp
        driver.find_element(By.CSS_SELECTOR, "input[name='451601467_2991507241'][value='2991507245']").click()

        # Q9. Tính linh hoạt và hợp tác của nhân viên Dräger khi trả lời bạn
        driver.find_element(By.CSS_SELECTOR, "input[name='447341770_2964384555'][value='2964384559']").click()

        # Q10. Sự đáp ứng của thiết bị Dräger
        driver.find_element(By.CSS_SELECTOR, "input[name='451601498_2991507409'][value='2991507413']").click()

        # Q11. Công việc có được thực hiện theo hướng dẫn An toàn lao động hay không?
        driver.find_element(By.CSS_SELECTOR, "input[name='447341771'][value='2964384560']").click()

        # Q12. Bạn sẽ giới thiệu về Dräger với đồng nghiệp?
        driver.find_element(By.CSS_SELECTOR, "input[name='447341766_2964384541'][value='2964384509']").click()

        # Q13. Nếu bạn có nhu cầu liên hệ với đại diện của Dräger, vui lòng cung cấp email của bạn tại đây.
        driver.find_element(By.CSS_SELECTOR, "input[name='447341769_2964384551']").send_keys(f"test{random.randint(1000,9999)}@gmail.com")

        # Q14. Bạn có ý kiến nào khác hay không?
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

def is_proxy_working(proxy):
    try:
        resp = requests.get("https://api.ipify.org", proxies={
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }, timeout=5)
        if resp.status_code == 200:
            print(f"Proxy OK: {proxy}, IP: {resp.text}")
            return True
    except Exception as e:
        print(f"Proxy FAIL: {proxy}, Error: {e}")
    return False    

# Lọc proxy sống
PROXIES = [
    p for p in PROXIES if is_proxy_working(p)
]
print(f"Proxy usable: {PROXIES}")

# Main loop
success_count = 0
for i in range(NUM_SUBMISSIONS):
    proxy = random.choice(PROXIES) if PROXIES else None
    ua = random.choice(USER_AGENTS)
    print(f"\n=== Submission {i+1}/{NUM_SUBMISSIONS} (proxy={proxy}, ua={ua}) ===")
    ok = run_single_submit(proxy=proxy, ua=ua, verbose=True)
    if ok:
        success_count += 1
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Waiting {delay:.1f}s before next run...")
    time.sleep(delay)

print(f"\nDone. Success: {success_count}/{NUM_SUBMISSIONS}")
