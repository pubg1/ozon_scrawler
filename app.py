from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from ozon_scraper import OzonScraper

app = Flask(__name__)

scraper = OzonScraper()

DATA_DIR = 'scraped_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    product_id = data.get('product_id', '').strip()
    
    if not product_id:
        return jsonify({
            'success': False,
            'error': '商品ID不能为空'
        }), 400
    
    product_info = scraper.get_product_info(product_id)
    
    if not product_info:
        return jsonify({
            'success': False,
            'error': '获取商品信息失败，请检查商品ID是否正确'
        }), 404
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{DATA_DIR}/product_{product_id}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        'success': True,
        'data': product_info,
        'filename': filename
    })


@app.route('/history')
def history():
    files = []
    if os.path.exists(DATA_DIR):
        for filename in sorted(os.listdir(DATA_DIR), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(DATA_DIR, filename)
                files.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                })
    return jsonify(files)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
