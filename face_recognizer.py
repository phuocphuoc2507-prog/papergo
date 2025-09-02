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
        print("Dang tai mo hinh AI va co so du lieu...")
        self.index = None
        self.student_ids = []
        self.df_metadata = None

        try:
            db_path = config.DATABASE_PATH
            self.index = faiss.read_index(os.path.join(db_path, "face_index.faiss"))
            with open(os.path.join(db_path, "student_ids.pkl"), "rb") as f:
                self.student_ids = pickle.load(f)

            # Đảm bảo student_id được đọc là kiểu chuỗi để tra cứu chính xác
            self.df_metadata = pd.read_csv(config.METADATA_FILE, dtype={'student_id': str})
            self.df_metadata.set_index('student_id', inplace=True)
            print("Tai du lieu AI thanh cong.")
        except Exception as e:
            print(f"!!! LOI: Khong the tai CSDL AI. Hay chay file 'build_database.py'. Chi tiet: {e}")

    def recognize(self, frame):
        if self.index is None:
            return None

        try:
            embedding_objs = DeepFace.represent(
                img_path=frame,
                model_name=config.MODEL_NAME,
                detector_backend=config.DETECTOR_BACKEND,
                enforce_detection=False # Không báo lỗi nếu không thấy mặt, chỉ trả về list rỗng
            )
            
            # Nếu không tìm thấy khuôn mặt nào
            if not embedding_objs:
                return None

            # Chỉ xử lý khuôn mặt đầu tiên (lớn nhất) mà DeepFace tìm thấy
            embedding = np.array([embedding_objs[0]['embedding']], dtype='f4')
            faiss.normalize_L2(embedding)
            
            distances, indices = self.index.search(embedding, k=1)
            best_match_distance = distances[0][0]
            
            result_package = {"distance": best_match_distance, "info": None}

            if best_match_distance < config.RECOGNITION_THRESHOLD:
                best_match_index = indices[0][0]
                student_id = self.student_ids[best_match_index]
                student_info = self.df_metadata.loc[student_id]
                
                result_package["info"] = {
                    "student_id": student_id,
                    "ho_ten": student_info['ho_ten'],
                    "lop": student_info['lop']
                }
            return result_package
            
        except KeyError as e:
            print(f"!!! LOI TIM KIEM: Khong tim thay student_id '{e}' trong file metadata.csv.")
            return None
        except Exception:
            # Bỏ qua các lỗi tiềm tàng khác của DeepFace để chương trình không bị treo
            return None