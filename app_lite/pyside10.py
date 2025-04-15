import sys  # 导入系统模块
import cv2  # 导入OpenCV库
import numpy as np
from PySide2.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QTableWidget, QListWidget, QGridLayout, 
                               QFrame, QSizePolicy, QHeaderView, QTableWidgetItem, 
                               QMessageBox)  
from PySide2.QtGui import QPixmap, QImage, QFont  
from PySide2.QtCore import Qt, QThread, Signal,  QTimer  

from init_rknn import init_rknn  
from run_rknn import run_rknn 
from id2label import id2label, id2price, enlabels

import serial
import threading
from multiprocessing import Process, Queue

class SerialReader:
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.1)
        self.display_weight = 0  # 初始化显示重量为0
        self.tare_weight = 0  # 初始化去皮重量为0
        self.lock = threading.Lock()  # 用于线程同步的锁

    def read_serial_data(self):
        i = 0
        while True:
            try:
                if self.serial.inWaiting() > 0:
                    line = self.serial.readline().decode('utf-8').strip()
                    print(i, line)
                    i += 1
                    if line.startswith('weight='):
                        weight_str = line.split('=')[1].replace('g', '').strip()
                        try:
                            weight = float(weight_str) / 1000
                            with self.lock:
                                self.display_weight = weight
                        except ValueError:
                            print("Received non-numeric weight data.")
            except Exception as e:
                print(f"Uart error occurred: {e}")
            # 线程休眠200ms
            threading.Event().wait(0.2)

    def perform_tare(self):
        with self.lock:
            self.tare_weight = self.display_weight

class InferenceProcess(Process):
    def __init__(self, result_queue):
        super().__init__()
        self.image_queue = Queue()
        self.result_queue = result_queue
        self.running = True
        

    def run(self):
        try:
            print("Inference process has started.")
            model_path = '/home/orangepi/Desktop/model/vit.rknn'
            rknn_lite = init_rknn(model_path)  
            while self.running:
                if not self.image_queue.empty():
                    image = self.image_queue.get()
                    if image is None:
                        self.running = False
                        print("Inference process received stop signal.")
                    else:
                        print(f"Processing image: {image.shape}")
                        #results = run_rknn(self.rknn_lite, self.img)
                        outputs = rknn_lite.inference(inputs=[image])
                        logits = outputs[0]
                        probabilities = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)

                        # 筛选高概率结果
                        high_prob_results = [(str(i), prob) for i, prob in enumerate(probabilities[0]) if prob > 0.15]

                        # 如果没有高概率结果，返回概率最大的结果
                        if not high_prob_results:
                            max_prob_index = np.argmax(probabilities[0])
                            max_prob_value = probabilities[0][max_prob_index]
                            print(f"没有识别到概率大于0.4的结果，返回概率最大的结果: 类别 {max_prob_index}, 概率 {max_prob_value}")
                            if max_prob_value > 0.15:
                                results =  [(str(max_prob_index), max_prob_value)]
                            else:
                                results = []
                        results = high_prob_results
                        print(results)
                        self.result_queue.put(results)
                #else:
                    #print("Image queue is empty.")
        except Exception as e:
            print(f"Exception in inference process: {e}")

    def process_image(self, image):
        print(f"Putting image in the queue: {image.shape}")
        self.image_queue.put(image)

    def stop(self):
        print("Sending stop signal to inference process.")
        self.process_image(None)  # Send stop signal using None



class CardBtn(QPushButton):
    def __init__(self, parent, commodity, image_path, price, table):
        super().__init__(commodity, parent)
        self.table = table
        self.parent = parent
        self.commodity = commodity
        self.price = price
        self.setFixedSize(240, 30)  # 设置卡片的固定大小
        self.setMaximumSize(240, 400)  # 设置卡片的最大尺寸

        # 设置按钮样式
        self.setStyleSheet(
            "QPushButton {"  
            "border: 2px solid #8f8f91;"  
            "border-radius: 20px;"  
            "background-color: #ffffff;" 
            "}"
            "QPushButton:pressed {"  
            "background-color: #ADD8E6;"  
            "}"
        )

        # 创建并设置垂直布局
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        # 添加并设置标签显示商品名称
        self.label_name = QLabel(commodity, self)
        self.label_name.setAlignment(Qt.AlignCenter)
        self.label_name.setFont(QFont('MiSans', 18))  # 设置按钮的字体
        self.layout.addWidget(self.label_name)

        # 添加并设置标签显示商品图片
        self.label_image = QLabel(self)
        self.pixmap = QPixmap(image_path)
        self.label_image.setPixmap(self.pixmap.scaled(240, 180, Qt.KeepAspectRatio))
        self.label_image.setMinimumSize(200, 150)
        self.layout.addWidget(self.label_image)

        # 添加并设置标签显示价格
        self.label_price = QLabel(f'单价: {price}￥/kg', self)
        self.label_price.setAlignment(Qt.AlignCenter)
        self.label_price.setFont(QFont('MiSans', 18)) 
        self.layout.addWidget(self.label_price)

        current_weight = parent.get_weight()
        self.subtotal = QLabel(f'小计: {round(self.price*current_weight,2)}', self)
        self.subtotal.setAlignment(Qt.AlignCenter)
        self.subtotal.setFont(QFont('MiSans', 18))
        self.layout.addWidget(self.subtotal)

        self.setLayout(self.layout)

        self.clicked.connect(self.add_to_table)

    def add_to_table(self):

        current_weight = self.parent.get_weight()
        self.parent.add_data(self.table, [self.commodity, str(self.price), str(round(current_weight,3)), 
                                   str(round(self.price*current_weight,2))])
        self.parent.update_totals(self.table)


class VideoWidget(QLabel): 
    def __init__(self, inference_process): 
        super().__init__() 
        self.inference_process = inference_process
        self.setFixedSize(320, 240)  
        self.cap = cv2.VideoCapture(0) 
        self.timer = QTimer() 
        self.timer.timeout.connect(self.update_frame)  
        self.timer.start(1000)  

    def update_frame(self): 
        ret, frame = self.cap.read()  
        if ret:  
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
            h, w, ch = rgb_image.shape  # 获取图像的高度、宽度和通道数
            bytes_per_line = ch * w  # 计算每行的字节数
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)  #
            p = convert_to_Qt_format.scaled(self.width(), self.height(), Qt.KeepAspectRatio)  # 调整图像大小以适应组件
            self.setPixmap(QPixmap.fromImage(p))  # 设置标签的显示内容为调整后的图像

            #深度学习# 发送图像到推理线程
            rgb_image = cv2.resize(rgb_image, (224, 224))
            rgb_image = np.expand_dims(rgb_image, 0)
            self.inference_process.process_image(rgb_image)

    def stop_video(self): 
        self.timer.stop()
        self.cap.release() 

class MainWindow(QWidget): 
    def __init__(self, serial_reader, inference_process, result_queue):  
        super().__init__() 
        #串口进程
        self.serial_reader = serial_reader
        QTimer.singleShot(100, self.serial_reader.perform_tare)  # 延迟后执行去皮
        #npu进程
        self.inference_process = inference_process
        self.result_queue = result_queue

        self.setWindowTitle("果蔬识别结算系统")
        self.setStyleSheet("background-color: white;")
        self.showFullScreen()  
        
        #主窗口#
        main_layout = QHBoxLayout(self)  

        left_layout = QVBoxLayout()  

        #左上部分# 主布局>容器>网络布局
        
        self.card_layout = QGridLayout()  
        card_container = QWidget() 
        card_container.setLayout(self.card_layout) 
        left_layout.addWidget(card_container,1)  

        #left_layout.addStretch()  # 在布局中添加一个伸setFixedSize缩项目

        #左下部分#
        operation_layout = QHBoxLayout() 
        operation_container = QWidget()
        operation_container.setLayout(operation_layout)  
        operation_container.setMaximumSize(720, 250) 

        #左下1
        self.video_widget = VideoWidget(self.inference_process)  # 创建一个视频显示组件实例
        operation_layout.addWidget(self.video_widget, 1)
        #左下2
        opt2_layout = QVBoxLayout()
        self.logo_label = QLabel()
        self.logo = QPixmap('/home/orangepi/Desktop/app/logo2.png')
        self.logo_label.setPixmap(self.logo.scaled(100,100, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.weight_label = QLabel("无重量数据", self)
        self.weight_label.setFont(QFont('MiSans', 24))
        self.btn_tare = QPushButton('去皮', self)
        self.btn_tare.setFont(QFont('MiSans', 24))
        self.btn_tare.clicked.connect(self.serial_reader.perform_tare)

        ''''''
        self.add_card_button = QPushButton("添加卡片") 
        self.add_card_button.setFont(QFont('MiSans', 18)) 
        #self.add_card_button.clicked.connect(self.add_card)  
        self.add_card_button.clicked.connect(self.close)
        
        opt2_layout.addWidget(self.logo_label, 1)
        opt2_layout.addWidget(self.weight_label,1)
        opt2_layout.addWidget(self.add_card_button, 1)
        opt2_layout.addWidget(self.btn_tare,1)
        
        operation_layout.addLayout(opt2_layout, 1)
        # 设置定时器每200ms更新重量数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(200)
        #左下3
        opt3_layout = QVBoxLayout()
        self.btn_add = QPushButton("手动添加商品")
        self.btn_add.setFont(QFont('MiSans', 18)) 
        self.btn_add.clicked.connect(lambda: self.add_data(self.table, ["橙子", "4.00", "20", "80.00"]))
        
        self.count_label = QLabel("件数: 0")
        self.count_label.setFont(QFont('MiSans', 18))
        self.total_label = QLabel("总计: 0.00")
        self.total_label.setFont(QFont('MiSans', 18))

        self.btn_remove = QPushButton("删除")
        self.btn_remove.setFont(QFont('MiSans', 18))
        self.btn_remove.clicked.connect(lambda: self.remove_last_item(self.table))

        self.btn_total = QPushButton("结算")
        self.btn_total.setFont(QFont('MiSans', 24))
        self.btn_total.clicked.connect(lambda: self.settle_accounts(self.table))

        opt3_layout.addWidget(self.btn_add, 2)
        opt3_layout.addWidget(self.count_label, 1)
        opt3_layout.addWidget(self.total_label, 1)
        opt3_layout.addWidget(self.btn_remove, 2)
        opt3_layout.addWidget(self.btn_total, 2)
        operation_layout.addLayout(opt3_layout, 1) 


        left_layout.addWidget(operation_container,1)  
        main_layout.addLayout(left_layout, 3)  
        

        self.table = QTableWidget(0, 4)
        self.table.setFont(QFont('MiSans', 14))
        self.table.setHorizontalHeaderLabels(["商品", "单价", "重量", "小计"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)# 设置为一次选择一行
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table, 1) 

        self.setLayout(main_layout) 

        

    def add_card(self):  # 定义添加卡片的函数#迟早被删
        #self.weight
        name = "新卡片"  
        image_path = "/home/orangepi/Desktop/capture.jpg" 
        price = 5.3  
        new_card = CardBtn(self, name, image_path, price, self.table)  # 创建一个新的卡片组件
        count = self.card_layout.count()  # 获取当前布局中的组件数量
        self.card_layout.addWidget(new_card, 1, count % 3) # 将新卡片添加到布局中
        

    def update_result(self):
        if not self.result_queue.empty():
            results = self.result_queue.get()
            self.clear_layout(self.card_layout)
            for label, prob in results:
                image_path = "/home/orangepi/Desktop/app/test/"+enlabels[label]+"/Image_1.jpg" 
                new_card = CardBtn(self, id2label[label], image_path, id2price[label], self.table) 
                count = self.card_layout.count() 
                if count < 4:
                    self.card_layout.addWidget(new_card, 1, count % 3)

    def add_data(self, table, data):
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        for column_index, item in enumerate(data):
            table.setItem(row_index, column_index, QTableWidgetItem(str(item)))
        self.update_totals(table)
    def remove_last_item(self, table):
        if table.rowCount() > 0:
            table.removeRow(table.rowCount() - 1)
        self.update_totals(table)
    def settle_accounts(self, table):
        #还得加收款的弹窗
        table.setRowCount(0) # 清空列表
        self.update_totals(table)
    def calculate_total(self, table):
        total = 0
        for row in range(table.rowCount()):
            total += float(table.item(row, 3).text())
        return total
    def update_totals(self, table):
        total = self.calculate_total(table) 
        self.total_label.setText(f"总金额: {round(total,2)}")
        self.count_label.setText(f"件数: {table.rowCount()}") 
    def clear_layout(self, layout):#清空布局
        # 遍历布局中的所有位置
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            # 如果位置上有小部件，将其从布局中移除并删除
            if widget:
                layout.removeWidget(widget)
                widget.deleteLater()

    def update_weight(self): # 串口用
        with self.serial_reader.lock:
            self.weight = self.serial_reader.display_weight - self.serial_reader.tare_weight
        self.weight_label.setText(f" 当前重量:\n  {self.weight:.3f} kg")
        self.update_result()
    def get_weight(self):
        return self.weight
    def resizeEvent(self, event): # 自动图片缩放
        super().resizeEvent(event)
        if hasattr(self, 'logo_label') and self.logo_label:
            self.logo_label.setPixmap(self.logo.scaled(self.logo_label.size(), Qt.KeepAspectRatio))
    def closeEvent(self, event):
        self.video_widget.stop_video()

        self.inference_process.stop()
        self.inference_process.join()
        
        
        self.serial_reader.join()
        event.accept() 


if __name__ == "__main__":

    

    result_queue = Queue()
    inference_process = InferenceProcess(result_queue)
    inference_process.start()
    
    serial_reader = SerialReader('/dev/ttyS0', 9600)  
    serial_thread = threading.Thread(target=serial_reader.read_serial_data, daemon=True)
    serial_thread.start()

    app = QApplication(sys.argv)  
    window = MainWindow(serial_reader, inference_process, result_queue)  
    window.show() 
    sys.exit(app.exec_()) 
