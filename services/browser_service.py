import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config

class BrowserService:
    def __init__(self):
        self.options = self._get_options()
        self.driver = None

    def _get_options(self):
        opt = Options()
        opt.add_argument("--headless=new")
        opt.add_argument("--disable-gpu")
        opt.add_argument("--no-sandbox")
        opt.page_load_strategy = 'eager'
        # Bloqueia imagens para performance
        opt.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        return opt

    def perform_login(self):
        self.driver = webdriver.Chrome(options=self.options)
        wait = WebDriverWait(self.driver, 10)
        
        try:
            self.driver.get(Config.URL)
            
            # Login
            user_input = wait.until(EC.presence_of_element_located((By.XPATH, Config.XPATH_USER)))
            user_input.send_keys(Config.USER)
            
            pass_input = self.driver.find_element(By.XPATH, Config.XPATH_PASS)
            pass_input.send_keys(Config.PASS + Keys.ENTER)

            # Polling otimizado para extração do Token
            for _ in range(20):
                token = self.driver.execute_script("""
                    return Object.keys(localStorage)
                        .filter(k => k.toLowerCase().includes('token'))
                        .map(k => localStorage.getItem(k))[0];
                """)
                if token: return token
                time.sleep(0.5)
            return None
        finally:
            self.driver.quit()