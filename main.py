# main.py
import time
import cv2
import os
from datetime import datetime
import numpy as np
import random
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import keyboard

# --- KHỞI TẠO CÁC MODULE ---
import config
import hardware_handler
import data_logger
from face_recognizer import FaceRecognizer

# --- KHỞI TẠO FLASK & SOCKETIO ---
app = Flask(__name__)
socketio = SocketIO(app)

# --- CÁC BIẾN TOÀN CỤC ---
state = "IDLE"
load_cell_1 = hardware_handler.LoadCell(bin_number=1)
load_cell_2 = hardware_handler.LoadCell(bin_number=2)
recognizer = FaceRecognizer()
cap = None
recognition_start_time = 0
current_transaction_info = {}
manual_trigger = False

# --- HÀM LẮNG NGHE BÀN PHÍM ---
def key_listener():
    global manual_trigger
    while True:
        try:
            keyboard.wait('h')
            if state == "IDLE":
                print("\n[MANUAL TRIGGER] Da nhan phim 'h'. Kich hoat he thong!")
                manual_trigger = True
        except Exception:
            break

# --- CÁC ROUTE VÀ SỰ KIỆN SOCKETIO ---
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('confirmation_response')
def handle_confirmation(data):
    global state
    if state == "AWAITING_CONFIRMATION":
        if data['response'] == 'yes': state = "WEIGHING"
        else: state = "FAILURE_LEARNING"

@socketio.on('weighing_mock_add')
def handle_weighing_mock():
    # SỬA ĐỔI: Giả lập thêm giấy vào một trong hai cân ngẫu nhiên
    if random.choice([True, False]):
        load_cell_1.add_paper_mock(random.uniform(0.1, 0.5))
    else:
        load_cell_2.add_paper_mock(random.uniform(0.1, 0.5))

# --- HÀM LOGIC CHÍNH ---
def background_thread():
    global state, cap, recognition_start_time, current_transaction_info, manual_trigger

    print("-" * 40)
    print("He thong PaperGo Pro da khoi dong.")
    print("Mo trinh duyet va truy cap http://127.0.0.1:5000")
    print("-" * 40)

    while True:
        if state == "IDLE":
            # ... (Giữ nguyên) ...
            print(f"[{time.strftime('%H:%M:%S')}] Trang thai: CHO. Nhan phim 'h' trong CMD de bat dau.", end='\r')
            if manual_trigger:
                state = "ACTIVATED"
                manual_trigger = False
                print(f"\n[{time.strftime('%H:%M:%S')}] >> Da kich hoat thu cong! Chuyen sang trang thai KICH HOAT.")
            socketio.sleep(0.5)

        elif state == "ACTIVATED":
            # ... (Giữ nguyên) ...
            socketio.emit('update_state', {'state': 'recognizing', 'message': 'Xin hãy nhìn thẳng vào camera...'})
            cap = cv2.VideoCapture(config.CAMERA_INDEX)
            recognition_start_time = time.time()
            state = "RECOGNIZING"

        elif state == "RECOGNIZING":
            # ... (Giữ nguyên) ...
            if not cap or not cap.isOpened(): state = "CLEANUP"; continue
            ret, frame = cap.read()
            if not ret: state = "CLEANUP"; continue
            _, buffer = cv2.imencode('.jpg', frame)
            b64_frame = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('update_frame', {'frame': b64_frame})
            result_package = recognizer.recognize(frame)
            if result_package and result_package.get("info"):
                current_transaction_info = result_package["info"]
                state = "AWAITING_CONFIRMATION"
                recognition_start_time = time.time()
            elif time.time() - recognition_start_time > config.RECOGNITION_TIMEOUT_S:
                state = "FAILURE_LEARNING"
            socketio.sleep(0.05)

        elif state == "AWAITING_CONFIRMATION":
            # ... (Giữ nguyên) ...
            socketio.emit('show_confirmation', {'name': current_transaction_info['ho_ten']})
            if time.time() - recognition_start_time > config.CONFIRMATION_TIMEOUT_S:
                state = "CLEANUP"
            socketio.sleep(1)

        elif state == "FAILURE_LEARNING":
            # ... (Giữ nguyên) ...
            socketio.emit('update_state', {'state': 'failure_learning'})
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            unidentified_folder_path = os.path.join(config.UNIDENTIFIED_PATH, timestamp_str)
            os.makedirs(unidentified_folder_path, exist_ok=True)
            for i in range(config.NUM_UNKNOWN_FACES_TO_SAVE):
                ret, frame = cap.read()
                if ret: cv2.imwrite(os.path.join(unidentified_folder_path, f"face_{i+1}.jpg"), frame)
                socketio.sleep(0.3)
            print(f"[AI]: Da luu anh nguoi la vao thu muc: {unidentified_folder_path}")
            current_transaction_info = {"student_id": "UNKNOWN", "ho_ten": "UNKNOWN", "lop": "UNKNOWN", "unidentified_folder": timestamp_str}
            state = "WEIGHING"

        # --- SỬA ĐỔI TOÀN BỘ LOGIC CÂN ---
        elif state == "WEIGHING":
            if cap: cap.release(); cap = None
            socketio.emit('update_state', {'state': 'weighing'})

            # Lấy cân nặng ban đầu của cả 2 cân
            weight_before_1 = load_cell_1.get_weight()
            weight_before_2 = load_cell_2.get_weight()

            active_bin_index = 0 # Chưa xác định thùng nào hoạt động
            paper_weight = 0.0

            weighing_start_time = time.time()
            while time.time() - weighing_start_time < config.WEIGHING_DURATION_S:
                current_weight_1 = load_cell_1.get_weight()
                current_weight_2 = load_cell_2.get_weight()

                added_weight_1 = current_weight_1 - weight_before_1
                added_weight_2 = current_weight_2 - weight_before_2

                # Xác định thùng đang hoạt động (thùng có giấy được thêm vào)
                if added_weight_1 > added_weight_2 and added_weight_1 > 0.01:
                    active_bin_index = 1
                    paper_weight = added_weight_1
                elif added_weight_2 > added_weight_1 and added_weight_2 > 0.01:
                    active_bin_index = 2
                    paper_weight = added_weight_2
                else: # Nếu không có sự thay đổi hoặc bằng nhau, không có thùng nào hoạt động
                    active_bin_index = 0
                    paper_weight = 0.0

                time_left = config.WEIGHING_DURATION_S - (time.time() - weighing_start_time)

                socketio.emit('update_weight', {
                    'weights': {
                        'bin_1': current_weight_1,
                        'bin_2': current_weight_2
                    },
                    'added_weight': paper_weight,
                    'time_left': int(time_left)
                })
                socketio.sleep(0.5)

            # Sau khi hết thời gian, ghi lại sự kiện nếu có giấy được thêm vào
            if paper_weight > 0.01 and active_bin_index != 0:
                print(f"[LOG]: Da ghi nhan {paper_weight:.3f}kg giay vao thung {active_bin_index}.")
                data_logger.log_recycling_event(
                    student_id=current_transaction_info.get("student_id"),
                    ho_ten=current_transaction_info.get("ho_ten"),
                    lop=current_transaction_info.get("lop"),
                    khoi_luong_kg=paper_weight,
                    unidentified_folder=current_transaction_info.get("unidentified_folder")
                )
            current_transaction_info["khoi_luong_kg"] = paper_weight
            state = "THANK_YOU"

        elif state == "THANK_YOU":
            # ... (Giữ nguyên) ...
            weight = current_transaction_info.get("khoi_luong_kg", 0)
            message = f"Cảm ơn bạn đã tái chế {weight*1000:.0f}g giấy!" if weight > 0.01 else "Cảm ơn bạn đã ghé thăm!"
            socketio.emit('show_thankyou', {'message': message})
            socketio.sleep(5)
            state = "CLEANUP"

        elif state == "CLEANUP":
            # ... (Giữ nguyên) ...
            if cap: cap.release(); cap = None
            state = "IDLE"
            socketio.emit('update_state', {'state': 'idle'})

# --- KHỞI ĐỘNG HỆ THỐNG ---
if __name__ == '__main__':
    listener_thread = threading.Thread(target=key_listener, daemon=True)
    listener_thread.start()
    socketio.start_background_task(background_thread)
    socketio.run(app, host='0.0.0.0', port=5000)