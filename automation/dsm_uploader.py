from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def upload_file_to_dsm(file_path: str, dsm_url: str, username: str, password: str, quiet: bool = True):
    """
    自動登入 DSM，進入 File Station 的 manager.change 資料夾，執行「上傳 - 覆寫」。
    """
    def log(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 25)
    actions = ActionChains(driver)

    def click_next():
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-btn")))
        if btn.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView({block:'center'})", btn)
            btn.click()
        else:
            print("❌ 按鈕尚未啟用，請確認帳號與密碼輸入是否完成")

    try:
        driver.get(dsm_url)

        # Step 1: 帳號
        user_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form#dsm-user-fieldset input[name='username']")
            )
        )
        user_input.clear()
        user_input.send_keys(username)
        click_next()
        time.sleep(2)

        # Step 2: 密碼
        pass_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form#dsm-pass-fieldset input[type='password']")
            )
        )
        pass_input.clear()
        pass_input.send_keys(password)
        click_next()
        time.sleep(2)

        # Step 3: 等 File Station 圖示
        wait.until(
            EC.any_of(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[normalize-space(text())='File Station']")
                ),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[title='File Station'], [aria-label='File Station']")
                ),
            )
        )
        log("✅ 已登入 DSM")

        # Step 4: 開啟 File Station
        fs_icon = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[title='File Station'], [aria-label='File Station']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", fs_icon)
        fs_icon.click()
        time.sleep(2)

        # Step 5: 進入 manager.change
        manager_change_folder = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(@class, 'webfm-file-type-icon') and contains(text(), 'manager.change')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'})", manager_change_folder)
        actions.move_to_element(manager_change_folder).double_click().perform()
        time.sleep(2)

        # Step 6: 聚焦清單
        try:
            grid = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.x-grid3-body")))
            actions.move_to_element_with_offset(grid, 20, 20).click().perform()
            time.sleep(0.8)
        except Exception:
            pass

        # Step 7: 點「上傳」
        opened = driver.execute_script(
            """
            const btns = Array.from(document.querySelectorAll('button[aria-label="上傳"], button.x-btn-text'));
            const visible = btns.find(b => b.innerText.trim() === '上傳' && b.offsetParent !== null && getComputedStyle(b).visibility !== 'hidden');
            if (visible) { visible.scrollIntoView({block:'center'}); visible.click(); return true; }
            return false;
            """
        )
        if not opened:
            raise Exception("找不到『上傳』按鈕（可見狀態）")
        time.sleep(2)

        # Step 8: 選「上傳 - 覆寫」
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script(
                "return Array.from(document.querySelectorAll('div.x-menu-floating')).some(m => getComputedStyle(m).visibility==='visible');"
            )
        )
        clicked_overwrite = driver.execute_script(
            """
            const menu = Array.from(document.querySelectorAll('div.x-menu-floating'))
                .find(m => getComputedStyle(m).visibility === 'visible');
            if (!menu) return false;
            const target = Array.from(menu.querySelectorAll('span.x-menu-item-text'))
                .find(i => i.textContent.trim() === '上傳 - 覆寫' || i.textContent.includes('覆寫'));
            if (target) { target.click(); return true; }
            return false;
            """
        )
        if not clicked_overwrite:
            raise Exception("可見浮層裡找不到『上傳 - 覆寫』")
        time.sleep(2)

        # Step 9: 送檔案路徑
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file' and not(@disabled)]")))
        file_input.send_keys(file_path)
        time.sleep(2)
        log("✅ 已選擇檔案準備上傳：", file_path)

    finally:
        # 視需要關閉瀏覽器
        # driver.quit()
        pass
