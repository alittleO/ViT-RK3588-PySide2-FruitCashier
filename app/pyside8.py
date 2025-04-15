import sys  # 导入系统模块
import cv2  # 导入OpenCV库
import numpy as np
from PySide2.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QTableWidget, QListWidget, QGridLayout, 
                               QFrame, QSizePolicy, QHeaderView, QTableWidgetItem, 
                               QMessageBox)  # 导入PySide2中的多个控件
from PySide2.QtGui import QPixmap, QImage, QFont  # 导入PySide2中的图形相关模块
from PySide2.QtCore import Qt, QThread, Signal,  QTimer  # 导入PySide2的核心模块，包括定时器

from init_rknn import init_rknn  # 从init_rknn文件导入init_rknn函数
from run_rknn import run_rknn  # 从run_rknn文件导入run_rknn函数
from id2label import id2label, id2price

import serial
import threading


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
                # run_rknn返回的是列表
                results = run_rknn(self.rknn_lite, self.image)
                self.result_signal.emit(results)  # 发送结果列表
                self.image = None

    def process_image(self, image):
        self.image = image

    def stop(self):
        self.running = False

class CardWidget(QWidget):  # 定义一个卡片组件类，继承自QWidget
    def __init__(self, name, image_path, price, list_widget):  # 类的初始化函数
        super().__init__()  # 调用父类的初始化函数
        self.name = name  # 初始化名称属性
        #self.list_widget = list_widget  # 初始化列表组件属性
        self.setFixedSize(224, 224)  # 设置卡片的固定大小

        self.layout = QVBoxLayout()  # 使用垂直布局
        self.name_label = QLabel(self.name)  # 创建显示名称的标签
        self.name_label.setAlignment(Qt.AlignCenter)  # 设置标table签的对齐方式为居中

        self.image_label = QLabel()  # 创建显示图片的标签
        self.pixmap = QPixmap(image_path)  # 从图片路径加载图片
        self.image_label.setPixmap(self.pixmap.scaled(240, 180, Qt.KeepAspectRatio))  # 设置图片标签的图片，并保持比例
        self.image_label.setAlignment(Qt.AlignCenter)  # 设置图片标签的对齐方式为居中

        self.price_label = QLabel(f"价格: {price}")  # 创建显示价格的标签
        self.price_label.setAlignment(Qt.AlignCenter)  # 设置价格标签的对齐方式为居中

        self.button = QPushButton("添加到列表")  # 创建一个按钮
        self.button.clicked.connect(self.add_to_list)  # 将按钮的点击信号连接到add_to_list函数
        self.button.setFont(QFont('MiSans', 18))  # 设置按钮的字体

        self.layout.addWidget(self.name_label)  # 向布局中添加名称标签
        self.layout.addWidget(self.image_label)  # 向布局中添加图片标签
        self.layout.addWidget(self.price_label)  # 向布局中添加价格标签
        self.layout.addWidget(self.button)  # 向布局中添加按钮
        self.setLayout(self.layout)  # 设置本组件的布局为之前定义的垂直布局

    def add_to_list(self):  # 定义添加到列表的函数
        self.table.addItem(self.name)  # 在列表组件中添加此卡片的名称
        print(f"添加了：{self.name}")  # 控制台输出信息

class CardBtn(QPushButton):
    def __init__(self, parent, commodity, image_path, price, table):
        super().__init__(commodity, parent)
        self.table = table
        self.parent = parent
        self.commodity = commodity
        self.price = price
        #self.setFixedSize(240, 30)  # 设置卡片的固定大小
        self.setMaximumSize(240, 400)  # 设置卡片的最大尺寸

        # 设置按钮样式
        self.setStyleSheet(
            "QPushButton {"  # 设置按钮的基本样式
            "border: 2px solid #8f8f91;"  # 按钮边框为2px宽，颜色为灰色
            "border-radius: 20px;"  # 按钮边角的圆角半径为20px
            "background-color: #ffffff;"  # 按钮的背景颜色为浅灰色
            "}"
            "QPushButton:pressed {"  # 设置按钮在被按下时的样式
            "background-color: #ADD8E6;"  # 按钮被按下时的背景颜色为浅蓝色
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
        self.label_price.setFont(QFont('MiSans', 18))  # 设置按钮的字体
        self.layout.addWidget(self.label_price)

        current_weight = parent.get_weight()
        self.subtotal = QLabel(f'小计: {round(self.price*current_weight,2)}', self)
        self.subtotal.setAlignment(Qt.AlignCenter)
        self.subtotal.setFont(QFont('MiSans', 18))  # 设置按钮的字体
        self.layout.addWidget(self.subtotal)


        # 将布局应用到按钮上
        self.setLayout(self.layout)

        # 连接按钮点击信号到槽函数
        self.clicked.connect(self.add_to_table)

    def add_to_table(self):
        # 弹出消息框显示按钮文本
        #QMessageBox.information(self.parent, 'Button Name', self.text())
        # 向表格中添加一项（这部分可能需要根据你的实际需要进行调整）
        # 这里的 self.text() 将作为添加到列表的文本
        #self.table.addItem(self.name)  # 修改使用 self.text() 替代 self.name
        #print(f"添加了：{self.commodity}")  # 控制台输出信息

        current_weight = self.parent.get_weight()
        self.parent.add_data(self.table, [self.commodity, str(self.price), str(round(current_weight,3)), 
                                   str(round(self.price*current_weight,2))])
        self.parent.update_totals(self.table)


class VideoWidget(QLabel):  # 定义一个视频显示组件类，继承自QLabel
    def __init__(self, inference_thread):  # 类的初始化函数
        super().__init__()  # 调用父类的初始化函数
        self.inference_thread = inference_thread
        self.setFixedSize(320, 240)  # 设置视频显示组件的固定大小
        self.cap = cv2.VideoCapture(0)  # 初始化摄像头设备，0通常表示默认摄像头
        self.timer = QTimer()  # 创建一个定时器
        self.timer.timeout.connect(self.update_frame)  # 将定时器的超时信号连接到update_frame函数
        self.timer.start(1000)  # 设置定时器的时间间隔为1000毫秒，并启动

    def update_frame(self):  # 定义更新视频帧的函数
        ret, frame = self.cap.read()  # 读取摄像头的一帧
        if ret:  # 如果读取成功
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将帧转换为RGB格式
            h, w, ch = rgb_image.shape  # 获取图像的高度、宽度和通道数
            bytes_per_line = ch * w  # 计算每行的字节数
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)  # 创建QImage对象
            p = convert_to_Qt_format.scaled(self.width(), self.height(), Qt.KeepAspectRatio)  # 调整图像大小以适应组件
            self.setPixmap(QPixmap.fromImage(p))  # 设置标签的显示内容为调整后的图像

            #深度学习# 发送图像到推理线程
            rgb_image = cv2.resize(rgb_image, (224, 224))
            rgb_image = np.expand_dims(rgb_image, 0)
            self.inference_thread.process_image(rgb_image)

    def stop_video(self):  # 定义停止视频播放的函数
        self.timer.stop()  # 停止定时器
        self.cap.release()  # 释放摄像头资源

class MainWindow(QWidget):  # 定义主窗口类，继承自QWidget
    def __init__(self, serial_reader, rknn_lite):  # 类的初始化函数
        super().__init__()  # 调用父类的初始化函数
        #串口进程
        self.serial_reader = serial_reader
        QTimer.singleShot(100, self.serial_reader.perform_tare)  # 延迟后执行去皮
        #npu进程
        self.inference_thread = InferenceThread(rknn_lite)
        self.inference_thread.result_signal.connect(self.update_result)
        self.inference_thread.start()

        self.setWindowTitle("果蔬识别结算系统")  # 设置窗口标题
        self.setStyleSheet("background-color: white;")
        self.showFullScreen()  # 设置窗口全屏显示
        
        #主窗口#################################################################
        main_layout = QHBoxLayout(self)  # 创建水平主布局

        left_layout = QVBoxLayout()  # 创建一个垂直布局用于放置右侧的组件

        #左上部分# 主布局>容器>网络布局
        
        self.card_layout = QGridLayout()  # 创建一个网格布局用于放置卡片
        card_container = QWidget()  # 创建一个容器用于容纳卡片布局
        card_container.setLayout(self.card_layout)  # 将卡片布局设置给容器
        #card_container.setStyleSheet("background-color: blue;")
        left_layout.addWidget(card_container,1)  # 将容器添加到布局中

        #left_layout.addStretch()  # 在布局中添加一个伸setFixedSize缩项目

        #左下部分#
        operation_layout = QHBoxLayout()  # 创建一个水平布局用于放置操作按钮
        operation_container = QWidget()  # 创建一个容器用于容纳操作布局
        operation_container.setLayout(operation_layout)  # 将操作布局设置给容器
        operation_container.setMaximumSize(720, 250)  # 设置最大尺寸

        #左下1
        self.video_widget = VideoWidget(self.inference_thread)  # 创建一个视频显示组件实例
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

        
        self.add_card_button = QPushButton("添加卡片")  # 创建一个添加卡片的按钮
        self.add_card_button.setFont(QFont('MiSans', 18))  # 设置按钮的字体
        self.add_card_button.clicked.connect(self.add_card)  # 将按钮的点击信号连接到add_card函数
        
        opt2_layout.addWidget(self.logo_label, 1)
        opt2_layout.addWidget(self.weight_label,1)
        opt2_layout.addWidget(self.add_card_button, 1)
        opt2_layout.addWidget(self.btn_tare,1)
        
        operation_layout.addLayout(opt2_layout, 1)  # 添加到操作布局中
        # 设置定时器每200ms更新重量数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(200)
        #左下3
        opt3_layout = QVBoxLayout()
        self.btn_add = QPushButton("手动添加商品")
        self.btn_add.setFont(QFont('MiSans', 18))  # 设置按钮的字体
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
        operation_layout.addLayout(opt3_layout, 1)  # 添加到操作布局中


        left_layout.addWidget(operation_container,1)  # 将容器添加到左侧布局中
        main_layout.addLayout(left_layout, 3)  # 将所有左侧布局添加到主布局中
        

        #右侧已购商品
        #self.list_widget = QListWidget()  # 创建一个列表组件
        #self.list_widget.setFixedWidth(150)  # 设置列表组件的固定宽度

        self.table = QTableWidget(0, 4)
        self.table.setFont(QFont('MiSans', 14))
        self.table.setHorizontalHeaderLabels(["商品", "单价", "重量", "小计"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)# 设置为一次选择一行
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 商品列，填充剩余空间
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 单价列，内容调整
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 数量列，内容调整
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 小计列，内容调整
        main_layout.addWidget(self.table, 1)  # 将列表组件添加到主布局中

        self.setLayout(main_layout)  # 设置窗口的布局为主布局

        

    def add_card(self):  # 定义添加卡片的函数#迟早被删
        #self.weight
        name = "新卡片"  
        image_path = "/home/orangepi/Desktop/capture.jpg" 
        price = 5.3  
        new_card = CardBtn(self, name, image_path, price, self.table)  # 创建一个新的卡片组件
        count = self.card_layout.count()  # 获取当前布局中的组件数量
        self.card_layout.addWidget(new_card, 1, count % 3)#(new_card, count // 6, count % 6)  # 将新卡片添加到布局中
        
        for i in range(self.card_layout.count()):
            item = self.card_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, CardBtn):  # 检查是否为CardBtn实例
                size = widget.size()  # 获取按钮的大小
                print(f"按钮大小: 宽度={size.width()} 高度={size.height()}")

    def update_result(self, results):
        #results = [(id2label[label], prob) for label, prob in results]
        result_text = '\n'.join(f"类别{label}: 概率{prob:.2%}" for label, prob in results)
        #print(result_text)
        self.clear_layout(self.card_layout)
        for label, prob in results:
            image_path = "/home/orangepi/Desktop/capture.jpg" 
            new_card = CardBtn(self, id2label[label], image_path, id2price[label], self.table)  # 创建一个新的卡片组件
            count = self.card_layout.count()  # 获取当前布局中的组件数量
            if count < 4:
                self.card_layout.addWidget(new_card, 1, count % 3)
        #self.result_label.setText(f"推理结果: {result_text}")

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
        total = self.calculate_total(table)  # 使用 calculate_total 函数计算总金额
        self.total_label.setText(f"总金额: {round(total,2)}")  # 更新金额总计标签
        self.count_label.setText(f"件数: {table.rowCount()}")  # 更新件数总计标签
    def clear_layout(self, layout):#清空布局
        # 遍历布局中的所有位置
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            # 如果位置上有小部件，将其从布局中移除并删除
            if widget:
                layout.removeWidget(widget)
                widget.deleteLater()

    def update_weight(self):#串口用
        with self.serial_reader.lock:
            self.weight = self.serial_reader.display_weight - self.serial_reader.tare_weight
        self.weight_label.setText(f" 当前重量:\n  {self.weight:.3f} kg")
    def get_weight(self):
        return self.weight
    def resizeEvent(self, event):# 自动图片缩放
        super().resizeEvent(event)
        if hasattr(self, 'logo_label') and self.logo_label:
            self.logo_label.setPixmap(self.logo.scaled(self.logo_label.size(), Qt.KeepAspectRatio))
    def closeEvent(self, event):  # 定义关闭事件的处理函数
        self.video_widget.stop_video()  # 停止视频播放

        self.inference_thread.stop()
        self.inference_thread.wait()

        event.accept()  # 接受关闭事件


if __name__ == "__main__":

    model_path = '/home/orangepi/Desktop/model/vit.rknn'  # 模型文件路径
    rknn_lite = init_rknn(model_path)  # 初始化RKNN模型

    serial_reader = SerialReader('/dev/ttyS0', 9600)  # 替换为你的串口名和波特率
    serial_thread = threading.Thread(target=serial_reader.read_serial_data, daemon=True)
    serial_thread.start()

    app = QApplication(sys.argv)  # 创建一个应用程序实例
    window = MainWindow(serial_reader, rknn_lite)  # 创建一个主窗口实例
    window.show()  # 显示窗口
    sys.exit(app.exec_())  # 启动应用程序的事件循环，并在退出时返回状态
