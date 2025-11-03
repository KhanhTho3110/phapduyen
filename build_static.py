import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader # Chúng ta cần thư viện này

print("--- Bắt đầu script build_static.py ---")

# --- LINK CSV CỦA BẠN ---
# (Hãy chắc chắn đây là link CSV đã "Publish to the web")
PRODUCT_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHOvfG4hGVCBQYsjOpC0QhamhVKWwFojz4IRc32B6HOvRDaEqc9dNRy8E8pLyJDnDo2mGvJ4oJANtk/pub?gid=319581950&single=true&output=csv"
VIDEO_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHOvfG4hGVCBQYsjOpC0QhamhVKWwFojz4IRc32B6HOvRDaEqc9dNRy8E8pLyJDnDo2mGvJ4oJANtk/pub?gid=1503614356&single=true&output=csv"
ANALYTICS_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSHOvfG4hGVCBQYsjOpC0QhamhVKWwFojz4IRc32B6HOvRDaEqc9dNRy8E8pLyJDnDo2mGvJ4oJANtk/pub?gid=1732750877&single=true&output=csv"
# -------------------------------------

def load_data(url):
    """Hàm tải dữ liệu từ Google Sheet CSV."""
    try:
        df = pd.read_csv(url, dtype=str)
        df = df.fillna("")
        print(f"Đã tải thành công {len(df)} dòng từ {url.split('gid=')[1]}")
        return df.to_dict('records')
    except Exception as e:
        print(f"[LỖI LOAD_DATA] Lỗi khi tải dữ liệu từ {url}: {e}")
        return []

def process_data(products_raw, videos_raw):
    """Xử lý dữ liệu thô (giống hệt code cũ của bạn)."""
    products_processed = []
    
    # Xử lý Sản phẩm
    print("Đang xử lý dữ liệu sản phẩm...")
    for product in products_raw:
        try:
            # Đọc từ cột 'image_id'
            file_id = product.get('image_id') 
            if file_id:
                product['image_url_processed'] = f"https://drive.google.com/thumbnail?id={file_id}&sz=w500"
            else:
                product['image_url_processed'] = "https://placehold.co/300x300/eee/333?text=No+Image"
            
            # Đọc từ cột 'link_shopee'
            shopee_link = product.get('link_shopee', '') 
            if shopee_link and not shopee_link.startswith(('http://', 'https://')):
                product['shopee_link_processed'] = f"https://{shopee_link}"
            elif not shopee_link:
                product['shopee_link_processed'] = '#' 
            else:
                product['shopee_link_processed'] = shopee_link
            
            products_processed.append(product)
        except Exception as e:
            print(f"Lỗi xử lý sản phẩm {product.get('name')}: {e}")
            continue
            
    # Xử lý Video (chỉ cần tải)
    videos_processed = videos_raw
    
# --- BỘ LỌC VÀ TÍNH TOÁN ANALYTICS MỚI ---
    df_analytics = pd.DataFrame(analytics_raw)
    
    # Tính toán các chỉ số
    total_requests = len(df_analytics) if not df_analytics.empty else 0
    unique_visitors = df_analytics['User_ID'].nunique() if not df_analytics.empty else 0
    
    # Đếm các sự kiện cụ thể
    if not df_analytics.empty:
        # Chuyển đổi thành string để tránh lỗi
        events = df_analytics['Event_Type'].astype(str) 
        click_product = len(events[events == 'CLICK_PRODUCT'])
        click_video = len(events[events == 'CLICK_VIDEO'])
        click_donate = len(events[events == 'CLICK_DONATE'])
    else:
        click_product, click_video, click_donate = 0, 0, 0
    
    stats = {
        'total_visits': total_requests,
        'unique_visitors': unique_visitors,
        'click_product': click_product,
        'click_video': click_video,
        'click_donate': click_donate
    }
    # ----------------------------------------
    
    print("Đã xử lý xong dữ liệu.")
          
    return products_processed, videos_processed, stats

def build_site():
    """Hàm chính: Tải data, render template và lưu file HTML."""
    
    print("Bắt đầu tải dữ liệu từ Google Sheets...")
    products_raw = load_data(PRODUCT_SHEET_URL)
    videos_raw = load_data(VIDEO_SHEET_URL)
    analytics_raw = load_data(ANALYTICS_SHEET_URL) # <-- Tải thêm data analytics
    
    products, videos, stats = process_data(products_raw, videos_raw, analytics_raw) # <-- 3 biến
    # --- Thiết lập môi trường Template ---
    # 'templates' là tên thư mục chứa file .html của bạn
    env = Environment(loader=FileSystemLoader('templates'))
    
    # Tải file 'index.html' (từ thư mục 'templates')
    template = env.get_template('index.html')
    
    # Render file HTML với data
    print("Đang render file HTML...")

    output_html = template.render(products=products, videos=videos, stats=stats)
    
    # Tạo thư mục 'build' (đây là thư mục mà Cloudflare sẽ publish)
    os.makedirs('build', exist_ok=True)
    
    # Lưu file HTML đã render vào thư mục 'build'
    with open('build/index.html', 'w', encoding='utf-8') as f:
        f.write(output_html)
        
    print("Đã tạo file 'build/index.html' thành công!")

# --- Chạy hàm build ---
if __name__ == '__main__':
    build_site()
    print("--- Script build_static.py đã hoàn tất ---")