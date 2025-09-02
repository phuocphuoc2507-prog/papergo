# config.py

# --- Cấu hình Camera & AI ---
# Sử dụng camera mặc định của máy
CAMERA_INDEX = 0
# DeepFace hỗ trợ nhiều mô hình, ArcFace cân bằng giữa tốc độ và độ chính xác
MODEL_NAME = "ArcFace"
# Backend phát hiện khuôn mặt, 'ssd' nhẹ và nhanh
DETECTOR_BACKEND = 'ssd'
# Ngưỡng nhận diện (càng thấp càng chính xác, 1.2 là giá trị tốt cho ArcFace)
RECOGNITION_THRESHOLD = 1.2

# --- Cấu hình Logic hệ thống ---
# Thời gian (giây) chờ nhận diện trước khi coi là người lạ
RECOGNITION_TIMEOUT_S = 15
# Thời gian (giây) chờ người dùng xác nhận
CONFIRMATION_TIMEOUT_S = 10
# Số lượng ảnh của người lạ cần lưu lại
NUM_UNKNOWN_FACES_TO_SAVE = 5
# Thời gian (giây) cho phép người dùng bỏ giấy vào thùng
WEIGHING_DURATION_S = 15

# --- Cấu hình Thùng rác & Cân ---
# Sức chứa tối đa của mỗi thùng (kg)
BIN_CAPACITY_KG = 10.0

# --- Cấu hình Phần cứng (QUAN TRỌNG) ---
# Hãy kiểm tra cổng COM trong Device Manager và điền vào đây
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

# --- Đường dẫn File ---
DATASET_PATH = "dataset/"
DATABASE_PATH = "database/"
METADATA_FILE = "metadata.csv"
RECYCLING_LOG_FILE = "recycling_log.csv"
UNIDENTIFIED_PATH = "unidentified/"