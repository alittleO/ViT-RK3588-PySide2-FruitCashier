import sys
import cv2
from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide2.QtGui import QImage, QPixmap

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera App")
        self.setGeometry(100, 100, 1000, 600)

        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)

        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)

        # 菜品信息标签
        self.dish_info = QLabel("Dish Name: Tomato\nPrice: $2.5 per kg", self)
        self.dish_info.setStyleSheet("background-color: lightgrey; padding: 10px;")

        # 重量和总价标签
        self.weight_price_info = QLabel("Weight: 0.5 kg\nTotal Price: $1.25", self)
        self.weight_price_info.setStyleSheet("background-color: lightgrey; padding: 10px;")

        # 垂直布局容器
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.dish_info)
        right_layout.addStretch()
        right_layout.addWidget(self.weight_price_info)
        right_layout.addWidget(self.capture_button)

        # 主布局容器
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.cap = cv2.VideoCapture(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(p))

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite("captured_image.jpg", frame)
            print("Image captured and saved!")

    def closeEvent(self, event):
        self.cap.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())

