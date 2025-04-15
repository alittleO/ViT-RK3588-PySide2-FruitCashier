import sys
import cv2
import threading
import time
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QGridLayout
from PySide2.QtGui import QPixmap, QImage, QFont
from PySide2.QtCore import Qt, QTimer
from init_rknn import init_rknn
from run_rknn import run_rknn

class CardWidget(QWidget):
    def __init__(self, name, image_path, list_widget):
        super().__init__()
        self.name = name
        self.list_widget = list_widget
        self.setFixedSize(224, 224)

        self.layout = QVBoxLayout()
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.pixmap = QPixmap(image_path)
        self.image_label.setPixmap(self.pixmap.scaled(140, 100, Qt.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignCenter)

        self.prob_label = QLabel("概率: 0.000000")
        self.prob_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.prob_label)
        self.setLayout(self.layout)

    def update_content(self, name, prob):
        self.name_label.setText(name)
        self.prob_label.setText(f"概率: {prob:.6f}")

class MainWindow(QWidget):
    def __init__(self, rknn_lite):
        super().__init__()
        self.rknn_lite = rknn_lite
        self.setWindowTitle("识别结果显示")
        self.setGeometry(100, 100, 800, 600)

        self.card_widget = CardWidget("等待推理结果...", "/home/orangepi/Desktop/temp.jpg", self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.card_widget)
        self.setLayout(self.layout)

        self.thread = threading.Thread(target=self.capture_and_infer)
        self.thread.start()

    def capture_and_infer(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imwrite('/home/orangepi/Desktop/temp.jpg', frame)
                results = run_rknn(self.rknn_lite, '/home/orangepi/Desktop/temp.jpg')
                if results:
                    self.update_gui(results[0])
            time.sleep(1)
        cap.release()

    def update_gui(self, result):
        name, prob = result
        self.card_widget.update_content(f"商品{name}", prob)

    def closeEvent(self, event):
        self.thread.join()
        event.accept()

if __name__ == "__main__":
    model_path = '/home/orangepi/Desktop/model/vit.rknn'
    rknn_lite = init_rknn(model_path)

    app = QApplication(sys.argv)
    window = MainWindow(rknn_lite)
    window.show()
    sys.exit(app.exec_())
