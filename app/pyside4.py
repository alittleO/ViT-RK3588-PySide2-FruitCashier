from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide2.QtGui import QImage, QPixmap, QFont
from PySide2.QtCore import QTimer, Qt
import sys, cv2, serial
import os

# 指定使用软件渲染
os.environ["QT_QUICK_BACKEND"] = "software"

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera App")
        self.setGeometry(100, 100, 1000, 600)
        self.qupi = 0.0  # 初始化去皮重量为0

        # 设置字体
        font = QFont("Arial", 12)  # 创建字体对象，字号为12

        # 设置图片显示标签
        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)

        # 创建按钮
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setMinimumSize(100, 50)
        self.capture_button.setFont(font)

        self.tare_button = QPushButton("去皮", self)
        self.tare_button.clicked.connect(self.perform_tare)
        self.tare_button.setMinimumSize(100, 50)
        self.tare_button.setFont(font)

        # 创建显示标签
        self.dish_info = QLabel("Dish Name: Tomato\nPrice: $2.5 per kg", self)
        self.dish_info.setStyleSheet("background-color: lightgrey; padding: 10px;")
        self.dish_info.setFont(font)

        self.weight_label = QLabel("重量: 0 kg", self)  # 创建重量显示标签
        self.weight_label.setStyleSheet("background-color: lightgrey; padding: 10px;")
        self.weight_label.setFont(font)

        self.price_label = QLabel("总价: $0.00", self)  # 创建价格显示标签
        self.price_label.setStyleSheet("background-color: lightgrey; padding: 10px;")
        self.price_label.setFont(font)

        # 布局设置
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.dish_info)
        right_layout.addWidget(self.weight_label)
        right_layout.addWidget(self.price_label)
        right_layout.addWidget(self.capture_button)
        right_layout.addWidget(self.tare_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 初始化摄像头和定时器
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

        # 初始化串口通信
        self.serial = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        self.serial_timer = QTimer(self)
        self.serial_timer.timeout.connect(self.read_serial_data)
        self.serial_timer.start(100)

    def perform_tare(self):
        if self.serial.inWaiting() > 0:
            line = self.serial.readline().decode('utf-8').strip()
            if line.startswith('weight='):
                weight_str = line.split('=')[1].replace('g', '').strip()
                try:
                    self.qupi = float(weight_str) / 1000
                    self.update_labels(self.qupi)  # 更新标签显示去皮重量
                except ValueError:
                    print("Received non-numeric weight data.")

    def update_labels(self, weight):
        display_weight = max(weight, 0)  # 防止显示负数
        total_price = display_weight * 2.5  # 计算总价
        self.weight_label.setText(f"重量: {display_weight:.3f} kg {display_weight*2:.3f}斤")
        self.price_label.setText(f"总价: ${total_price:.2f}")

    # 其他函数如 update_frame, read_serial_data, capture_image 和 closeEvent 保持不变

    def update_frame(self):  # 更新帧的函数
        ret, frame = self.cap.read()  # 从摄像头读取一帧
        if ret:  # 如果读取成功
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将图像从BGR格式转换为RGB格式
            h, w, ch = rgb_image.shape  # 获取图像的高度、宽度和通道数
            bytes_per_line = ch * w  # 计算每行的字节数
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)  # 将图像转换为Qt的图像格式
            p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)  # 将图像缩放到指定大小
            self.image_label.setPixmap(QPixmap.fromImage(p))  # 将图像显示在标签上

    def read_serial_data(self):  # 读取串口数据的函数
        if self.serial.inWaiting() > 0:  # 如果串口有待读取数据
            line = self.serial.readline().decode('utf-8').strip()  # 读取一行数据，并去除前后空格
            if line.startswith('weight='):  # 如果数据以'weight='开头
                weight_str = line.split('=')[1].replace('g', '').strip()  # 获取重量数据，并去除单位和空格
                try:
                    weight = float(weight_str) / 1000  # 将重量转换为千克
                    if weight < 0:  # 如果重量为负
                        display_weight = 0  # 显示的重量设为0
                    else:
                        display_weight = weight

                    # 根据重量计算总价，不考虑负值
                    total_price = max(weight, 0) * 2.5
                    self.weight_price_info.setText(f"重量: {display_weight:.3f} kg {display_weight*2:.3f}斤\n总价: ${total_price:.2f}")
                except ValueError:
                    print("Received non-numeric weight data.")  # 打印错误信息
                    
    def capture_image(self):  # 捕获图像的函数
        ret, frame = self.cap.read()  # 从摄像头读取一帧
        if ret:  # 如果读取成功
            cv2.imwrite("captured_image.jpg", frame)  # 保存图像
            print("Image captured and saved!")  # 打印提示信息

    def closeEvent(self, event):  # 窗口关闭事件处理函数
        self.cap.release()  # 释放摄像头
        self.serial.close()  # 关闭串口

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())

