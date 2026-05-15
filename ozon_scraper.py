import requests
import json
import time
from typing import Dict, Optional


class OzonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def get_product_info(self, product_id: str) -> Optional[Dict]:
        """
        根据商品ID获取Ozon商品信息
        
        Args:
            product_id: Ozon商品ID
            
        Returns:
            包含商品信息的字典，如果失败返回None
        """
        try:
            url = f"https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=/product/-{product_id}/"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
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

    def _parse_product_data(self, data: Dict, product_id: str) -> Dict:
        """解析API返回的商品数据"""
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
            
            for widget in layout_data:
                if not isinstance(widget, dict):
                    continue
                    
                widget_state = widget.get('state', {})
                
                if 'webGallery' in widget.get('component', ''):
                    images = widget_state.get('images', [])
                    product_info['images'] = [img.get('src', '') for img in images if img.get('src')]
                
                if 'webProductHeading' in widget.get('component', ''):
                    product_info['title'] = widget_state.get('title', '')
                    product_info['rating'] = str(widget_state.get('rating', ''))
                    product_info['reviews_count'] = str(widget_state.get('reviewsCount', ''))
                
                if 'webPrice' in widget.get('component', ''):
                    price_data = widget_state.get('price', {})
                    product_info['price'] = price_data.get('price', '')
                    product_info['old_price'] = price_data.get('originalPrice', '')
                
                if 'webDescription' in widget.get('component', ''):
                    product_info['description'] = widget_state.get('text', '')
                
                if 'webCharacteristics' in widget.get('component', ''):
                    chars = widget_state.get('characteristics', [])
                    for char in chars:
                        key = char.get('key', '')
                        values = char.get('values', [])
                        if key and values:
                            product_info['characteristics'][key] = ', '.join([v.get('text', '') for v in values])
                
                if 'webSeller' in widget.get('component', ''):
                    product_info['seller'] = widget_state.get('title', '')
                
                if 'webAddToCart' in widget.get('component', ''):
                    product_info['availability'] = '有货' if widget_state.get('isAvailable') else '无货'

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
