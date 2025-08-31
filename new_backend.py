from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from util import dorm_info, to_cn_number
from datetime import datetime
# import datetime as dt


class new_backend:
    def __init__(self, url, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.url = url
        
    def __del__(self):
        self.driver.quit()
    
    def wait_click(self, parent_selector, selector, innertext=None, timeout=5):
        parent = WebDriverWait(self.driver, timeout, poll_frequency=0.1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, parent_selector))
        )
        time.sleep(0.2)
        elems = parent.find_elements(By.CSS_SELECTOR, selector)
        if not elems:
            raise RuntimeError(f"the element {selector} could not be located")
        
        if innertext:
            try:
                target = next(e for e in elems if e.text == innertext) # returns first
            except StopIteration:
                availables = [e.text for e in elems]
                raise RuntimeError(f"Cannot locate [{innertext}]. Available: {availables}")
        else:
            target = elems[0]
        target.click()
        
    def query(self, dorm: dorm_info) -> tuple[float, datetime]:
        assert dorm.is_new_backend()
        # TODO: optimize
        self.driver.get(self.url)
        self.wait_click("ul.payment-list", "span.word", "校本部公寓电费充值")
        self.wait_click("div.form-body", "section.address-choose.van-hairline--bottom")
        self.wait_click("ul.area-list", "li.item-list.van-hairline--bottom", "北京邮电大学")
        self.wait_click("ul.area-list", "li.item-list.van-hairline--bottom", f"{dorm.bld}号公寓")
        self.wait_click("ul.area-list", "li.item-list.van-hairline--bottom", f"{to_cn_number(dorm.floor)}层")
        self.wait_click("ul.area-list", "li.item-list.van-hairline--bottom", dorm.canonical_id)
        ts = datetime.now()
        time.sleep(0.2)
        elem = self.driver.find_element(By.CSS_SELECTOR, "div.num")
        print("balance:", elem.text)
        return float(elem.text), ts
    
    
if __name__ == "__main__":
    from secret import new_backend_url as url
    b = new_backend(url=url, headless=False)
    d = dorm_info("9-100A")
    q = b.query(d)
    print(q)