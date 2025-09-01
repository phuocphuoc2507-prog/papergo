import os
import numpy as np
import faiss
from deepface import DeepFace
import pickle
import time
import config # SỬ DỤNG FILE CONFIG TRUNG TÂM

def build():
    """
    Hàm chính để xây dựng cơ sở dữ liệu khuôn mặt.
    Đọc ảnh từ config.DATASET_PATH và lưu kết quả vào config.DATABASE_PATH.
    """
    print("Bat dau qua trinh xay dung co so du lieu khuon mat...")
    start_time = time.time()

    face_embeddings = []
    student_ids = []

    # Đảm bảo các thư mục tồn tại
    os.makedirs(config.DATABASE_PATH, exist_ok=True)
    if not os.path.isdir(config.DATASET_PATH):
        print(f"!!! LOI: Thu muc dataset '{config.DATASET_PATH}' khong ton tai.")
        return

    # Lấy danh sách các thư mục học sinh hợp lệ và sắp xếp
    valid_student_folders = [f for f in os.listdir(config.DATASET_PATH) if os.path.isdir(os.path.join(config.DATASET_PATH, f))]
    valid_student_folders.sort()
    total_students = len(valid_student_folders)

    if total_students == 0:
        print("!!! Canh bao: Khong tim thay thu muc hoc sinh nao trong dataset.")
        return

    print(f"Tim thay {total_students} hoc sinh trong dataset.")

    for i, student_id_folder in enumerate(valid_student_folders):
        folder_path = os.path.join(config.DATASET_PATH, student_id_folder)
        try:
            # Lấy tất cả các file ảnh trong thư mục của học sinh
            image_files = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not image_files:
                print(f"Canh bao: Thu muc {student_id_folder} khong co file anh nao.")
                continue

            # Xử lý tất cả các ảnh tìm thấy
            for image_name in image_files:
                image_path = os.path.join(folder_path, image_name)
                # Dùng DeepFace để trích xuất vector đặc trưng
                embedding_obj = DeepFace.represent(img_path=image_path, model_name=config.MODEL_NAME, enforce_detection=False)
                face_embeddings.append(embedding_obj[0]['embedding'])
                student_ids.append(student_id_folder)
            
            print(f"[{i+1}/{total_students}] Da xu ly: {student_id_folder} ({len(image_files)} anh)")

        except Exception as e:
            print(f"Loi khi xu ly thu muc {student_id_folder}: {e}")

    if not face_embeddings:
        print("!!! LOI: Khong xu ly duoc bat ky anh nao. Ket thuc.")
        return

    face_embeddings_np = np.array(face_embeddings, dtype='f4')
    # Chuẩn hóa L2 cho tất cả các vector
    faiss.normalize_L2(face_embeddings_np)

    # Lấy kích thước vector từ dữ liệu thực tế
    embedding_dimension = face_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(embedding_dimension)
    index.add(face_embeddings_np)

    print(f"\nDa xay dung xong chi muc FAISS voi {index.ntotal} vector da duoc chuan hoa.")

    # Lưu chỉ mục và danh sách ID
    faiss.write_index(index, os.path.join(config.DATABASE_PATH, "face_index.faiss"))
    with open(os.path.join(config.DATABASE_PATH, "student_ids.pkl"), "wb") as f:
        pickle.dump(student_ids, f)

    end_time = time.time()
    print(f"Hoan tat! Qua trinh mat {end_time - start_time:.2f} giay.")

# Đoạn này đảm bảo hàm build() sẽ được chạy khi bạn thực thi "python build_database.py"
if __name__ == "__main__":
    build()