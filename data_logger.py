# data_logger.py
import csv
import os
from datetime import datetime
import config # Import file cấu hình để lấy đường dẫn

# SỬA LỖI: Đổi tên các tham số để khớp với tên cột trong CSV
def log_recycling_event(student_id, ho_ten, lop, khoi_luong_kg, unidentified_folder=None):
    """
    Ghi lại một sự kiện tái chế vào file CSV.
    :param student_id: ID của học sinh (hoặc "UNKNOWN").
    :param ho_ten: Tên học sinh.
    :param lop: Lớp của học sinh.
    :param khoi_luong_kg: Khối lượng giấy đã tái chế.
    :param unidentified_folder: Tên thư mục chứa ảnh người lạ (nếu có).
    """
    file_exists = os.path.isfile(config.RECYCLING_LOG_FILE)
    
    try:
        with open(config.RECYCLING_LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            # Tên các cột trong file CSV
            fieldnames = ['timestamp', 'student_id', 'ho_ten', 'lop', 'khoi_luong_kg', 'unidentified_folder']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()
            
            # SỬA LỖI: Dùng các biến có tên nhất quán
            writer.writerow({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'student_id': student_id,
                'ho_ten': ho_ten,
                'lop': lop,
                'khoi_luong_kg': f"{khoi_luong_kg:.3f}",
                'unidentified_folder': unidentified_folder or ''
            })
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [LOG]: Da ghi nhan su kien tai che: {khoi_luong_kg:.3f} kg")
    except Exception as e:
        print(f"!!! LOI khi ghi file log: {e}")