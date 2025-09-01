# face_recognizer.py
import cv2
import faiss
import pickle
import numpy as np
import pandas as pd
from deepface import DeepFace
import config
import os

class FaceRecognizer:
    def __init__(self):
        """
        Hàm khởi tạo, tải tất cả các model và dữ liệu cần thiết lên.
        """
        print("Dang tai mo hinh AI va co so du lieu...")
        self.index = None
        self.student_ids = []
        self.df_metadata = None
        
        # SỬA LỖI 1: Thêm đầy đủ tên file .xml
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        try:
            self.index = faiss.read_index(os.path.join(config.DATABASE_PATH, "face_index.faiss"))
            with open(os.path.join(config.DATABASE_PATH, "student_ids.pkl"), "rb") as f:
                self.student_ids = pickle.load(f)
            self.df_metadata = pd.read_csv(config.METADATA_FILE)
            self.df_metadata.set_index('student_id', inplace=True)
            print("Tai du lieu AI thanh cong.")
        except Exception as e:
            print(f"!!! LOI: Khong the tai CSDL AI. Hay chay file build_database.py. Chi tiet: {e}")

    def recognize(self, frame):
        """
        Hàm nhận diện chính, chứa logic cốt lõi từ file main_app.py cũ của bạn.
        :param frame: Một khung hình (ảnh) từ camera.
        :return: Một dictionary chứa kết quả và khoảng cách.
        """
        if self.index is None:
            return None

        # Logic phát hiện và cắt ảnh thông minh được chuyển vào đây
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # SỬA LỖI 2: Thêm đầy đủ tham số
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))

        # SỬA LỖI 3: Bỏ 'not' để logic chạy đúng
        if len(faces) > 0:
            # Chỉ xử lý khuôn mặt lớn nhất
            (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
            
            padding_w = int(w * 0.30)
            padding_h = int(h * 0.30)
            x1 = max(0, x - padding_w)
            y1 = max(0, y - padding_h)
            x2 = min(frame.shape[1], x + w + padding_w)
            y2 = min(frame.shape[0], y + h + padding_h)
            
            smart_face_crop = frame[y1:y2, x1:x2]

            try:
                embedding_obj = DeepFace.represent(img_path=smart_face_crop, model_name=config.MODEL_NAME, enforce_detection=False)
                embedding = np.array([embedding_obj[0]['embedding']], dtype='f4')
                faiss.normalize_L2(embedding)
                
                distances, indices = self.index.search(embedding, k=1)
                best_match_distance = distances[0][0]
                
                result_package = {"distance": best_match_distance, "info": None}

                if best_match_distance < config.RECOGNITION_THRESHOLD:
                    best_match_index = indices[0][0]
                    student_id = int(self.student_ids[best_match_index])
                    student_info = self.df_metadata.loc[student_id]
                    
                    result_package["info"] = {
                        "student_id": student_id,
                        "ho_ten": student_info['ho_ten'],
                        "lop": student_info['lop']
                    }
                return result_package
            except Exception as e:
                # print(f"Loi khi xu ly anh da cat: {e}")
                return None
        
        return None # Trả về None nếu không có khuôn mặt nào trong khung hình