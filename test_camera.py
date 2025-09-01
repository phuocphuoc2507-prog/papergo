# test_camera.py
import cv2

# Số 0 là webcam mặc định. Nếu bạn cắm camera ngoài, hãy thử đổi thành 1 hoặc 2.
CAMERA_INDEX = 0 
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print(f"Loi: Khong the mo camera o vi tri so {CAMERA_INDEX}.")
    exit()

print("Da mo camera thanh cong! Nhan phim 'q' de thoat.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Loi: Khong the doc hinh anh tu camera.")
        break

    cv2.imshow("Kiem tra Camera - Nhan 'q' de thoat", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()