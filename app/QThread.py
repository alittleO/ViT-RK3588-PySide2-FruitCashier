import cv2
import numpy as np
from PySide2.QtCore import Qt, QThread, Signal, QTimer
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

# 导入初始化和推理函数
from init_rknn import init_rknn
from run_rknn import run_rknn
from id2label import id2label

class InferenceThread(QThread):
    result_signal = Signal(list)  # 修改信号类型，使其可以传递列表

    def __init__(self, rknn_lite):
        super().__init__()
        self.rknn_lite = rknn_lite
        self.image = None
        self.running = True

    def run(self):
        while self.running:
            if self.image is not None:
                # 假设run_rknn返回的是列表
                results = run_rknn(self.rknn_lite, self.image)
                self.result_signal.emit(results)  # 发送结果列表
                self.image = None

    def process_image(self, image):
        self.image = image

    def stop(self):
        self.running = False

class MainWidget(QWidget):
    def __init__(self, rknn_lite):
        super().__init__()
        self.setWindowTitle("实时图像和推理结果")
        self.showFullScreen()  # 设置窗口全屏显示
        self.image_label = QLabel("等待图像...")
        self.result_label = QLabel("等待推理结果...")
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

        self.inference_thread = InferenceThread(rknn_lite)
        self.inference_thread.result_signal.connect(self.update_result_label)
        self.inference_thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_image)
        self.timer.start(1000)  # 每1000毫秒触发一次

        # 设置摄像头
        self.cap = cv2.VideoCapture(0)

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            # 显示摄像头图像
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(p))

            # 发送图像到推理线程
            rgb_image = cv2.resize(rgb_image, (224, 224))
            rgb_image = np.expand_dims(rgb_image, 0)
            self.inference_thread.process_image(rgb_image)

    def update_result_label(self, results):
        #self.result_label.setText(text)
        results = [(id2label[label], prob) for label, prob in results]
        result_text = ', '.join(f"类别{label}: 概率{prob:.2%}" for label, prob in results)
        self.result_label.setText(f"推理结果: {result_text}")

    def closeEvent(self, event):
        self.inference_thread.stop()
        self.inference_thread.wait()
        self.cap.release()
        super().closeEvent(event)

# 初始化RKNN模型
model_path = '/home/orangepi/Desktop/model/vit.rknn'
rknn_lite = init_rknn(model_path)

app = QApplication([])
window = MainWidget(rknn_lite)
window.show()
app.exec_()
