# src/engine/executor/tool/tools/local/fetch_website_text.py
from engine.executor.tool.tool_base import ToolBase

class FetchWebsiteText(ToolBase):
    def __init__(self):
        super().__init__()
        globals()['requests'] = self.import_or_install('requests')
        globals()['BeautifulSoup'] = self.import_or_install('bs4').BeautifulSoup
        # self.import_or_install('requests')
        # import requests
        # self.requests = requests
        # globals()['requests'] = requests
        # self.import_or_install('bs4')
        # from bs4 import BeautifulSoup
        # self.BeautifulSoup = BeautifulSoup
        
    @staticmethod
    def metadata():
        return {
            "id": "search.search_url2text_static",
            "name": "url2text",
            "description": "基于url，提取静态加载网页的纯文本内容，并去除多余的空格和换行符。",
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

        try:
            # 添加必要的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': url,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            proxies = None
            response = requests.get(url, headers=headers, proxies=proxies)
            response.raise_for_status()
            # 检测网页编码
            encoding = response.encoding
            if 'charset' in response.headers.get('Content-Type', '').lower():
                encoding = response.headers['Content-Type'].split('charset=')[-1]
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                meta_tag = soup.find('meta', charset=True)
                if meta_tag:
                    encoding = meta_tag['charset']
                else:
                    meta_tag = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
                    if meta_tag:
                        content = meta_tag.get('content', '')
                        if 'charset=' in content:
                            encoding = content.split('charset=')[-1]

            # 设置编码
            response.encoding = encoding

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ')
            text = ' '.join(text.split())
            return {"text": text}

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching the URL: {url}. Error: {e}")