# src/engine/executor/tool/tools/local/fetch_website_text.py

from engine.executor.tool.tool_base import ToolBase

class FetchWebsiteText(ToolBase):
    # 类变量初始化为None
    webdriver = None
    Service = None
    ChromeDriverManager = None
    time = None
    BeautifulSoup = None
    By = None
    WebDriverWait = None
    expected_conditions = None
    
    def __init__(self):
        super().__init__()
        globals()['webdriver'] = self.import_or_install('selenium').webdriver
        globals()['Service'] = self.import_or_install('selenium.webdriver.chrome.service').Service
        globals()['ChromeDriverManager'] = self.import_or_install('webdriver_manager.chrome').ChromeDriverManager
        globals()['time'] = self.import_or_install('time')
        globals()['BeautifulSoup'] = self.import_or_install('bs4').BeautifulSoup
        globals()['By'] = self.import_or_install('selenium.webdriver.common.by').By
        globals()['WebDriverWait'] = self.import_or_install('selenium.webdriver.support.ui').WebDriverWait
        globals()['expected_conditions'] = self.import_or_install('selenium.webdriver.support.expected_conditions')
        
    @staticmethod
    def metadata():
        return {
            "id": "search.search_url2text_dynamic",
            "name": "url2text",
            "description": "基于url，提取动态加载网页的纯文本内容，并去除多余的空格和换行符。",
            "inputs": [
                {"name": "url", "type": "string", "description": "目标网页的URL"}
            ],
            "outputs": [
                {"name": "text", "type": "string", "description": "提取的纯文本内容"}
            ]
        }

    def run(self, inputs):
        url = inputs.get("url")
        if not url:
            raise ValueError("URL is required.")

        driver = None
        try:
            # 设置Chrome选项
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # 设置隐式等待
            driver.implicitly_wait(10)
            
            # 获取页面
            driver.get(url)
            
            # 等待页面加载完成（可以根据具体页面调整等待条件）
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator=' ')
            text = ' '.join(text.split())
            return {"text": text}

        except webdriver.WebDriverException as e:
            raise ValueError(f"WebDriver error for URL {url}: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching URL {url}: {e}")
        finally:
            if driver:
                driver.quit()