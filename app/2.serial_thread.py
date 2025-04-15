import sys
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PySide2.QtCore import QTimer
import serial
import threading

class SerialReader:
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.1)
        self.display_weight = 0  # 初始化显示重量为0
        self.tare_weight = 0  # 初始化去皮重量为0
        self.lock = threading.Lock()  # 用于线程同步的锁

    def read_serial_data(self):
        while True:
            if self.serial.inWaiting() > 0:
                line = self.serial.readline().decode('utf-8').strip()
                print(line)
                if line.startswith('weight='):
                    weight_str = line.split('=')[1].replace('g', '').strip()
                    try:
                        weight = float(weight_str) / 1000
                        with self.lock:
                            self.display_weight = weight
                    except ValueError:
                        print("Received non-numeric weight data.")
            # 线程休眠200ms
            threading.Event().wait(0.2)

    def perform_tare(self):
        with self.lock:
            self.tare_weight = self.display_weight

class App(QWidget):
    def __init__(self, serial_reader):
        super().__init__()
        self.serial_reader = serial_reader
        self.initUI()

        # 在程序启动时设置去皮，使用定时器延迟执行
        QTimer.singleShot(1000, self.serial_reader.perform_tare)  # 延迟1秒后执行去皮

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.weight_label = QLabel("等待数据...", self)
        self.tare_button = QPushButton('去皮', self)
        self.tare_button.clicked.connect(self.serial_reader.perform_tare)

        self.layout.addWidget(self.weight_label)
        self.layout.addWidget(self.tare_button)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Serial Weight Reader')

        # 设置定时器每200ms更新界面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(200)

    def update_weight(self):
        with self.serial_reader.lock:
            weight = self.serial_reader.display_weight - self.serial_reader.tare_weight
        self.weight_label.setText(f"当前重量: {weight:.3f} kg")

if __name__ == "__main__":
    
    serial_reader = SerialReader('/dev/ttyS0', 9600)  # 替换为你的串口名和波特率
    serial_thread = threading.Thread(target=serial_reader.read_serial_data, daemon=True)
    serial_thread.start()
    
    app = QApplication(sys.argv)
    ex = App(serial_reader)
    ex.show()
    sys.exit(app.exec_())
