# Ozon商品信息爬虫

一个用于爬取Ozon平台商品信息的Python工具，提供Web界面和命令行两种使用方式。

## 功能特性

- 根据商品ID获取商品详细信息
- 支持获取多种商品数据：
  - 商品标题
  - 价格（当前价格和原价）
  - 评分和评论数
  - 商品描述
  - 商品图片
  - 商品特性/参数
  - 卖家信息
  - 库存状态
- 支持将商品信息保存为JSON格式
- **美观的Web界面** - 一键爬取，实时显示结果
- 交互式命令行界面
- 历史记录查看

## 安装

### 1. 克隆或下载项目

```bash
cd d:\ozon
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一: Web界面（推荐）

1. 启动Web服务器：

```bash
python app.py
```

2. 打开浏览器访问：`http://localhost:5000`

3. 在输入框中输入商品ID，点击"开始爬取"按钮

4. 查看商品信息，可下载JSON文件或查看历史记录

**Web界面特点：**
- 美观的现代化UI设计
- 实时显示商品信息（标题、价格、图片、评分等）
- 一键下载JSON数据
- 查看历史爬取记录
- 支持远程访问（修改`app.py`中的host参数）

### 方式二: 命令行交互模式

```bash
python ozon_scraper.py
```

运行后按提示输入商品ID即可。

### 如何获取商品ID

Ozon商品ID可以从商品URL中获取，例如：
- URL: `https://www.ozon.ru/product/example-product-123456789/`
- 商品ID: `123456789`

### 在代码中使用

```python
from ozon_scraper import OzonScraper

# 创建爬虫实例
scraper = OzonScraper()

# 获取商品信息
product_id = "123456789"
product_info = scraper.get_product_info(product_id)

if product_info:
    print(f"商品标题: {product_info['title']}")
    print(f"价格: {product_info['price']}")
    
    # 保存为JSON文件
    scraper.save_to_json(product_info)
```

## 输出示例

```json
{
  "product_id": "123456789",
  "url": "https://www.ozon.ru/product/-123456789/",
  "title": "商品标题",
  "price": "1999 ₽",
  "old_price": "2999 ₽",
  "rating": "4.5",
  "reviews_count": "120",
  "description": "商品描述...",
  "images": [
    "https://cdn1.ozon.ru/...",
    "https://cdn1.ozon.ru/..."
  ],
  "characteristics": {
    "品牌": "品牌名称",
    "颜色": "黑色",
    "尺寸": "M"
  },
  "seller": "卖家名称",
  "availability": "有货"
}
```

## 注意事项

1. **请求频率**: 建议在请求之间添加适当的延迟，避免对服务器造成过大压力
2. **网络要求**: 需要能够访问Ozon网站
3. **数据准确性**: 爬取的数据结构可能随Ozon网站更新而变化
4. **使用限制**: 请遵守Ozon的服务条款和robots.txt规则

## 依赖项

- Python 3.7+
- requests
- flask

## 许可

本项目仅供学习和研究使用。
