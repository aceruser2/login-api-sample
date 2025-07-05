import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# 從環境變數獲取設定
BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_USERNAME = os.getenv("TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "admin123")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "./screenshots")

# 確保截圖目錄存在
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)


@pytest.fixture
def driver():
    # 設定 Chrome 選項
    chrome_options = Options()

    # 在 CI/CD 環境中使用 headless 模式
    if os.getenv("CI") == "true":
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 初始化 WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    yield driver

    # 測試結束後關閉瀏覽器
    driver.quit()


def take_screenshot(driver, name):
    """截取螢幕畫面並儲存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOT_DIR}/{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    return filename


class TestRestaurantPOS:

    def test_staff_login(self, driver):
        """測試員工登入功能"""
        # 1. 訪問登入頁面
        driver.get(f"{BASE_URL}/login")
        take_screenshot(driver, "login_page")

        # 2. 選擇「員工登入」選項（如果有多個標籤）
        try:
            staff_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), '員工登入')]")
                )
            )
            staff_tab.click()
        except:
            # 如果沒有標籤，則已經在員工登入頁面
            pass

        # 3. 輸入帳號密碼
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(ADMIN_USERNAME)
        password_field.send_keys(ADMIN_PASSWORD)
        take_screenshot(driver, "login_form_filled")

        # 4. 點擊登入按鈕
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        # 5. 驗證登入成功，應該被導向儀表板或首頁
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
        take_screenshot(driver, "dashboard_after_login")

        # 驗證當前 URL
        current_url = driver.current_url
        assert "/dashboard" in current_url, f"Expected dashboard URL, got {current_url}"

    def test_order_process(self, driver):
        """測試下單流程"""
        # 1. 首先需要登入
        self.test_staff_login(driver)

        # 2. 導航到菜單頁面
        driver.get(f"{BASE_URL}/menu")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h4[contains(text(), '菜單管理')]")
            )
        )
        take_screenshot(driver, "menu_page")

        # 3. 選擇菜單項目並加入購物車
        try:
            # 嘗試點擊第一個"加入"按鈕
            add_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), '加入')]")
                )
            )
            add_button.click()
            time.sleep(1)  # 短暫等待購物車更新
            take_screenshot(driver, "item_added_to_cart")

            # 4. 點擊結帳按鈕
            checkout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), '結帳')]")
                )
            )
            checkout_button.click()

            # 5. 確認訂單
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), '確認支付')]")
                )
            )
            take_screenshot(driver, "checkout_dialog")
            confirm_button.click()

            # 6. 驗證訂單成功
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), '訂單提交並付款成功')]")
                )
            )
            take_screenshot(driver, "order_success")

        except Exception as e:
            take_screenshot(driver, "order_process_error")
            pytest.fail(f"訂單流程失敗: {str(e)}")

    def test_report_page(self, driver):
        """測試報表頁面"""
        # 1. 首先需要登入
        self.test_staff_login(driver)

        # 2. 導航到報表頁面
        driver.get(f"{BASE_URL}/reports")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), '報表')]"))
        )
        take_screenshot(driver, "reports_page")

        # 3. 檢查日銷售報表是否加載
        try:
            sales_report = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "daily-sales-chart"))
            )
            assert sales_report.is_displayed(), "日銷售報表未顯示"
            take_screenshot(driver, "sales_report")

        except Exception as e:
            take_screenshot(driver, "reports_page_error")
            pytest.fail(f"報表頁面載入失敗: {str(e)}")
