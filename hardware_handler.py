# hardware_handler.py
import serial
import time
import config
import threading

class LoadCell:
    # Biến của class để đảm bảo chỉ có một kết nối và luồng đọc duy nhất
    serial_connection = None
    weights = {1: 0.0, 2: 0.0}
    last_data_received_time = 0
    is_connected = False
    reader_thread = None

    def __init__(self, bin_number):
        self.bin_number = bin_number
        # Chỉ khởi tạo một lần duy nhất
        if LoadCell.reader_thread is None:
            LoadCell.initialize_serial()
        self.mock_weight = 0.0

    @classmethod
    def initialize_serial(cls):
        try:
            cls.serial_connection = serial.Serial(config.SERIAL_PORT, config.BAUD_RATE, timeout=2)
            time.sleep(2) # Chờ kết nối vật lý ổn định
            if cls.serial_connection.isOpen():
                print(f"[HARDWARE] Da ket noi thanh cong voi ESP32 tai cong {config.SERIAL_PORT}")
                cls.is_connected = True
                cls.last_data_received_time = time.time()
                cls.reader_thread = threading.Thread(target=cls.read_serial_data, daemon=True)
                cls.reader_thread.start()
            else:
                 cls.is_connected = False
        except serial.SerialException:
            print(f"!!! LOI: Khong tim thay ESP32 tai cong {config.SERIAL_PORT}. Kiem tra lai ket noi.")
            print("   -> He thong se chay o che do GIA LAP CAN NANG.")
            cls.is_connected = False

    @classmethod
    def read_serial_data(cls):
        while cls.is_connected:
            try:
                if cls.serial_connection and cls.serial_connection.in_waiting > 0:
                    line = cls.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if "Can 1:" in line and "Can 2:" in line:
                        parts = line.split('|')
                        weight1_str = parts[0].split(':')[1].replace('g', '').strip()
                        cls.weights[1] = float(weight1_str) / 1000.0
                        weight2_str = parts[1].split(':')[1].replace('g', '').strip()
                        cls.weights[2] = float(weight2_str) / 1000.0
                        cls.last_data_received_time = time.time()

                if time.time() - cls.last_data_received_time > 5 and cls.last_data_received_time != 0:
                     print("\n!!! Canh bao: Mat ket noi voi ESP32 (khong nhan duoc du lieu).")
                     cls.is_connected = False
            except Exception:
                cls.is_connected = False
            time.sleep(0.1)

    def get_weight(self):
        if LoadCell.is_connected:
            return LoadCell.weights.get(self.bin_number, 0.0)
        else:
            return self.mock_weight

    def add_paper_mock(self, weight_kg):
        if not LoadCell.is_connected:
            self.mock_weight += weight_kg
            print(f"\n[GIA LAP] Ban vua bo them {weight_kg:.3f} kg giay vao thung {self.bin_number}...")