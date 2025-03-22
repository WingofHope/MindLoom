# src/engine/executor/tool/tools/local/fetch_website_text.py

from engine.executor.tool.tool_base import toolbase

class FetchWebsiteText:
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

    @staticmethod
    def run(inputs):
        toolbase.import_or_install('selenium')
        toolbase.import_or_install('webdriver_manager')
        toolbase.import_or_install('bs4')
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        from bs4 import BeautifulSoup
        url = inputs.get("url")
        if not url:
            raise ValueError("URL is required.")

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get(url)
            time.sleep(3)
            html = driver.page_source
            driver.quit()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator=' ')
            text = ' '.join(text.split())
            return {"text": text}

        except Exception as e:
            raise ValueError(f"Error fetching the URL: {url}. Error: {e}")