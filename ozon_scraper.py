import requests
import json
import time
import re
from typing import Dict, Optional


class OzonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'DNT': '1',
        })
        self.initialized = False
    
    def _initialize_session(self):
        """访问首页建立session和cookie"""
        if self.initialized:
            return
        
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
            }
            response = self.session.get('https://www.ozon.ru/', headers=headers, timeout=15)
            time.sleep(2)
            self.initialized = True
        except Exception as e:
            print(f"初始化session失败: {e}")

    def get_product_info(self, product_id: str) -> Optional[Dict]:
        """
        根据商品ID获取Ozon商品信息
        
        Args:
            product_id: Ozon商品ID
            
        Returns:
            包含商品信息的字典，如果失败返回None
        """
        try:
            self._initialize_session()
            
            time.sleep(1)
            
            url = f"https://www.ozon.ru/product/-{product_id}/"
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': 'https://www.ozon.ru/',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            
            response = self.session.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            html_content = response.text
            
            data = self._extract_json_from_html(html_content)
            
            if not data:
                print("无法从页面提取数据")
                return None
            
            product_info = self._parse_product_data(data, product_id)
            return product_info
            
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"发生错误: {e}")
            return None
    
    def _extract_json_from_html(self, html: str) -> Optional[Dict]:
        """从HTML中提取嵌入的JSON数据"""
        try:
            pattern = r'<script[^>]*>\s*window\.__NUXT__\s*=\s*({.*?});?\s*</script>'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                data = json.loads(json_str)
                return data
            
            pattern2 = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            match2 = re.search(pattern2, html, re.DOTALL)
            
            if match2:
                json_str = match2.group(1)
                data = json.loads(json_str)
                return data
            
            pattern3 = r'"layout":\s*(\[.*?\])'
            match3 = re.search(pattern3, html, re.DOTALL)
            
            if match3:
                try:
                    layout_data = json.loads(match3.group(1))
                    return {'layout': layout_data}
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"提取JSON数据时出错: {e}")
            return None

    def _parse_product_data(self, data: Dict, product_id: str) -> Dict:
        """解析页面数据"""
        product_info = {
            'product_id': product_id,
            'url': f"https://www.ozon.ru/product/-{product_id}/",
            'title': '',
            'price': '',
            'old_price': '',
            'rating': '',
            'reviews_count': '',
            'description': '',
            'images': [],
            'characteristics': {},
            'seller': '',
            'availability': ''
        }

        try:
            layout_data = data.get('layout', [])
            
            if isinstance(data, dict) and 'props' in data:
                page_props = data.get('props', {}).get('pageProps', {})
                if 'layout' in page_props:
                    layout_data = page_props.get('layout', [])
            
            for widget in layout_data:
                if not isinstance(widget, dict):
                    continue
                    
                widget_state = widget.get('state', {})
                
                component_name = widget.get('component', '')
                
                if 'Gallery' in component_name or 'webGallery' in component_name:
                    images = widget_state.get('images', [])
                    product_info['images'] = [img.get('src', '') or img.get('link', '') for img in images if img.get('src') or img.get('link')]
                
                if 'Heading' in component_name or 'webProductHeading' in component_name:
                    product_info['title'] = widget_state.get('title', '') or widget_state.get('name', '')
                    product_info['rating'] = str(widget_state.get('rating', '') or widget_state.get('reviewRating', ''))
                    product_info['reviews_count'] = str(widget_state.get('reviewsCount', '') or widget_state.get('reviews', ''))
                
                if 'Price' in component_name or 'webPrice' in component_name:
                    price_data = widget_state.get('price', widget_state)
                    product_info['price'] = price_data.get('price', '') or price_data.get('currentPrice', '')
                    product_info['old_price'] = price_data.get('originalPrice', '') or price_data.get('oldPrice', '')
                
                if 'Description' in component_name or 'webDescription' in component_name:
                    product_info['description'] = widget_state.get('text', '') or widget_state.get('description', '')
                
                if 'Characteristics' in component_name or 'webCharacteristics' in component_name:
                    chars = widget_state.get('characteristics', [])
                    for char in chars:
                        key = char.get('key', '') or char.get('name', '')
                        values = char.get('values', [])
                        if key and values:
                            product_info['characteristics'][key] = ', '.join([v.get('text', '') or str(v.get('value', '')) for v in values])
                
                if 'Seller' in component_name or 'webSeller' in component_name:
                    product_info['seller'] = widget_state.get('title', '') or widget_state.get('name', '')
                
                if 'AddToCart' in component_name or 'webAddToCart' in component_name:
                    is_available = widget_state.get('isAvailable', widget_state.get('available', False))
                    product_info['availability'] = '有货' if is_available else '无货'

        except Exception as e:
            print(f"解析数据时出错: {e}")

        return product_info

    def save_to_json(self, product_info: Dict, filename: str = None):
        """将商品信息保存为JSON文件"""
        if filename is None:
            filename = f"product_{product_info['product_id']}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(product_info, f, ensure_ascii=False, indent=2)
        
        print(f"商品信息已保存到: {filename}")


def main():
    print("=" * 50)
    print("Ozon商品信息爬虫")
    print("=" * 50)
    
    scraper = OzonScraper()
    
    while True:
        product_id = input("\n请输入Ozon商品ID (输入'q'退出): ").strip()
        
        if product_id.lower() == 'q':
            print("再见！")
            break
        
        if not product_id:
            print("商品ID不能为空！")
            continue
        
        print(f"\n正在爬取商品ID: {product_id}...")
        
        product_info = scraper.get_product_info(product_id)
        
        if product_info:
            print("\n" + "=" * 50)
            print("商品信息:")
            print("=" * 50)
            print(f"标题: {product_info['title']}")
            print(f"价格: {product_info['price']}")
            print(f"原价: {product_info['old_price']}")
            print(f"评分: {product_info['rating']}")
            print(f"评论数: {product_info['reviews_count']}")
            print(f"卖家: {product_info['seller']}")
            print(f"库存状态: {product_info['availability']}")
            print(f"图片数量: {len(product_info['images'])}")
            print(f"特性数量: {len(product_info['characteristics'])}")
            print(f"链接: {product_info['url']}")
            
            save = input("\n是否保存为JSON文件? (y/n): ").strip().lower()
            if save == 'y':
                scraper.save_to_json(product_info)
        else:
            print("获取商品信息失败！")
        
        time.sleep(1)


if __name__ == "__main__":
    main()
