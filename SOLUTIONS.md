# Ozon 403错误解决方案

由于Ozon有严格的反爬虫机制，可能会遇到403 Forbidden错误。以下是几种解决方案：

## 方案1: 使用代理IP（推荐）

Ozon可能封禁了云服务器IP段。使用代理可以绕过IP封锁。

### 修改 `ozon_scraper.py`

```python
class OzonScraper:
    def __init__(self, proxy=None):
        self.session = requests.Session()
        
        # 如果提供代理，设置代理
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy,
            }
        
        # ... 其余代码
```

### 使用方式

```python
# 使用代理
scraper = OzonScraper(proxy='http://username:password@proxy-server:port')
# 或使用SOCKS5代理
scraper = OzonScraper(proxy='socks5://username:password@proxy-server:port')
```

### 获取代理服务

- [Bright Data](https://brightdata.com/)
- [Oxylabs](https://oxylabs.io/)
- [SmartProxy](https://smartproxy.com/)
- 或搜索俄罗斯本地代理服务

## 方案2: 使用Selenium + 无头浏览器

真实浏览器可以完全绕过反爬虫检测。

### 安装依赖

```bash
pip install selenium webdriver-manager
```

### 创建 `selenium_scraper.py`

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

class SeleniumOzonScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def get_product_info(self, product_id):
        url = f"https://www.ozon.ru/product/-{product_id}/"
        self.driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 提取页面数据
        page_source = self.driver.page_source
        
        # 关闭浏览器
        # self.driver.quit()
        
        return page_source
```

## 方案3: 使用现有的Ozon API服务

一些第三方服务提供Ozon数据API：

- **RapidAPI** - 搜索 "Ozon API"
- **ScraperAPI** - 提供反反爬虫服务
- **Apify** - Ozon scraper actors

## 方案4: 手动解决验证后使用Cookie

1. 在浏览器访问 Ozon.ru
2. 通过人机验证（如果有）
3. 复制浏览器Cookie
4. 在代码中使用这些Cookie

```python
scraper = OzonScraper()
scraper.session.cookies.update({
    'cookie_name': 'cookie_value',
    # 添加所有必要的cookie
})
```

## 当前建议

鉴于403错误持续存在，建议：

1. **首选**: 购买俄罗斯本地代理IP
2. **备选**: 使用Selenium方案（但速度较慢）
3. **临时**: 手动获取cookie并每天更新

## 检查403响应

运行爬虫后，查看生成的 `debug_403.html` 文件，看是否有：
- Cloudflare验证页面
- 人机验证（CAPTCHA）
- IP封禁信息
- 其他反爬虫提示
