# config.py

# --- Cấu hình Camera & AI ---
CAMERA_INDEX = 0
MODEL_NAME = "ArcFace"
RECOGNITION_THRESHOLD = 1.2
DETECTOR_BACKEND = 'ssd'

# --- Cấu hình Logic hệ thống ---
PROXIMITY_THRESHOLD_CM = 100
RECOGNITION_TIMEOUT_S = 15
CONFIRMATION_TIMEOUT_S = 10
NUM_UNKNOWN_FACES_TO_SAVE = 5
WEIGHING_DURATION_S = 15 # Thời gian (giây) cho phép bỏ giấy

# --- Cấu hình Thùng rác & Cân ---
BIN_CAPACITY_KG = 10.0
# XÓA BỎ: Không cần chỉ định cân mặc định nữa
# ACTIVE_BIN_INDEX = 1

# --- CẤU HÌNH PHẦN CỨNG (MỚI) ---
SERIAL_PORT = 'COM4'  # QUAN TRỌNG: Thay 'COM4' bằng cổng COM thật của ESP32
BAUD_RATE = 115200

# --- Đường dẫn File ---
DATASET_PATH = "dataset/"
DATABASE_PATH = "database/"
METADATA_FILE = "metadata.csv"
RECYCLING_LOG_FILE = "recycling_log.csv"
UNIDENTIFIED_PATH = "unidentified/"